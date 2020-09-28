#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import commands
import datetime

from conectar import *
from relatorio import extrato
from retaguarda import adiciona

from wx.lib.buttons import GenBitmapTextButton,GenBitmapButton

sb      = sbarra()
mens    = menssagem()
alertas = dialogos()
acs     = acesso()
nF      = numeracao()

class DavConsultar(wx.Frame):

	clientes = {}
	registro = 0
	
	def __init__(self, parent,id):

		self.impres = parent.impre
		self.myfram = parent
		self.p      = parent
		self.t      = truncagem()
		mkn = wx.lib.masked.NumCtrl

		self.numera = parent.numer
		self.logins = parent.usuem
		self.extcli = extrato()
		
		self.fundcr = '#D7D78A'
		self.lreceb = '#4D4D4D'
		self.filial = '#C7C7ED'
		
		self.csFilial = self.p.fildavs
		self.p.Disable()
		self.p.data_emissao_devolucao = ""
		self.p.consolida_emissao_nota_fiscal=False

		wx.Frame.__init__(self, parent, id, u'DAVs: pedidos, orçamentos - consulta e reimpressão', size=(800,678), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,id,style=wx.BORDER_SUNKEN)

		self.ListaDavs = DVListCtrl(self.painel, 300, pos=(12,10), size=(784,224),
								style=wx.LC_REPORT
								|wx.LC_VIRTUAL
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)
								
		cabe = wx.StaticText(self.painel,-1,"DAVs,Orçamentos [ Consulta e Reimpressão ]",pos=(0,0))
		cabe.SetForegroundColour('#6D98C3')
		cabe.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.ListaDavs.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.impresDav)
		self.ListaDavs.Bind(wx.EVT_RIGHT_DOWN, self.marcar_desmarcar_davs)
		self.Bind(wx.EVT_CLOSE, self.voltar)
		self.ListaDavs.SetBackgroundColour('#EFF4FA')

		""" Pedidos relacionados """
		self.relacionar_pedidos = wx.ListCtrl(self.painel, -1, pos=(0,530), size=(703,140),
										style=wx.LC_REPORT
										|wx.BORDER_SUNKEN
										|wx.LC_HRULES
										|wx.LC_VRULES
										|wx.LC_SINGLE_SEL
										)
		self.relacionar_pedidos.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.relacionar_pedidos.SetBackgroundColour('#75A9DB')
		self.relacionar_pedidos.SetForegroundColour('#000000')

		self.relacionar_pedidos.InsertColumn(0,u'Ordem', format=wx.LIST_ALIGN_LEFT,width=60)
		self.relacionar_pedidos.InsertColumn(1,u'Numero pedido', format=wx.LIST_ALIGN_LEFT,width=120)
		self.relacionar_pedidos.InsertColumn(2,u'Cliente    { Agrupar davs para emissão de nf consolidada }', width=410)
		self.relacionar_pedidos.InsertColumn(3,u'CPF/CNPJ', width=110)
		self.relacionar_pedidos.InsertColumn(4,u'Dados envio', width=1000)
		self.relacionar_pedidos.InsertColumn(5,u'SubTotal', format=wx.LIST_ALIGN_LEFT,width=120)
		"""-----------------------------------[ Pedidos relacionados ] """
		
		if len(login.usaparam.split(";"))>=43 and login.usaparam.split(";")[42]=="T":

		    wx.StaticText(self.painel,-1,"Pesquisa apenas pelo numero do DAV { Bloqueio }",pos=(17,392)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		else:
		    wx.StaticText(self.painel,-1,"Descrição do Cliente, Nº DAV, V:Vendedor P:Expressão",pos=(17,392)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		    
		wx.StaticText(self.painel,-1,"SubToTal",    pos=(415,315)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Frete",       pos=(415,350)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Acréscimo",   pos=(500,315)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Tributos",    pos=(500,350)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Desconto",    pos=(585,315)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"ToTal DAV",   pos=(585,350)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"RECEBIMENTO", pos=(665,315)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"ENTREGA:",    pos=(665,360)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Relação de Filias Remotas/Parceiros", pos=(15,235)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Descrição da Filial/Parceiro", pos=(407,235)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"{%}>-->Redução", pos=(310,434)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Devolução-desconto", pos=(213,434)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"NofaFiscal", pos=(338,394)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		informp = wx.StaticText(self.painel,-1,"Informações do controle de projetos", pos=(500,430))
		informp.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		informp.SetForegroundColour("#8A8A8A")

		informe = wx.StaticText(self.painel,-1,"{ Consultar }", pos=(732,478))
		informe.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		informe.SetForegroundColour("#8A8A8A")

		self.rcusa = wx.StaticText(self.painel,-1,pos=(665,325))
		self.endat = wx.StaticText(self.painel,-1,pos=(665,372))
		self.filvd = wx.StaticText(self.painel,-1,pos=(407,407))		
		self.vincu = wx.StaticText(self.painel,-1,"", pos=(233,235))
		
		self.rcusa.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.endat.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.filvd.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vincu.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.rcusa.SetForegroundColour(self.lreceb)
		self.endat.SetForegroundColour(self.lreceb)
		self.filvd.SetForegroundColour('#4D4D4D')
		self.vincu.SetForegroundColour('#A52A2A')

		self.ocorr = wx.StaticText(self.painel,-1,pos=(285,365))
		self.ocorr.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ocorr.SetForegroundColour("#1E90FF")

		self.Tipos = wx.StaticText(self.painel,-1,'Tipo: {}',pos=(407,280))
		self.Tipos.SetFont(wx.Font(11,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tipos.SetForegroundColour("#1E90FF")

		self.enTre= wx.StaticText(self.painel,-1,'',pos=(413,382))
		self.enTre.SetFont(wx.Font(8.5,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.enTre.SetForegroundColour("#A91414")

		self.prazo = wx.StaticText(self.painel,-1,'',pos=(413,385))
		self.prazo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.prazo.SetForegroundColour("#E64A4A")

		self.modo = wx.StaticText(self.painel,-1,"Modo: DAVs", pos=(698,402))
		self.modo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.modo.SetForegroundColour("#A1A114")
	    
		periodo = wx.StaticText(self.painel,-1,"Período",pos=(125,297))
		periodo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Alteração manual do frete: ",pos=(310,506)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.copiaDav = wx.ComboBox(self.painel, -1, '',  pos=(12, 247), size=(389,27), choices = login.ciaRemot,style=wx.NO_BORDER|wx.CB_READONLY)
		self.dcFilial = wx.TextCtrl(self.painel,-1,'',    pos=(405,250), size=(392,24), style=wx.TE_READONLY)
		self.dcFilial.SetBackgroundColour("#E5E5E5")
		self.dcFilial.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.DvVoltar = wx.BitmapButton(self.painel, 221, wx.Bitmap("imagens/voltam.png",  wx.BITMAP_TYPE_ANY), pos=(282,300), size=(34,34))				
		self.Procurar = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/procurap.png",wx.BITMAP_TYPE_ANY), pos=(323,300), size=(34,34))				
		self.Printar  = wx.BitmapButton(self.painel, 223, wx.Bitmap("imagens/printp.png",  wx.BITMAP_TYPE_ANY), pos=(361,300), size=(34,34))

		self.extratp = wx.BitmapButton(self.painel, 224, wx.Bitmap("imagens/cccl.png",     wx.BITMAP_TYPE_ANY), pos=(250,300), size=(28,28))				
		self.importa = wx.BitmapButton(self.painel, 225, wx.Bitmap("imagens/import16.png", wx.BITMAP_TYPE_ANY), pos=(250,330), size=(28,28))				
		self.davrefe = wx.BitmapButton(self.painel, 226, wx.Bitmap("imagens/edit.png",     wx.BITMAP_TYPE_ANY), pos=(250,360), size=(28,28))				
		self.consrem = wx.BitmapButton(self.painel, 226, wx.Bitmap("imagens/cliente16.png", wx.BITMAP_TYPE_ANY), pos=(765,340), size=(28,28))				
		self.consulta_cliente_varios = wx.BitmapButton(self.painel, 227, wx.Bitmap("imagens/referencia16.png",  wx.BITMAP_TYPE_ANY), pos=(370,360), size=(26,24))

		""" Botoes para agregar davs """
		self.incluir_todos = GenBitmapTextButton(self.painel,333,label=u'Incluir\nTods do cliente\nSelecionado',  pos=(705,551),size=(93,50), bitmap=wx.Bitmap("imagens/agrupar16.png", wx.BITMAP_TYPE_ANY))
		self.incluir_todos.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.incluir_todos.SetBackgroundColour('#C2DBF4')

		self.apagar_selecionado = GenBitmapTextButton(self.painel,334,label=u'Apagar\nDav\nSelecionado',  pos=(705,603),size=(93,37), bitmap=wx.Bitmap("imagens/cancela16.png", wx.BITMAP_TYPE_ANY))
		self.apagar_selecionado.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.apagar_selecionado.SetBackgroundColour('#9BC7F2')

		self.limpar_lista = GenBitmapTextButton(self.painel,335,label=u'Apagar\nToda a Lista',  pos=(705,643),size=(93,28), bitmap=wx.Bitmap("imagens/delete.png", wx.BITMAP_TYPE_ANY))
		self.limpar_lista.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.limpar_lista.SetBackgroundColour('#7CAFE0')

		self.valor_total_selecionados = wx.TextCtrl(self.painel, 500,"", pos=(705, 528),  size=(92,23),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.valor_total_selecionados.SetBackgroundColour('#E5E5E5')
		self.valor_total_selecionados.SetForegroundColour("#195590")
		self.valor_total_selecionados.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		"""-----------------------------[ Botoes para agregar davs] """
		
		self.ffilia = wx.CheckBox(self.painel, 501, "Filtrar pedidos-davs filial: { "+str( self.csFilial )+"-"+login.filialLT[self.csFilial][14]+" }", pos=(14,278 ))
		self.ffilia.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ffilia.SetForegroundColour('#2865A1')
		self.ffilia.SetValue( True )
		
		self.Todos = wx.RadioButton(self.painel,-1,"Todos    ", pos=(15, 302),style=wx.RB_GROUP)
		self.Davss = wx.RadioButton(self.painel,-1,"Dav      ", pos=(15, 323))
		self.Orcam = wx.RadioButton(self.painel,-1,"Orçamento", pos=(15, 345))
		self.Devol = wx.CheckBox(self.painel,   -1,"Devolução", pos=(15, 367))

		filtrar_pedidos = ['1-Filtrar direto','2-Filtrar check-out','3-Filtrar loja virtual']
		self.copiaDav = wx.ComboBox(self.painel, -1, '',  pos=(12, 247), size=(389,27), choices = login.ciaRemot,style=wx.NO_BORDER|wx.CB_READONLY)
		self.pedido_filtrar = wx.ComboBox(self.painel, -1, filtrar_pedidos[0], pos=(120,363), size = (125,27), choices = filtrar_pedidos, style=wx.NO_BORDER|wx.CB_READONLY)
			
		self.Todos.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial-bold"))
		self.Davss.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial-bold"))
		self.Orcam.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial-bold"))
		self.Devol.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial-bold"))
		
		self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(120,310), size=(125,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(120,335), size=(125,25))

		self.consultar = wx.TextCtrl(self.painel, 500,"",                     pos=(15, 404),  size=(320,25),style=wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
		self.numeronfe = wx.TextCtrl(self.painel, 501,"",                     pos=(337,404),  size=(60, 25),style=wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
		self.pesqperio = wx.CheckBox(self.painel, -1, "Pesquisar\np/Período", pos=(283,330))
		self.vinculnfe = wx.CheckBox(self.painel, -1, "Marque para vincular orçamento ao\ndav selecionado p/emissão de NFe", pos=(2,435))

		self.atualCFis = wx.CheckBox(self.painel, -1, "Atualizar código fiscal", pos=(3,473))
		self.aTualizap = wx.CheckBox(self.painel, -1, "Atualizar preço    ", pos=(150,473))
		self.devolufrt = wx.CheckBox(self.painel, -1, "Devolução do frete ", pos=(267,473))
		self.devolacre = wx.CheckBox(self.painel, -1, "Devolução do acrescimo ", pos=(405,473))
		self.devorcame = wx.CheckBox(self.painel, -1, "Devolução pelo orçamento ", pos=(565,473))
		self.aproveita = wx.CheckBox(self.painel, -1, "Aproveitamento do dav com produtos de filiais diferentes ", pos=(3,502))
		self.nfecomple = wx.CheckBox(self.painel, -1, "Utilize orçamento p/NF complementar ICMS ", pos=(565,502))

		self.nfecomple.Enable( True if len(login.usaparam.split(";")) >=36 and login.usaparam.split(";")[35]=='T' else False )
		
		self.atualCFis.Enable( False )
		self.devorcame.Enable( False )
		self.aproveita.Enable( False )
		self.consrem.Enable( False )

		self.devolacre.Enable( self.p.TComa3.GetValue() )
		if len( login.filialLT[ self.csFilial ][35].split(";") ) >= 55 and login.filialLT[ self.csFilial ][35].split(";")[54] == "T":	self.devolacre.SetValue( False )
		else:	self.devolacre.SetValue( True )

		self.atualCFis.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pesqperio.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.devolufrt.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.aTualizap.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.vinculnfe.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.devolacre.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.devorcame.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.aproveita.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.nfecomple.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pesqperio.SetValue( True )
		self.devolufrt.Disable()
	
		self.suToT = wx.TextCtrl(self.painel,-1, value="0.00", pos=(410,325), size=(75,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Frete = wx.TextCtrl(self.painel,-1, value="0.00", pos=(410,360), size=(75,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Acres = wx.TextCtrl(self.painel,-1, value="0.00", pos=(495,325), size=(75,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Tribu = wx.TextCtrl(self.painel,-1, value="0.00", pos=(495,360), size=(75,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Desco = wx.TextCtrl(self.painel,-1, value="0.00", pos=(580,325), size=(75,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.ToDAV = wx.TextCtrl(self.painel,-1, value="0.00", pos=(580,360), size=(75,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)

		self.reducao = mkn(self.painel, 800, value = '0.00', pos=(307,446),size=(90,15), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.reducao.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.reducao.SetBackgroundColour('#E5E5E5')
		self.reducao.Enable( False )
		self.vinculnfe.Enable( False )

		self.ajdesco = mkn(self.painel, 801, value = '0.00', pos=(210,446),size=(90,15), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 4, fractionWidth = 2, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.ajdesco.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		if len( login.usaparam.split(";") ) >=7 and login.usaparam.split(";")[6] == "T":	self.ajdesco.Enable( True )
		else:	self.ajdesco.Enable( False )
		if not self.p.TComa3.GetValue():	self.ajdesco.Enable( False )

		self.frete_manual = mkn(self.painel, 888, value = '0.00', pos=(448,501),size=(100,15), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 4, fractionWidth = 2, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.frete_manual.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.frete_manual.SetBackgroundColour('#E5E5E5')
		self.frete_manual.Enable( False )
		
		self.suToT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Frete.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Acres.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tribu.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Desco.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ToDAV.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.suToT.SetForegroundColour('#7F7F7F')
		self.Frete.SetForegroundColour('#7F7F7F')
		self.Acres.SetForegroundColour('#7F7F7F')
		self.Tribu.SetForegroundColour('#7F7F7F')
		self.Desco.SetForegroundColour('#7F7F7F')
		self.ToDAV.SetForegroundColour('#7F7F7F')

		self.Procurar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.DvVoltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.Printar.Bind (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.extratp.Bind (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.importa.Bind (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.davrefe.Bind (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
				
		self.Procurar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.DvVoltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.Printar.Bind (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.extratp.Bind (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.importa.Bind (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.davrefe.Bind (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.selecionar)
		self.numeronfe.Bind(wx.EVT_TEXT_ENTER, self.selecionar)
		
		self.Procurar.Bind(wx.EVT_BUTTON,self.selecionar)
		self.DvVoltar.Bind(wx.EVT_BUTTON,self.voltar)
		self.Printar.Bind(wx.EVT_BUTTON, self.impresDav)
		self.extratp.Bind(wx.EVT_BUTTON, self.extrato)
		self.importa.Bind(wx.EVT_BUTTON, self.importacao)
		
		self.Bind(wx.EVT_KEY_UP,self.Teclas)
		self.ListaDavs.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.Teclas)		
		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.selecionar)
		self.Devol.Bind(wx.EVT_CHECKBOX, self.dvchekb)
		self.pedido_filtrar.Bind(wx.EVT_COMBOBOX, self.selecionar)
	
		self.Todos.Bind(wx.EVT_RADIOBUTTON,self.evradio)
		self.Davss.Bind(wx.EVT_RADIOBUTTON,self.evradio)
		self.Orcam.Bind(wx.EVT_RADIOBUTTON,self.evradio)
		self.Devol.Bind(wx.EVT_RADIOBUTTON,self.evradio)

		self.pesqperio.Bind(wx.EVT_CHECKBOX, self.selecionar)
		self.ffilia.Bind(wx.EVT_CHECKBOX, self.selecionar)
		self.copiaDav.Bind(wx.EVT_COMBOBOX, self.SELFilial)
		self.devolufrt.Bind(wx.EVT_CHECKBOX, self.freteManual)
		self.davrefe.Bind(wx.EVT_BUTTON, self.referenciaEntregas)
		
		self.reducao.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.ajdesco.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.frete_manual.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.consulta_cliente_varios.Bind(wx.EVT_BUTTON,self.pesquisaClientesOutros)
		self.consrem.Bind(wx.EVT_BUTTON, self.mostraRemocaoRomaneio)
		self.incluir_todos.Bind(wx.EVT_BUTTON, self.marcar_desmarcar_davs)
		self.limpar_lista.Bind(wx.EVT_BUTTON, self.limpar_lista_davs)
		self.apagar_selecionado.Bind(wx.EVT_BUTTON, self.limpar_lista_davs)
	
		if self.p.TComa3.GetValue() == True:
			
			self.Devol.Disable()
			self.aTualizap.Disable()
			
			self.copiaDav.Enable( False )
			self.dcFilial.Enable( False )
            
		if self.p.TComa4.GetValue():	self.aTualizap.Disable()
		if self.p.TComa3.GetValue():	self.ffilia.Enable( False )

		if self.p.caixaDavRecalculo == True:
			
			self.consultar.SetValue( self.p.caixaDavNumeroRec )

			self.Todos.Enable( False )
			self.Davss.Enable( False )
			self.Orcam.Enable( False )
			self.Devol.Enable( False )
			self.consultar.Enable( False )

			self.copiaDav.Enable( False )
			self.dcFilial.Enable( False )

			self.Procurar.Enable( False )
			self.Printar.Enable( False )
			self.extratp.Enable( False ) 
			self.ffilia.Enable( False )

			self.dindicial.Enable( False )
			self.datafinal.Enable( False )
			self.pesqperio.Enable( False )
			self.devolufrt.Enable( False )
			self.aTualizap.Enable( False )
			self.davrefe.Enable( False )
			
			self.atualCFis.Enable( True )

		self.selecionar(wx.EVT_BUTTON)
		self.consultar.SetFocus()

		""" Icones """
		self.importa.Enable(acs.acsm("612",True)) #-:Importar Davs-Orcamentos
		if len( login.usaparam.split(";") ) >=5 and login.usaparam.split(";")[4] == "T":

			self.ffilia.Enable( False )
			self.copiaDav.Enable( False )
			if self.p.TComa3.GetValue():	self.ffilia.Enable( True )

		self.inibir_consolidar_nota=False
		if self.p.TComa2.GetValue() and len(login.usaparam.split(";"))>=50 and login.usaparam.split(";")[49]=="T":	self.inibir_consolidar_nota=True
		
		if not self.inibir_consolidar_nota:

		    self.incluir_todos.Enable(False)
		    self.apagar_selecionado.Enable(False)
		    self.limpar_lista.Enable(False)	    
		    self.relacionar_pedidos.Enable(False)

	def limpar_lista_davs(self,event):

	    if self.relacionar_pedidos.GetItemCount():
		
		informe = u"Limpar toda lista de davs selecionados para emissão de nf"
		if event.GetId()==334:	informe = u"Apagar o dav selecionado"
		receb = wx.MessageDialog(self,informe + u"\n\nConfirme p/Continuar...\n"+(" "*180),"Limpar a lista",wx.YES_NO|wx.NO_DEFAULT)
		if event.GetId()==335 and receb.ShowModal() ==  wx.ID_YES:

		    self.relacionar_pedidos.DeleteAllItems()
                    self.relacionar_pedidos.Refresh()
		    self.valor_total_selecionados.SetValue("")

		elif event.GetId()==334 and receb.ShowModal() ==  wx.ID_YES:
		    self.relacionar_pedidos.DeleteItem( self.relacionar_pedidos.GetFocusedItem() )
		    self.relacionar_pedidos.Refresh()
		    
		    self.valor_total_selecionados.SetValue("")
		    if self.relacionar_pedidos.GetItemCount():
			
			valor_totalizado=Decimal()
			for i in range(self.relacionar_pedidos.GetItemCount()):

			    valor_totalizado += Decimal(self.relacionar_pedidos.GetItem(i,5).GetText())
			    self.valor_total_selecionados.SetValue('R$ '+format(valor_totalizado,','))
    			    if i %2:	self.relacionar_pedidos.SetItemBackgroundColour(i, "#75A9DB")
			    else:	self.relacionar_pedidos.SetItemBackgroundColour(i, "#61A3EF")

	def marcar_desmarcar_davs(self,event):

	    if self.ListaDavs.GetItemCount() and self.inibir_consolidar_nota:
		
		self.valor_total_selecionados.SetValue("")
		registros = self.ListaDavs.GetItemCount() if event.GetId()==333 else 1
		nome_cliente = self.ListaDavs.GetItem(self.ListaDavs.GetFocusedItem(),3).GetText()

		for indice in range(registros):
		
		    if event.GetId()!=333:	indice = self.ListaDavs.GetFocusedItem()
		    status = self.ListaDavs.GetItem(indice,16).GetText()
		    notafiscal = self.ListaDavs.GetItem(indice,22).GetText()
		    cancelado = self.ListaDavs.GetItem(indice,17).GetText()
		    
		    orcame = self.ListaDavs.GetItem(indice,0).GetText()
		    clNome = self.ListaDavs.GetItem(indice,3).GetText()
		    valord = Decimal(self.ListaDavs.GetItem(indice,4).GetText().replace(',',''))
		    caixas = self.ListaDavs.GetItem(indice, 9).GetText()
		    clDocu = self.ListaDavs.GetItem(indice,18).GetText()
		    clCodi = self.ListaDavs.GetItem(indice,19).GetText()

		    filial = self.ListaDavs.GetItem(indice,14).GetText().split("-")[1]
		    vended = self.ListaDavs.GetItem(indice,15).GetText()
		    idfili = self.ListaDavs.GetItem(indice,20).GetText()
		    
		    dados_envio = orcame+'|'+clNome+'|'+clDocu+'|'+clCodi+'|'+filial+'|'+vended+'|'+idfili

		    if clNome==nome_cliente:

			menssagem=''
			if status.strip()!='1':	menssagem=u"Não e pedido"
			if notafiscal:	menssagem+=u", Nota fiscal emitida" if menssagem else "Nota fiscal emitida"
			if cancelado:	menssagem+=u", Cancelado" if menssagem else u"Cancelado"
			if not clDocu:	menssagem+=u", Cliente sem CNPJ/CPF" if menssagem else u"Cliente sem CNPJ/CPF"
			if filial!=idfili:	menssagem+=u", Filiais diferentes" if menssagem else u"Filiais diferentes"
			if not caixas:	menssagem+=u", Dav não recebido" if menssagem else u"Dav não recebido"

			if not menssagem:
			    
			    for i in range(self.relacionar_pedidos.GetItemCount()):
				if self.relacionar_pedidos.GetItem(i,2).GetText()!=nome_cliente:
				    menssagem=u"Clitente diferentes"
				    break
				if self.relacionar_pedidos.GetItem(i,1).GetText()==orcame:
				    menssagem=u"Numero de dav ja lançado"
				    break

			if event.GetId()!=333 and menssagem:	alertas.dia(self,u"{ Flata dados para incluir o pedido na relação }\n\n"+menssagem+'\n'+(' '*170),'Validando pedido')
			if not menssagem:
			    
			    incluir = self.relacionar_pedidos.GetItemCount()
			    self.relacionar_pedidos.InsertStringItem(incluir,str(incluir+1).zfill(3))
			    self.relacionar_pedidos.SetStringItem(incluir,1,  orcame )
			    self.relacionar_pedidos.SetStringItem(incluir,2,  clNome )
			    self.relacionar_pedidos.SetStringItem(incluir,3,  clDocu )
			    self.relacionar_pedidos.SetStringItem(incluir,4,  dados_envio )
			    self.relacionar_pedidos.SetStringItem(incluir,5,  str(valord))
			    if incluir %2:	self.relacionar_pedidos.SetItemBackgroundColour(incluir, "#61A3EF")

		valor_totalizado=Decimal()
		self.valor_total_selecionados.SetValue('')
		if self.relacionar_pedidos.GetItemCount():

		    for i in range(self.relacionar_pedidos.GetItemCount()):

			valor_totalizado += Decimal(self.relacionar_pedidos.GetItem(i,5).GetText())
			self.valor_total_selecionados.SetValue('R$ '+format(valor_totalizado,','))
	    
	def pesquisaClientesOutros(self,event):
	    
	    adiciona.TipoConsulta='55'		

	    addc_frame=adiciona(parent=self,id=-1)
	    addc_frame.Centre()
	    addc_frame.Show()
	    
	def freteManual( self, event ):
		
		if self.devolufrt.GetValue():	self.frete_manual.Enable( True )
		else:
			self.frete_manual.Enable( False )
			self.frete_manual.SetValue('0')
		
	def TlNum(self,event):

		TelNumeric.decimais = 2
		tel_frame=TelNumeric(parent=self,id=event.GetId() )
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		if idfy == 800:
			
			if Decimal(valor) > Decimal('99999.99'):
				valor = "0.00"
				alertas.dia(self,"Quantidade enviado é incompatível!!","Retaguarda")

			self.reducao.SetValue( valor )

		if idfy == 801:
			
			if Decimal(valor) > Decimal('99999.99'):
				valor = "0.00"
				alertas.dia(self,"Valor enviado é incompatível!!","Retaguarda")

			self.ajdesco.SetValue( valor )

		if idfy == 888:
			
			if Decimal(valor) > Decimal('99999.99'):
				valor = "0.00"
				alertas.dia(self,"Valor enviado é incompatível!!","Retaguarda")

			self.frete_manual.SetValue( valor )
			
	def evradio(self,event):

		self.selecionar(wx.EVT_BUTTON)
		self.ListaDavs.Refresh()

	def referenciaEntregas(self,event):
		
		if self.ListaDavs.GetItemCount() > 0 and self.ListaDavs.GetItem( self.ListaDavs.GetFocusedItem(), 0 ).GetText() !="" and Decimal( self.suToT.GetValue().replace(",","") ) > 0:
			self.p.alteraReferencia( self.ListaDavs.GetItem( self.ListaDavs.GetFocusedItem(), 0 ).GetText() )
				
		else:	alertas.dia( self, "Lista vazia e/ou dav não selecionado...\n"+(" "*120),"Retaguarda: Alterar referências")

	def SELFilial(self,event):

		self.ListaDavs.DeleteAllItems()
		if self.copiaDav.GetValue().split('-')[0] == "":
			
			self.dcFilial.SetValue('')
			self.dcFilial.SetBackgroundColour("#E5E5E5")
			self.ListaDavs.SetBackgroundColour('#EFF4FA')

			self.Devol.Enable(True)

		if self.copiaDav.GetValue().split('-')[0] != "":

			self.dcFilial.SetValue( self.copiaDav.GetValue().split('-')[0] +'-'+ login.filialLT[ self.copiaDav.GetValue().split('-')[0] ][1] )
			self.dcFilial.SetBackgroundColour("#A52A2A")
			self.dcFilial.SetForegroundColour('#FF0000')
			self.ListaDavs.SetBackgroundColour('#D8B9BE')

			self.Todos.SetValue(True)
			self.Devol.Enable(False)

	def dvchekb(self,event):
		
		if self.Devol.GetValue() == True:

			self.modo.SetLabel("Modo: Devolução")
			self.modo.SetForegroundColour('#A52A2A')
			self.ListaDavs.SetBackgroundColour('#F5E5E9')
			self.ListaDavs.attr1.SetBackgroundColour('#F8EDF0')
			self.ListaDavs.DeleteAllItems()

			header = self.ListaDavs.GetColumn ( 0 )
			header.SetText ( 'Nº Devolução' )
			self.ListaDavs.SetColumn ( 0, header )
			self.SetTitle(u'Devolução - Consulta e Reimpressão')

			self.Todos.SetValue(True)
			self.Todos.Disable()
			self.Davss.Disable() 
			self.Orcam.Disable()
			self.importa.Disable()
			
			self.selecionar(wx.EVT_BUTTON)
			self.ListaDavs.Refresh()

		else:

			self.modo.SetLabel("Modo: DAVs")
			self.modo.SetForegroundColour("#A1A114")
			self.ListaDavs.SetBackgroundColour('#EFF4FA')
			self.ListaDavs.attr1.SetBackgroundColour('#E5ECF2')
			self.ListaDavs.DeleteAllItems()
			self.SetTitle(u'DAVs: Pedidos,Orçamentos - Consulta e Reimpressão')

			header = self.ListaDavs.GetColumn ( 0 )
			header.SetText ( 'Nº D A V' )
			self.ListaDavs.SetColumn ( 0, header )

			self.Todos.Enable()
			self.Davss.Enable() 
			self.Orcam.Enable()
			self.importa.Enable()

			self.selecionar(wx.EVT_BUTTON)
			self.ListaDavs.Refresh()
		
			""" Icones """
		self.importa.Enable(acs.acsm("0612",True))
	
	def importacao(self,event):

		informacao_consolidar=""
		if self.relacionar_pedidos.GetItemCount() and self.inibir_consolidar_nota:

		    self.consultar.SetValue(self.relacionar_pedidos.GetItem(self.relacionar_pedidos.GetFocusedItem(),1).GetText())
		    self.numeronfe.SetValue('')
		    self.selecionar(wx.EVT_BUTTON)
		    self.ListaDavs.SetFocus()
		    self.ListaDavs.Focus(0)
		    
		    informacao_consolidar=u"\n\nDAVs, relacionados para emissão de notas consolidadas"
		    
		if self.vinculnfe.GetValue() and not self.reducao.GetValue():
		
			alertas.dia( self, "Vinculo sem percentual de redução...\n"+(" "*100),"Orçamento vinculado")
			return
		
		if not self.vinculnfe.GetValue() and self.reducao.GetValue():

			alertas.dia( self, "Vinculo sem marcação de vinculado...\n"+(" "*100),"Orçamento vinculado")
			return

		if self.ListaDavs.GetItem(self.ListaDavs.GetFocusedItem(),26).GetText() and self.ListaDavs.GetItem(self.ListaDavs.GetFocusedItem(),16).GetText() == '2':

			if self.p.TComa1.GetValue() or self.p.TComa2.GetValue():
			    
			    if not self.nfecomple.GetValue():
				alertas.dia( self, u"{ DAV/Orçamento com marca de vinculo, não pode ser utilizado }\n\nVinculado ao dav/orcamento ["+self.ListaDavs.GetItem(self.ListaDavs.GetFocusedItem(),26).GetText()+"]\n"+(" "*140),"Orçamento vinculado")
				return
		if self.nfecomple.GetValue() and len(self.ListaDavs.GetItem(self.ListaDavs.GetFocusedItem(),23).GetText().strip())<44:

			alertas.dia(self,u"{ Orçamento para emissão de nota fiscal complementar }\n\n1-Chave vazia e/ou chave incompleta\n\nNumero chave: "+self.ListaDavs.GetItem(self.ListaDavs.GetFocusedItem(),23).GetText()+"\n"+(' '*160),"DAV(s): Importação")
			return

		if Decimal(self.ToDAV.GetValue().replace(',','')) == 0:	alertas.dia(self.painel,"Selecione um DAV p/Continuar...\n",u"Importação de DAVs")
		else:
				
			indice = self.ListaDavs.GetFocusedItem()
			orcame = str( self.ListaDavs.GetItem(indice,0).GetText() )

			clNome = self.ListaDavs.GetItem(indice,3).GetText()
			clDocu = str(self.ListaDavs.GetItem(indice,18).GetText())
			clCodi = str(self.ListaDavs.GetItem(indice,19).GetText())

			filial = str( self.ListaDavs.GetItem(indice,14).GetText().split("-")[1] )
			vended = self.ListaDavs.GetItem(indice,15).GetText()
			idfili = str( self.ListaDavs.GetItem(indice,20).GetText() )

			regime = ""

			"""  Permitir q utilize pedidos de qualquer filial p/filial atual se as filias selecionadas forem estoque fisico unificado  """
			esf_unificado = True if login.filialLT[ self.csFilial ][35].split(";")[4] == "T" and login.filialLT[ idfili ][35].split(";")[4] == "T" else False

			"""  Altera a filial automaticamente se os estoques nao forem unificados   """
			if self.csFilial != idfili and not esf_unificado:

				fA = self.csFilial+'-'+login.filialLT[ self.csFilial ][14].upper()
				fD = idfili+'-'+login.filialLT[ idfili ][14].upper()
				
				alFil = wx.MessageDialog(self,u"{ Filiais Diferentes }\n\nFilial Atual...: "+str( fA )+u"\nFilial do DAV: "+str( fD )+u"\n\nO Sistema vai alterar a filial p/"+str( fD )+u"\nConfirme para continuar...\n"+(" "*180),u"Alteração da Filial",wx.YES_NO|wx.NO_DEFAULT)
				if alFil.ShowModal() !=  wx.ID_YES:	return
				
				regime = login.filialLT[ idfili ][30].split(";")[11]

				"""  Se as filiais forem diferentes e regimes diferentes o sistema pede para autualizar o codigo fiscal  """
				if self.csFilial != idfili and idfili and self.csFilial and regime !=login.filialLT[ self.csFilial ][30].split(";")[11]:	self.atualCFis.SetValue( True )

				self.csFilial = idfili
				self.p.davfili.SetValue( idfili +"-"+ login.filialLT[ idfili ][14] )
				self.p.arelFilial( 701 )

			else:
				"""  Se as filiais forem diferentes e regimes diferentes o sistema pede para autualizar o codigo fiscal  """
				if self.csFilial != idfili and idfili and self.csFilial and login.filialLT[ idfili ][30].split(";")[11] !=login.filialLT[ self.csFilial ][30].split(";")[11]:	self.atualCFis.SetValue( True )

			nnf = nfc = nfe = nfd = ""
			
			if str( self.ListaDavs.GetItem(indice,22) ).strip() !="" and self.p.TComa4.GetValue() == True:	nnf = str( self.ListaDavs.GetItem(indice,22).GetText() )
			if str( self.ListaDavs.GetItem(indice,23) ).strip() !="" and self.p.TComa4.GetValue() == True:	nfc = str( self.ListaDavs.GetItem(indice,23).GetText() )
			if str( self.ListaDavs.GetItem(indice,24) ).strip() !="" and self.p.TComa4.GetValue() == True:	nfe = str( self.ListaDavs.GetItem(indice,24).GetText() ).split(' ')[0]

			if self.p.TComa4.GetValue() == True and nnf !="" and nfc != "" and nfe !="":	nfd = nnf+";"+nfc+";"+format(datetime.datetime.strptime(nfe, "%Y-%m-%d"),"%d/%m/%Y")
			self.p.enTregaFutura = nfd

			RegisTros = self.p.ListaPro.GetItemCount()
			ValorDAVs = Decimal( str( self.p.Tg.GetValue() ).replace(',','') )

			if self.p.TComa3.GetValue() == True and self.prazo.GetLabel() !='':

				alertas.dia(self,u"Devolução fora do prazo...\n"+(' '*80),"DAV(s): Devolução")
				return

			if RegisTros !=0 or ValorDAVs !=0:

				alertas.dia(self,u"Lista de DAV(s), Não estar vazia...\n"+(' '*60),"DAV(s): Importação de Orçamentos")
				return

			if self.p.TComa3.GetValue() and str( self.ListaDavs.GetItem(indice,16).GetText() ).strip() !='1':
				
				alertas.dia(self,u"{ Devolução }\n\nA devolução aceita vincular apenas davs-pedidos...\n"+(' '*120),"DAV(s): Importação")
				return
				
			if self.p.caixaDavRecalculo != True and self.p.TComa3.GetValue() != True and self.p.TComa4.GetValue() !=True:

				_apaga = wx.MessageDialog(self,u"DAV Nº { "+str( orcame )+" }"+informacao_consolidar+u"\n\nO sistema vai importa este DAV como orçamento\ndepois você pode transformar em pedido\n\nConfirme para importar o pedido\n"+(" "*180),u"Caixa-Recebimentos de DAVs",wx.YES_NO|wx.NO_DEFAULT)
				if _apaga.ShowModal() ==  wx.ID_YES:	pass
				else:	return

			if Decimal( self.Frete.GetValue().replace(',','') ) and Decimal( self.frete_manual.GetValue() ) and Decimal( self.frete_manual.GetValue() ) > Decimal( self.Frete.GetValue().replace(',','') ):

				alertas.dia(self,u"{ Valor superior do frete }\n\nO valor manual do frete e maior do que o frete cobrado...\n"+(' '*120),"DAV(s): Importação")
				return

			if RegisTros == 0:

			    if self.nfecomple.GetValue() and self.ListaDavs.GetItem(indice,16).GetText().strip()=='2':	alertas.dia(self,u"{ Nota fiscal complementar [ Aceitas apenas davs emitidos ]  }\n\nClick OK p/voltar\n"+(' '*160),"DAV(s): Importação")
			    else:
				_fil = self.csFilial
				if self.copiaDav.GetValue().split('-')[0] !="":	_fil = self.copiaDav.GetValue().split('-')[0]

				impDav = ImporTaDAvs()
				dav_reducao = self.ListaDavs.GetItem( indice, 26 ).GetText() if self.p.TComa3.GetValue() else ""
				nuchave_nfe = self.ListaDavs.GetItem(indice,23).GetText().strip()

				""" Processar varios pedidos { Consolidar emissao de notas } """
				if self.relacionar_pedidos.GetItemCount() and self.inibir_consolidar_nota:
				    
				    valida_saida=[]
				    self.p.consolida_emissao_nota_fiscal=True
				    for cn in range(self.relacionar_pedidos.GetItemCount()):
					
					orcame=self.relacionar_pedidos.GetItem(cn,1).GetText()
					saida=impDav.davsImporTa(self, self.p, _fil, orcame, clCodi, regime, clDocu, clNome, vended, dav_reducao, self.devorcame.GetValue(), self.nfecomple.GetValue(), nuchave_nfe )
					valida_saida.append(saida)
					
				    self.p.transfo.Enable(False)
				    self.voltar(wx.EVT_BUTTON)
				    
				else:

				    if impDav.davsImporTa(self, self.p, _fil, orcame, clCodi, regime, clDocu, clNome, vended, dav_reducao, self.devorcame.GetValue(), self.nfecomple.GetValue(), nuchave_nfe ):

					if self.nfecomple.GetValue():
					    
					    self.p.transfo.Enable(False)
					    self.p.notafiscalcomplementar_chave=self.ListaDavs.GetItem(indice,23).GetText().strip()
					    
					self.voltar(wx.EVT_BUTTON)

			if self.p.caixaDavRecalculo == True:	self.p.recalcularDavCaixa()

	def extrato(self,event):

		indice = self.ListaDavs.GetFocusedItem()
		if self.ListaDavs.GetItem(indice, 18).GetText().strip() != '':	self.extcli.extratocliente( self.ListaDavs.GetItem(indice, 18).GetText(), self, Filial = self.csFilial, NomeCliente = self.ListaDavs.GetItem(indice, 3).GetText() )
		else:	alertas.dia(self,"CNPJ-CPF, Vazio...\n"+(" "*100),"Extrato do Cliente")

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 221:	sb.mstatus(u"  Sair da consulta de davs",0)
		elif event.GetId() == 222:	sb.mstatus(u"  Procurar/Pesquisar davs,cliente,Nº do DAV",0)
		elif event.GetId() == 223:	sb.mstatus(u"  Consultar,Visualizar,Enviar p/Email, Reimprimir Davs",0)
		elif event.GetId() == 224:	sb.mstatus(u"  Extrato do cliente",0)
		elif event.GetId() == 225:	sb.mstatus(u"  Importar ORÇAMENTO - DEVOLUÇÃO",0)
		elif event.GetId() == 226:	sb.mstatus(u"  Altera referencias de entrega do dav selecionado",0)
		
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus(u"  Consulta e Impressão de DAVs emitidos",0)
		event.Skip()

	def impresDav(self,event):

		__modo    = ''
		if self.Devol.GetValue() == True:	__modo = "DEV"
		
		indice    = self.ListaDavs.GetFocusedItem()
		NumeroDav = self.ListaDavs.GetItem( indice, 0 ).GetText()
		codFilial = self.ListaDavs.GetItem( indice,20 ).GetText()
		TipoDav   = self.ListaDavs.GetItem( indice,16 ).GetText()

		"""  Bloquei do Envio de Email   """
		if TipoDav == "2":	emai = "607"
		else:	emai = "608"
		
		_fil = self.csFilial
		if self.copiaDav.GetValue().split('-')[0] !="":	_fil = self.copiaDav.GetValue().split('-')[0]

		self.impres.impressaoDav( NumeroDav, self.myfram, True, True, __modo,"", servidor = _fil, codigoModulo = "616", enviarEmail = emai,recibo=False, vlunitario=True)

	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()

		"""  Aproveitamento de davs com produtos de filais diferentes  """
		self.aproveita.Enable( False )
		self.aproveita.SetValue( False )
 
		if keycode == wx.WXK_ESCAPE:	self.voltar(wx.EVT_BUTTON)
		if controle !=None and controle.GetId() == 300:

			indice = self.ListaDavs.GetFocusedItem()

			if self.p.TComa3.GetValue() and self.ListaDavs.GetItem(indice,5).GetText() and Decimal( self.ListaDavs.GetItem(indice,5).GetText().replace(',','') ):	self.devolufrt.Enable( True )
			else:
				
				self.devolufrt.SetValue( False )
				self.devolufrt.Enable( False )

			self.aTualizaImporTacao()
			
		""" Devolucao fora do prazo """
		if self.p.TComa3.GetValue() == True:

			indice = self.ListaDavs.GetFocusedItem()
			pagame = str( self.ListaDavs.GetItem(indice,10).GetText() )
			fildav = str( self.ListaDavs.GetItem(indice,20).GetText() )
			dahoje = datetime.datetime.now().date()
			if self.ajdesco.GetValue():	self.ajdesco.SetValue(0)
			
			if pagame and fildav and login.filialLT[ fildav ][20] !='' and Decimal(login.filialLT[ self.csFilial ][20]) > 0:	

				pagm = datetime.datetime.strptime(pagame, '%d/%m/%Y').date()
				dias = ( dahoje - pagm ).days

				if dias > int(login.filialLT[ self.csFilial ][20]):	self.prazo.SetLabel("Devolução fora do prazo!")

				else:	self.prazo.SetLabel("")
				
			else:	self.prazo.SetLabel("")

		"""  orcamento com reducao do preco p/emissao da nfe """
		if not self.p.TComa3.GetValue() and len( login.usaparam.split(";") ) >=1 and login.usaparam.split(";")[0] == "T" and self.ListaDavs.GetItemCount() and not self.ListaDavs.GetItem( self.ListaDavs.GetFocusedItem(), 23).GetText() and self.ListaDavs.GetItem( self.ListaDavs.GetFocusedItem(), 16).GetText() == '1':

			self.vinculnfe.Enable( True )
			self.reducao.Enable( True )

		else:
			
			self.vinculnfe.SetValue( False )
			self.vinculnfe.Enable( False )
			self.reducao.Enable( False )
			
		if self.p.TComa3.GetValue() and self.ListaDavs.GetItem( self.ListaDavs.GetFocusedItem(), 26 ).GetText():
			
			self.vincu.SetLabel(u"NFe orçamento: "+self.ListaDavs.GetItem( self.ListaDavs.GetFocusedItem(), 26 ).GetText())
			self.devorcame.SetValue( True )
			self.devorcame.Enable( True )
			
		else:
			self.vincu.SetLabel('')
			self.devorcame.SetValue( False )
			self.devorcame.Enable( False )

		if controle !=None and controle.GetId() == 500 and keycode == wx.WXK_TAB:	self.numeronfe.SetFocus()
		if controle !=None and controle.GetId() == 501 and keycode == wx.WXK_TAB:	self.consultar.SetFocus()

	def aTualizaImporTacao(self):
		
		indice = self.ListaDavs.GetFocusedItem()
		filial = self.ListaDavs.GetItem(indice,14).GetText().split("-")[1]
		self.suToT.SetValue( self.ListaDavs.GetItem(indice,4).GetText() )
		self.Frete.SetValue( self.ListaDavs.GetItem(indice,5).GetText() )
		self.Acres.SetValue( self.ListaDavs.GetItem(indice,6).GetText() )
		self.Desco.SetValue( self.ListaDavs.GetItem(indice,7).GetText() )
		self.ToDAV.SetValue( self.ListaDavs.GetItem(indice,8).GetText() )

		if self.p.TComa3.GetValue() == True and self.ListaDavs.GetItem(indice,5).GetText() !='' and Decimal( self.ListaDavs.GetItem(indice,5).GetText() ) !=0:	self.devolufrt.Enable( True )
		else:
			
			self.devolufrt.SetValue( False )
			self.devolufrt.Enable( False )

		emissao_dav = self.ListaDavs.GetItem(indice, 1).GetText()
		data_hoje = datetime.datetime.now().strftime("%Y-%m-%d")

		emissao_dav = self.p.data_emissao_devolucao = datetime.datetime.strptime(emissao_dav, "%d/%m/%Y").date()
		data_hoje = datetime.datetime.strptime(data_hoje, "%Y-%m-%d").date()
		
		_Rec = self.ListaDavs.GetItem(indice, 9).GetText()+" "+self.ListaDavs.GetItem(indice,10).GetText()
		_Ent = self.ListaDavs.GetItem(indice,12).GetText()+" "+self.ListaDavs.GetItem(indice,13).GetText()
		_rmn = self.ListaDavs.GetItem(indice,25).GetText()
		_rda = self.ListaDavs.GetItem(indice,29).GetText() #--// Dav removido do romaneio

		self.rcusa.SetLabel(_Rec)
		self.endat.SetLabel(_Ent)
		self.filvd.SetLabel((' '*10)+"Filial: "+self.ListaDavs.GetItem(indice,14).GetText()+'\nVendedor: '+self.ListaDavs.GetItem(indice,15).GetText())

		self.Tipos.SetLabel(u'Pedido: '+self.ListaDavs.GetItem(indice, 0).GetText() +'  NF: '+ self.ListaDavs.GetItem(indice,22).GetText() +'/'+ self.ListaDavs.GetItem(indice,27).GetText()+'  Filial: '+ self.ListaDavs.GetItem(indice, 20).GetText())
		self.Tipos.SetForegroundColour("#71710D")

		if self.ListaDavs.GetItem(indice, 26).GetText():

			self.Tipos.SetLabel(u'Orçamento: '+self.ListaDavs.GetItem(indice, 26).GetText()+ '  Filial: '+ self.ListaDavs.GetItem(indice, 20).GetText() )
			self.Tipos.SetForegroundColour("#406589")
		
		"""   Data de Entrega e Nome do Motorista  """
		self.endat.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.endat.SetForegroundColour(self.lreceb)
		
		if _rmn.strip():
			
			if len( _rmn.split(":") ) >= 2:

				if len( _rmn.split(":") ) >= 3:	self.enTre.SetLabel( "Motorista: "+str( _rmn.split(":")[2] ) )
				self.endat.SetLabel( _rmn.split(":")[1] )
				self.endat.SetForegroundColour("#A52A2A")
				self.endat.SetFont(wx.Font(12,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
							
		else:	self.enTre.SetLabel("")

		self.consrem.Enable(False)
		if _rda.strip() and 'REMOVE' in _rda:
		    
		    self.enTre.SetLabel("Removido: "+_rda.split('REMOVE')[1].strip().split('|')[0])
		    self.consrem.Enable(True)
		    
		"""  Marcar p/nao devolver o acrescimo  """
		if self.p.TComa3.GetValue():

			if len( login.filialLT[ filial ][35].split(";") ) >= 55 and login.filialLT[ filial ][35].split(";")[54] == "T":	self.devolacre.SetValue( False )
			else:	self.devolacre.SetValue( True )

	def mostraRemocaoRomaneio(self,event):

	    indice = self.ListaDavs.GetFocusedItem()
	    filial = self.ListaDavs.GetItem(indice,14).GetText().split("-")[1]
	    _rda = self.ListaDavs.GetItem(indice,29).GetText() #--// Dav removido do romaneio

	    hs = "Removido: "+_rda.split('REMOVE')[1].strip().split('|')[0]
	    motivo = _rda.split('REMOVE')[1].strip().split('|')[1]

	    MostrarHistorico.TP = ""
	    MostrarHistorico.hs = hs +'\n\n[ Motivo ]\n'+ motivo
	    MostrarHistorico.TT = "Remocao do dav do romaneio"
	    MostrarHistorico.AQ = ""
	    MostrarHistorico.FL = filial
	    MostrarHistorico.GD = ""

	    his_frame=MostrarHistorico(parent=self,id=-1)
	    his_frame.Centre()
	    his_frame.Show()
	    
	def voltar(self,event):
		
		self.p.Enable()
		self.Destroy()

	def selecionar(self,event):

		_fil = self.csFilial
		if self.copiaDav.GetValue().split('-')[0] != "":	_fil = self.copiaDav.GetValue().split('-')[0]
		
		if len(login.usaparam.split(";"))>=43 and login.usaparam.split(";")[42]=="T":

		    if not self.consultar.GetValue().strip():	return
		    if self.consultar.GetValue().strip().isdigit():		pass
		    else:

			alertas.dia(self,'{ Bloqueio para outras consultas }\n\n1 - Utilize o numero do dava para consultar...\n'+(' '*140),'Bloqueios para outras consultas')
			return
			
		conn = sqldb()
		sql  = conn.dbc("DAVs,Consuta de DAVs", fil = _fil, janela = self )

		if sql[0] == True:
			
			_mensagem = mens.showmsg("Consultando dados\nAguarde...")
			
			inicial = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			final   = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			consul  = self.consultar.GetValue()

			pPro = "SELECT * FROM cdavs WHERE cr_regi!=0 ORDER BY cr_edav,cr_ndav"
			if self.numeronfe.GetValue().strip():

				consul = ""
				pPro = "SELECT * FROM cdavs WHERE cr_nota='"+ self.numeronfe.GetValue() +"' ORDER BY cr_edav,cr_ndav"
				
			if self.pesqperio.GetValue() == True:	pPro = pPro.replace("WHERE","WHERE cr_edav >='"+inicial+"' and cr_edav <='"+final+"' and")
			if self.pesqperio.GetValue() == True:	pPro = pPro.replace("WHERE","WHERE cr_edav >='"+inicial+"' and cr_edav <='"+final+"' and")
			if   consul.strip().isdigit() == True:	pPro = "SELECT *  FROM cdavs WHERE cr_ndav='"+str( consul ).zfill(13)+"'"			
			elif self.p.TComa3.GetValue() == True or self.p.TComa4.GetValue() == True:
					
				if self.p.TComa3.GetValue() == True:	pPro = pPro.replace("WHERE","WHERE cr_tipo ='1' and cr_reca='1' and cr_tfat='' and")
				if self.p.TComa4.GetValue() == True:	pPro = pPro.replace("WHERE","WHERE cr_tipo ='1' and cr_reca='1' and cr_tfat='1' and")

				self.Todos.Enable( False )
				self.Davss.SetValue( True )
				self.Orcam.Enable( False )
				self.Devol.Enable( False )

			else:

				if self.Davss.GetValue() == True:	pPro = pPro.replace("ORDER BY cr_edav","and cr_tipo ='1' ORDER BY cr_edav")
				if self.Orcam.GetValue() == True:	pPro = pPro.replace("ORDER BY cr_edav","and cr_tipo ='2' ORDER BY cr_edav")

			if consul != '' and len( consul.split(':') ) == 1:	pPro = pPro.replace("ORDER BY cr_edav","and cr_nmcl like '"+consul+"%' ORDER BY cr_edav")
			if consul != '' and len( consul.split(':')[0] ) == 1 and consul.split(':')[0].upper() == "P":	pPro = pPro.replace("ORDER BY cr_edav","and cr_nmcl like '%"+str( consul.split(':')[1].upper() )+"%' ORDER BY cr_edav")
			if consul != '' and len( consul.split(':')[0] ) == 1 and consul.split(':')[0].upper() == "V":	pPro = pPro.replace("ORDER BY cr_edav","and cr_nmvd like  '"+str( consul.split(':')[1].upper() )+"%' ORDER BY cr_edav")
			if self.Devol.GetValue() == True:	pPro = pPro.replace("cdavs","dcdavs")
				
			if self.ffilia.GetValue() == True:	pPro = pPro.replace("WHERE","WHERE cr_inde='"+str( self.csFilial )+"' and")
			if len(login.usaparam.split(";"))>=33 and login.usaparam.split(";")[32]=="T":	pPro=pPro.replace("WHERE","WHERE cr_udav='"+login.usalogin+"' and")
			
			_pesqui = sql[2].execute( pPro )
			_result = sql[2].fetchall()

			self.clientes = {}
			self.registro = 0

			_registros = 0
			relacao    = {}
		
			indice  = 0
			filtro_pedidos = self.pedido_filtrar.GetValue().split('-')[0]
			for i in _result:

				_DTRec = ''
				_DTEmi = ''
				_DTEnt = ''
				romane = ''
				nserie = ''
				
				if i[73]:	nserie = i[73][22:25]
				if i[11] !=None:	_DTEmi = i[11].strftime("%d/%m/%Y")
				if i[13] !=None:	_DTRec = i[13].strftime("%d/%m/%Y")
				if i[21] !=None:	_DTEnt = i[21].strftime("%d/%m/%Y")
				if i[90] !=None and i[90] !="" and sql[2].execute( "SELECT rm_roman,rm_dtent,rm_motor FROM romaneio WHERE rm_roman='"+str( i[90] )+"'" ) !=0:
					
					rsRom = sql[2].fetchall()[0]
					rRoma = rsRom[1]
					rMoTo = rsRom[2]

					if rRoma !=None and rRoma !="":	romane = str( i[90] )+": "+format( rRoma, '%d/%m/%Y' )+":"+str( rMoTo )
				avancar=False
				if filtro_pedidos == '1' and 'CK' not in i[2]:	avancar = True
				if filtro_pedidos == '2' and 'CK' in i[2]:	avancar = True

				if avancar:
				    romaneio_removido = i[91] if i[91] else ""
				    
				    relacao[_registros] = str(i[2]),\
				    _DTEmi,\
				    str( i[54] )+'-'+str( i[12] ),\
				    i[4],\
				    format(i[36],','),\
				    format(i[23],','),\
				    format(i[24],','),\
				    format(i[25],','),\
				    format(i[37],','),\
				    i[10],\
				    _DTRec,\
				    i[14],\
				    _DTEnt,\
				    i[22],\
				    i[1]+'-'+i[54],\
				    i[43]+'-'+i[44],\
				    i[41],\
				    i[45],\
				    i[39],\
				    i[3],\
				    i[54],\
				    i[98],\
				    i[8],\
				    i[73],\
				    i[15],\
				    romane,\
				    i[112],\
				    nserie,\
				    str( i[113] ),\
				    romaneio_removido
				    
				    _registros +=1
				    indice +=1

			self.clientes = relacao 
			self.registro = _registros
			
			DVListCtrl.itemDataMap   = relacao
			DVListCtrl.itemIndexMap  = relacao.keys()  
			DVListCtrl.filialRemoTo  = self.copiaDav.GetValue().split('-')[0]
			self.ListaDavs.SetItemCount(_registros)
			self.ocorr.SetLabel("Ocorrências\n[ "+str(_registros).zfill(8)+" ]")

			conn.cls(sql[1])
			del _mensagem

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#4D4D4D") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD))		
		dc.DrawRotatedText("DAV(s) - Consulta e Reimpressão", 0, 405, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(1,   470, 795, 28,  3) #-->[ Pesquisa ]
		dc.DrawRoundedRectangle(12,  277, 388, 155, 3) #-->[ Pesquisa ]
		dc.DrawRoundedRectangle(405, 300, 390, 100, 3) #-->[ Consuta ]
		#dc.DrawRoundedRectangle(705, 530, 91, 20, 3) #-->[ Consuta ]

		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		

		
class DVListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}
	filialRemoTo = ""

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
       		
		_clientes = DavConsultar.clientes
		DVListCtrl.itemDataMap  = _clientes
		DVListCtrl.itemIndexMap = _clientes.keys()  
		      
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		self._frame = parent

		self.il = wx.ImageList(16, 16)
		for k,v in diretorios.pasta_icons.items():
			s="self.%s= self.il.Add(wx.Bitmap(%s))" % (k,v)
			exec(s)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		
		self.attr1 = wx.ListItemAttr()
		self.attr2 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour("#E5ECF2")
		self.attr2.SetBackgroundColour("#E4BAC1")

		self.InsertColumn(0, 'Nº D A V',    format=wx.LIST_ALIGN_LEFT,width=140)
		self.InsertColumn(1, 'Emissão',     format=wx.LIST_ALIGN_LEFT,width=80)
		self.InsertColumn(2, 'Filial - Horario', width=120)
		self.InsertColumn(3, 'Descrição dos Clientes', width=310)

		self.InsertColumn(4, 'SubTotal',    format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(5, 'Frete',       format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(6, 'Acrescimo',   format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(7, 'Desconto',    format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(8, 'Total do DAV',format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(9, 'Caixa',       width=160)
		self.InsertColumn(10,'DATA',        width=80)
		self.InsertColumn(11,'Horario',     width=65)
		self.InsertColumn(12,'Entrega',     width=80)
		self.InsertColumn(13,'Horario',     width=80)
		self.InsertColumn(14,'Filial',      width=75)
		self.InsertColumn(15,'Vendedor',    width=160)
		self.InsertColumn(16,'Tipo',        width=40)
		self.InsertColumn(17,'Cancelamento',width=120)
		self.InsertColumn(18,'CPF-CNPJ',    width=120)
		self.InsertColumn(19,'Código do Cliente',    width=120)
		self.InsertColumn(20,'ID-Filial',   width=120)
		self.InsertColumn(21,'1-Simples Faturamento 2-Entrega Futura',   width=300)
		self.InsertColumn(22,'Nº NFe',      width=80)
		self.InsertColumn(23,'Nº Chave NFe',width=400)
		self.InsertColumn(24,'NFe Emissão ',width=300)
		self.InsertColumn(25,'Dados do Romaneio',width=300)
		self.InsertColumn(26,'Vinculado ao orçamento',width=300)
		self.InsertColumn(27,'Serie nota fiscal',width=200)
		self.InsertColumn(28,'Reducao do vinculado',width=200)
		self.InsertColumn(29,'Remocao do DAV do romaneio',width=2000)
		
	def OnGetItemText(self, item, col):

		try:
			
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception as _reTornos:	pass
						
	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		if DVListCtrl.filialRemoTo !="" and item % 2:	return self.attr2
		if DVListCtrl.filialRemoTo !="" and item % 2:	return self.attr1
		return None

	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		genre=self.itemDataMap[index][0]
		orcam=self.itemDataMap[index][16] #->[ Orcamento - Pedido ]
		caixa=self.itemDataMap[index][9] #-->[ Caixa Recebeu ]
		cance=self.itemDataMap[index][17] #->[ Cancelamento ]
		
		if   orcam == "1" and cance !='':	return self.i_idx
		elif orcam == "1" and caixa !='':	return self.w_idx
		elif orcam == "1" and caixa =='':	return self.e_idx
		elif orcam == "2":	return self.i_orc
		else:	return self.w_idx	

	def GetListCtrl(self):	return self
	def GetSortImages(self):	return (self.sm_dn, self.sm_up)


class vendasAgregados(wx.Frame):

	produtos = {}	
	registro = 0
	nrgrupo  = ''
	nmgrupo  = ''
	filialg  = ''
	
	def __init__(self, parent,id):

		self.p = parent
		self.p.Disable()

		mkn = wx.lib.masked.NumCtrl
		self.Trunca = truncagem()
		
		wx.Frame.__init__(self, parent, id, u'DAVs: Consulta de produtos por grupo', size=(800,425), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,id,style=wx.BORDER_SUNKEN)

		self.VendasAgr = AGListCtrl(self.painel, 300, pos=(10,12), size=(788,248),
								style=wx.LC_REPORT
								|wx.LC_VIRTUAL
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.VendasAgr.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.similares)
		self.VendasAgr.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.vender)


		#-----------:[ Produtos Similares ]
		self.ListaSimi = wx.ListCtrl(self.painel, 410,pos=(12,260), size=(785, 120),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaSimi.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.vender)
		self.ListaSimi.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.simila)

		self.ListaSimi.SetBackgroundColour('#D7E3D7')
		self.ListaSimi.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.ListaSimi.InsertColumn(0, 'Preço',                  format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListaSimi.InsertColumn(1, 'Estoque',                format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListaSimi.InsertColumn(2, 'UN',                     width=30)
		self.ListaSimi.InsertColumn(3, 'Descrição dos produtos', width=600)
		self.ListaSimi.InsertColumn(4, 'Código',                 width=120)
		self.ListaSimi.InsertColumn(5, 'Francionar',             width=120)

		wx.StaticText(self.painel,-1,u"Pesquisar [Vinculado ao grupo]: Descrição-Expressão {ClickVazio}", pos=(15, 380)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Ocorrências: ",                      pos=(390,380)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Quantidade",                         pos=(667,383)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Descrição do grupo { sub-grupo }: ", pos=(12,0)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		gs = wx.StaticText(self.painel,-1,'{'+self.nmgrupo[:20]+'}', pos=(185,0))
		gs.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		gs.SetForegroundColour('#2186E9')

		#------:[ Atualiza codigo principal-similar p/vender ]
		self.cdproduto = wx.StaticText(self.painel,-1,u"", pos=(725, 0))
		self.cdproduto.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cdproduto.SetForegroundColour('#690505')

		#---------:[ em que lista estar focado ]
		self.ls = wx.StaticText(self.painel,-1,'',pos=(775,383))
		self.ls.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ls.SetForegroundColour('#4D4D4D')

		self.oc = wx.StaticText(self.painel,-1,'{}',pos=(460,380))
		self.oc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.oc.SetForegroundColour('#4D4D4D')

		procur = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/procurap.png",  wx.BITMAP_TYPE_ANY), pos=(520,385), size=(38,34))				
		voltar = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/voltap.png",    wx.BITMAP_TYPE_ANY), pos=(570,385), size=(38,34))				
		adicio = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/adiciona1.png", wx.BITMAP_TYPE_ANY), pos=(620,385), size=(38,34))				

		self.consultar = wx.TextCtrl(self.painel, 102, value='', pos=(12,393), size=(500,25), style=wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)

		self.quantidad = str(Decimal('1.000'))
		self.quantidad = mkn(self.painel, id = 110, value = self.quantidad, pos=(665,396),size=(127,30),style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 4, fractionWidth = 3, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False)
	
		self.VendasAgr.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ListaSimi.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.consultar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.quantidad.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		
		procur.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		adicio.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.VendasAgr.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ListaSimi.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.consultar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.quantidad.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		procur.Bind (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		voltar.Bind (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		adicio.Bind (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
	
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		procur.Bind(wx.EVT_BUTTON, self.consPesq)
		adicio.Bind(wx.EVT_BUTTON, self.adicionar)
		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.consPesq)
		self.quantidad.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		
		self.selecionar(True)

	def TlNum(self,event):

		TP = self.ls.GetLabel().replace('{','').replace('}','')
		if TP == '':	alertas.dia(self.painel,u"Selecione um produto para vender!!\n"+(' '*80),"DAVs: Alterar quantidade")
		else:

			TelNumeric.decimais = 3
			tel_frame=TelNumeric(parent=self,id=-1)
			tel_frame.Centre()
			tel_frame.Show()

	def Tvalores(self,valor,idfy):

		TP = self.ls.GetLabel().replace('{','').replace('}','')
		if   TP == "P":
			indice = self.VendasAgr.GetFocusedItem()
			fracio = self.VendasAgr.GetItem(indice, 5).GetText()
		
		elif TP == "S":
			indice = self.ListaSimi.GetFocusedItem()
			fracio = self.ListaSimi.GetItem(indice, 5).GetText()
				
			quanTi = self.quantidad.GetValue()

			if fracio == "T" and valor !='' and float(valor).is_integer() == False:
					
				alertas.dia(self.painel,"Não é permitido fração para este produto...\n"+(' '*80),"DAVs: Adicionando Produtos")
				self.quantidad.SetValue("1.000")
				return

			if valor == '':	valor = self.quantidad.GetValue()

			if Decimal(valor) > Decimal('99999.99') or Decimal(valor) == 0:

				valor = self.quantidad.GetValue()
				alertas.dia(self.painel,"Quantidade enviado é incompatível!!","Caixa: Recebimento")
				
			self.quantidad.SetValue(valor)

		
	def simila(self, event):

		ind = self.ListaSimi.GetFocusedItem()
		cod = self.ListaSimi.GetItem(ind, 4).GetText()
		self.cdproduto.SetLabel(cod)
		self.ls.SetLabel('{S}')
		
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 300:	sb.mstatus("  Click duplo para vender",0)
		elif event.GetId() == 410:	sb.mstatus("  Click duplo para vender",0)
		elif event.GetId() == 100:	sb.mstatus("  Procurar-Pesquisar produtos",0)
		elif event.GetId() == 101:	sb.mstatus("  S a i r",0)
		elif event.GetId() == 102:	sb.mstatus("  Pesquisar: Descrição,Expressão { Enter-Click Botão pesquisar com consultar vazio para voltar com a lista padrão}",0)
		elif event.GetId() == 105:	sb.mstatus("  Adicionar item selecionado na lista de compras",0)
		elif event.GetId() == 110:	sb.mstatus("  Entre com a quantidade { Click duplo para abrir teclado numérico }",0)
		
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Consulta de produtos por grupo,sub-grupo",0)
		event.Skip()

		
	def consPesq(self,event):	self.selecionar(False)
	def adicionar(self,event):

		cod = self.cdproduto.GetLabel()
		if cod == '':	alertas.dia(self.painel,u"Selecione um produto para vender!!\n"+(' '*80),"DAVs: Adicionando produtos")
		else:
			
			qtd = str( self.Trunca.trunca(1, self.quantidad.GetValue()) )
			self.p.vendasGrupo(cod,self,qtd,'2')
			self.quantidad.SetValue("1.000")
			
	def vender(self,event):
		
		if   event.GetId() == 300:

			ind = self.VendasAgr.GetFocusedItem()
			cod = self.VendasAgr.GetItem(ind, 0).GetText()
			self.p.vendasGrupo(cod,self,'0.000','1')
			
		elif event.GetId() == 410:

			ind = self.ListaSimi.GetFocusedItem()
			cod = self.ListaSimi.GetItem(ind, 4).GetText()
			self.p.vendasGrupo(cod,self,'0.000','1')

		self.quantidad.SetValue("1.000")
		
	def sair(self,event):
		
		self.p.Enable()
		self.Destroy()
	
	def selecionar(self,_cns):
		
		conn = sqldb()
		sql  = conn.dbc("DAVs, Consulta de Produtos por Grupo", fil = self.filialg, janela = self.painel )
		
		if sql[0] == True:

			psq = "SELECT t1.pd_codi,t1.pd_nome,t1.pd_estf,t1.pd_unid,t1.pd_tpr1,t1.pd_nmgr,t1.pd_simi,t1.pd_sug1,t1.pd_sug2,t1.pd_frac,t2.ef_fisico,t2.ef_virtua FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_nmgr='"+str( self.nmgrupo )+"' ORDER BY t1.pd_nome"
			if self.nrgrupo == "1":	psq = psq.replace("t1.pd_nmgr=","t1.pd_sug1=")
			if self.nrgrupo == "2":	psq = psq.replace("t1.pd_nmgr=","t1.pd_sug2=")
			if self.p.ffilia.GetValue() == True:	psq = psq.replace("=t2.ef_codigo","=t2.ef_codigo and t2.ef_idfili='"+str( self.filialg )+"'")
				
			filtro = self.consultar.GetValue().upper()
			if filtro !="":	psq = psq.replace("WHERE","WHERE t1.pd_nome like '%"+filtro+"%' and")
			pesquisa = sql[2].execute( psq )

			_result = sql[2].fetchall()

			vendasAgregados.produtos = {} 
			vendasAgregados.registro = 0   

			_registros = 0
			relacao = {}
			
			for i in _result:
				
				sim = sb1 = sb2 = ''
				fis = i[10]
				
				if i[6] !=None:	sim = i[6]
				if i[7] !=None:	sb1 = i[7]
				if i[8] !=None:	sb2 = i[8]

				relacao[_registros] = i[0],i[1],str( fis ),i[3],i[4],i[5],sim,sb1,sb2,i[9]
				_registros +=1

			self.VendasAgr.SetItemCount(pesquisa)   
			vendasAgregados.produtos = relacao 
			vendasAgregados.registro = pesquisa
			
			AGListCtrl.itemDataMap   = relacao
			AGListCtrl.itemIndexMap  = relacao.keys()
			self.oc.SetLabel('{ '+str(pesquisa)+' }')

			conn.cls(sql[1])

			self.consultar.SetValue('')
			
	#--------:[ Similares ]

	def similares(self,event):

		#--------:[  Similares ]
		indice = self.VendasAgr.GetFocusedItem()
		self.ListaSimi.DeleteAllItems()
		self.ListaSimi.Refresh()
		
		sim = self.VendasAgr.GetItem(indice, 6).GetText()
		cod = self.VendasAgr.GetItem(indice, 0).GetText()
		self.cdproduto.SetLabel(cod)
		
		self.ls.SetLabel('{P}')
		
		if sim != '':
	
			conn  = sqldb()
			sql   = conn.dbc("Caixa: Vendas de Similares", fil = self.filialg, janela = self.painel )

			if sql[0] == True:
		
				nRegis = 1
				indice = 0
			
				for i in sim.split('\n'):

					lsT = i.split('|')
					prc = esf = '0.00'
					uni = 'UN'

					if lsT[0] !='':
						
						prd = "SELECT pd_tpr1,pd_estf,pd_unid,pd_frac FROM produtos WHERE pd_codi='"+str(lsT[0])+"' and pd_idfi='"+str( self.filialg )+"'"
						achei = sql[2].execute(prd)

						if achei !=0:
							
							prds = sql[2].fetchall()
							prc  = format(prds[0][0],',')
							esf  = format(prds[0][1],',')
							uni  = str(prds[0][2])
							fra  = str(prds[0][3])

					self.ListaSimi.InsertStringItem(indice,prc)
					self.ListaSimi.SetStringItem(indice,1, str(esf))
					self.ListaSimi.SetStringItem(indice,2, uni)
					self.ListaSimi.SetStringItem(indice,3, lsT[1])
					self.ListaSimi.SetStringItem(indice,4, lsT[0])
					self.ListaSimi.SetStringItem(indice,5, fra)
					
					nRegis +=1
					indice +=1

				conn.cls(sql[1])
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#2186E9") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"DAVs, Pesquisa por grupo", 0, 420, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(660,    380,  135,  40, 3) #------>[ Dados da NFE ]

		
class AGListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
       		
		_produtos = vendasAgregados.produtos
		AGListCtrl.itemDataMap  = _produtos
		AGListCtrl.itemIndexMap = _produtos.keys()

		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		self._frame = parent

		self.il = wx.ImageList(16, 16)
		a={"sm_up":"UNDO","sm_dn":"REDO","w_idx":"TICK_MARK","e_idx":"WARNING","i_idx":"ERROR"}
		for k,v in a.items():
			s="self.%s= self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_%s,wx.ART_TOOLBAR,(16,16)))" % (k,v)
			exec(s)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour("#F7E7E7")

		self.InsertColumn(0, u"Código",                     format=wx.LIST_ALIGN_LEFT, width=150)
		self.InsertColumn(1, u"Descrição dos Produtos",     width=420)
		self.InsertColumn(2, u"Fisico",                     format=wx.LIST_ALIGN_LEFT, width=90)
		self.InsertColumn(3, u"UN",                         format=wx.LIST_ALIGN_TOP,  width=30)
		self.InsertColumn(4, u"Preço Venda",                format=wx.LIST_ALIGN_LEFT, width=90)
		self.InsertColumn(5, u"Grupo",                      width=130)
		self.InsertColumn(6, u"Similares",                  width=130)
		self.InsertColumn(7, u"Sub-grupo-1",                width=130)
		self.InsertColumn(8, u"Sub-grupo-2",                width=130)
		self.InsertColumn(9, u"Fracionar",                  width=130)
		
	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception, _reTornos:	pass

	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		if item % 2:
			return self.attr1
			
		else:
			return None

	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		genre=self.itemDataMap[index][2]

		if   float(genre)==0.0:	return self.e_idx
		elif float(genre)> 0.0:	return self.w_idx
		else:	return self.i_idx	

	def GetListCtrl(self):	return self
	def GetSortImages(self):	return (self.sm_dn, self.sm_up)


class confirmeSenhaUsuario(wx.Frame):

	Filial = ""
	
	def __init__(self, parent,id):
	
		self.p = parent
		self.i = id

		wx.Frame.__init__(self, parent, id, 'Senha', size=(170,80), style = wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,-1)

		us = wx.StaticText(self.painel,-1,"Login do Usuario",pos=(3,2))
		us.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		usa = wx.TextCtrl(self.painel,-1,'',pos=(0,15),size=(170,20),style = wx.TE_READONLY)
		usa.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		usa.SetBackgroundColour('#BFBFBF')
		usa.SetForegroundColour('#F3F3F3')
		usa.SetValue( login.usalogin )
		

		sh = wx.StaticText(self.painel,-1,"Confirmação de Senha",pos=(3,45))
		sh.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))	

		self.csh = wx.TextCtrl(self.painel,-1,'',pos=(0,57),size=(170,20),style = wx.TE_PASSWORD|wx.TE_PROCESS_ENTER)
		self.csh.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.csh.SetBackgroundColour('#E5E5E5')
		self.csh.SetForegroundColour('#1C61A4')

		self.csh.Bind(wx.EVT_TEXT_ENTER, self.confirmacao)
		self.csh.SetFocus()

	def confirmacao(self,event):

		avc = False
		if self.csh.GetValue() !="":
			
			conn = sqldb()
			sql  = conn.dbc("Confirmação de Senha", fil = self.Filial, janela = self.painel )
			
			if sql[0] == True:
				
				u = sql[2].execute("SELECT us_senh FROM usuario WHERE us_logi='"+str( login.usalogin )+"'")
				s = sql[2].fetchall()[0][0]
				conn.cls( sql[1] )
				
				if u == 0:	alertas.dia(self.painel,"Usuario não localizado...\n"+(" "*100),"Confirmação de senha")
				if u !=0 and s == self.csh.GetValue():	avc = True
				else:	alertas.dia(self.painel,"Senha não confere...\n"+(" "*100),"Confirmação de senha")
		
		if avc == True:
			
			self.p.comissaoVendas( self.i )
			self.Destroy()
			
		else:	self.Destroy()


class ImporTaDAvs:
	
	def davsImporTa( self, parent, par, _fil, orcame, clCodi, regime, clDocu, clNome, vended, nfe_reducao, usar_orcamento, nota_complementar, chave_complementar ):

		self.p = par
		self.t = truncagem()
		rcTribu = CalcularTributos()

		regimeT=login.filialLT[ _fil ][30].split(';')[11]
		
		conn = sqldb()
		sql  = conn.dbc("DAV(s): Importação", fil = _fil, janela = parent)

		if sql[0] == True:

			if nota_complementar:
			    
			    chave_emitida= chave_referenciada=""
			    nota_jaemitida=""
			    voltar_davs=False
			    achar_dav="SELECT cr_tipo,cr_ndav,cr_chnf,cr_chcp,cr_reca FROM cdavs WHERE cr_cdev='"+orcame+"' and cr_reca!='3'"

			    if orcame[:3]=="DEV":
				
				achar_dav=achar_dav.replace('cdavs','dcdavs')
				achar_dav=achar_dav.replace('cr_cdev','cr_ndav')
				
			    if sql[2].execute(achar_dav):
				
				primeiro_dav=orcame
				
				tipo_dav,dav_original,chave_emitida, chave_referenciada, cancelado=sql[2].fetchone()
				if not chave_referenciada:	chave_referenciada=''
				if not chave_emitida:	chave_emitida=''
				    
				if not chave_referenciada and chave_complementar and dav_original:

				    achar_devolucao="SELECT cr_tipo,cr_ndav,cr_chnf,cr_chcp,cr_reca FROM cdavs WHERE cr_ndav='"+dav_original+"' and cr_reca!='3'"

				    if orcame[:3]=="DEV":

					achar_devolucao=achar_devolucao.replace('cdavs','dcdavs')
					achar_devolucao=achar_dav.replace('cr_cdev','cr_ndav')
				    
				    if sql[2].execute(achar_devolucao):
					
					tipo_dav,dav_original,chave_emitida, chave_referenciada, cancelado=sql[2].fetchone()
					if not chave_referenciada:	chave_referenciada=''
					if not chave_emitida:	chave_emitida=''
					orcame=dav_original

				if chave_referenciada and chave_complementar==chave_referenciada and len(chave_emitida)==44:

				    nota_jaemitida=u"\n\n[ Nota fiscal ja emitida ]\n\nChave de nota referenciada: "+chave_referenciada+"\n"+(' '*10)+"Chave de nota emitida: "+chave_emitida+"\n"
				    voltar_davs=True

				if chave_referenciada and not chave_emitida.strip():

				    nota_jaemitida=u"\n\n[ Nota fiscal referenciada, mais nao emitida ]\n\nChave de nota referenciada: "+chave_referenciada+"\n"+(' '*10)+"Chave de nota emitida: "+chave_emitida+"\n"
				    voltar_davs=True
				    
				if not chave_referenciada and chave_complementar:
				    
				    nota_jaemitida="\n\n[ Nota fiscal nao referenciada no caixa ]\n\nChave de nota referenciada: "+chave_complementar+"\n"+(' '*10)+u"Chave de nota emitida: "+chave_emitida+"\n"+(' '*30)+u"DAV Original: "+dav_original+"\n\nClick OK para continuar\n"

				if voltar_davs:	conn.cls(sql[1])

				alertas.dia(parent,"{ Nota fiscal complementar No.DAV: ["+primeiro_dav+"] }\n\n1-DAV referenciado ja consta na base do caixa"+nota_jaemitida+"\n"+(' '*200),"DAV(s): Nota fiscal complementar")
				if voltar_davs:	return False

			listar_items="SELECT *  FROM idavs WHERE it_ndav='"+str( orcame )+"'"

			""" NF Complementar Devolucao """
			if nota_complementar and orcame[:3]=="DEV":	listar_items=listar_items.replace('idavs','didavs')
			
			ITems   = sql[2].execute(listar_items)
			_result = sql[2].fetchall()

			clEsta = '' #->[ Estado ] 
			clSegu = '' #->[ Seguimento s]

			if sql[2].execute("SELECT cl_estado,cl_revend  FROM clientes WHERE cl_codigo='"+str( clCodi )+"' ") !=0:

				_clr = sql[2].fetchall()
				clEsta = _clr[0][0]
				clSegu = _clr[0][1]

			ired_items = 0
			if nfe_reducao and usar_orcamento:

				ired_items = sql[2].execute("SELECT *  FROM idavs WHERE it_ndav='"+ nfe_reducao +"'")
				ired_resul = sql[2].fetchall()
				
			"""  Adicina na lista para alterar o preco do produto no orcamento  """
			lisTa = []
			rlsTa = [] #-: Regime diferentes
			if self.p.TComa3.GetValue() != True and self.p.TComa4.GetValue() != True and parent.aTualizap.GetValue() == True:

				for r in _result:
					
					if sql[2].execute("SELECT pd_codi,pd_tpr1,pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6,pd_cfis,pd_cfsc, pd_pcfl FROM produtos WHERE pd_codi='"+str( r[5] )+"' ") !=0:
						
						rsl = sql[2].fetchall()[0]

						"""    Precos separado p/filial   """
						if rsl[9] !=None and rsl[9] !="" and rcTribu.retornaPrecos( r[48], rsl[9], Tipo = 1 )[0] == True:
							
							rTn,p1,p2,p3,p4,p5,p6 = rcTribu.retornaPrecos( r[48], rsl[9], Tipo = 1 )
							lisTa.append(str(rsl[0])+'|'+str(p1)+'|'+str(p2)+'|'+str(p3)+'|'+str(p4)+'|'+str(p5)+'|'+str(p6)+'|'+str(rsl[7])+'|'+str(rsl[8]) )

						else:	lisTa.append(str(rsl[0])+'|'+str(rsl[1])+'|'+str(rsl[2])+'|'+str(rsl[3])+'|'+str(rsl[4])+'|'+str(rsl[5])+'|'+str(rsl[6])+'|'+str(rsl[7])+'|'+str(rsl[8]) )

			if regime !="":

				for rg in _result:
					
					if sql[2].execute("SELECT pd_codi,pd_tpr1,pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6,pd_cfis,pd_cfsc, pd_pcfl FROM produtos WHERE pd_codi='"+str( rg[5] )+"' ") !=0:
						
						rsl = sql[2].fetchall()[0]
						
						"""    Precos separado p/filial   """
						if rsl[9] !=None and rsl[9] !="" and rcTribu.retornaPrecos( rg[48], rsl[9], Tipo = 1 )[0] == True:
							
							rTn,p1,p2,p3,p4,p5,p6 = rcTribu.retornaPrecos( rg[48], rsl[9], Tipo = 1 )
							lisTa.append(str(rsl[0])+'|'+str(p1)+'|'+str(p2)+'|'+str(p3)+'|'+str(p4)+'|'+str(p5)+'|'+str(p6)+'|'+str(rsl[7])+'|'+str(rsl[8]) )
						
						else:	rlsTa.append( str(rsl[0])+'|'+str(rsl[1])+'|'+str(rsl[2])+'|'+str(rsl[3])+'|'+str(rsl[4])+'|'+str(rsl[5])+'|'+str(rsl[6])+'|'+str(rsl[7])+'|'+str(rsl[8]) )

			
			"""  Se for recalculo do dav pelo caixa  e se for atualizar o codigo fiscal   """
			atualizaCodigoFiscal = False
			if parent.atualCFis.GetValue() or nota_complementar:

				atualizaCodigoFiscal = True
				for rg in _result:
					
					if sql[2].execute("SELECT pd_codi,pd_tpr1,pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6,pd_cfis,pd_cfsc, pd_pcfl FROM produtos WHERE pd_codi='"+str( rg[5] )+"' ") !=0:
						
						rsl = sql[2].fetchall()[0]
						rlsTa.append( str(rsl[0])+'|'+str(rsl[1])+'|'+str(rsl[2])+'|'+str(rsl[3])+'|'+str(rsl[4])+'|'+str(rsl[5])+'|'+str(rsl[6])+'|'+str(rsl[7])+'|'+str(rsl[8]) )		

			conn.cls(sql[1])

			if ITems == 0 and self.p.TComa3.GetValue() !=True and self.p.TComa4.GetValue() !=True:	alertas.dia(parent,"DAV não localizado...\n"+(' '*70),"DAV(s): Importação de Orçamentos")	
			if ITems == 0 and self.p.TComa3.GetValue() ==True:	alertas.dia(parent,"Devolução não localizada...\n"+(' '*70),"DAV(s): Devolução")	
			if ITems == 0 and self.p.TComa4.GetValue() ==True:	alertas.dia(parent,"Simples faturamento não localizado...\n"+(' '*70),"DAV(s): Simples Faturamento")	

			if ITems !=0:

				""" Atualiza o cliente p/venda,ajusta obj
					Desconto e Acrescimo apenas para devolucao
				"""
				__dsp = __acr = __frT = ""

				__val = Decimal( parent.suToT.GetValue().replace(',','') )
				if Decimal( parent.Desco.GetValue().replace(',','') ) or Decimal( parent.ajdesco.GetValue() ):

					__des = Decimal( parent.Desco.GetValue().replace(',','') )
					if parent.ajdesco.GetValue():	__des +=Decimal( parent.ajdesco.GetValue() )
					
					__dsp = ( __des / __val * 100 )

				passa_acrescimo = True
				if not parent.devolacre.GetValue():	passa_acrescimo = False
				if passa_acrescimo and Decimal( parent.Acres.GetValue().replace(',','') ) > 0:

					__acs = Decimal( parent.Acres.GetValue().replace(',','') )
					__acr = ( __acs / __val * 100 )

				if parent.devolufrt.GetValue() == True and Decimal( parent.Frete.GetValue().replace(',','') ) > 0:

					__fre = Decimal( parent.Frete.GetValue().replace(',','') ) if not Decimal( parent.frete_manual.GetValue() ) else Decimal( parent.frete_manual.GetValue() )
					__frT = ( __fre / __val * 100 )
					self.p.devolucaofrete = True

				self.p.AtualizaClientes( clCodi, clDocu, clNome, clSegu, clEsta )
				self.p.dclientes('','','') 

				if self.p.TComa3.GetValue() == True or self.p.TComa4.GetValue() == True:	self.p.dclientes( str( __dsp ), str( __acr ), str( __frT ) )
				if self.p.TComa3.GetValue() == True or self.p.TComa4.GetValue() == True:	self.p.ddevol = str( orcame )+"|"+_fil+"|"+vended

				if self.p.TComa3.GetValue() != True and self.p.TComa4.GetValue() != True:

					self.p.TComa2.SetValue(True)
					self.p.abilitar(2)
					self.p.evradio(wx.EVT_BUTTON)

				"""  Verifica se o aproveitamento tem produtos com filiais diferentes  """
				if not self.p.TComa3.GetValue() and not parent.aproveita.GetValue():

					___filial = _result[0][48]
					varias_filiais = False

					for rf in _result:
						
						if rf[48] != ___filial:	varias_filiais = True
						
					if varias_filiais:
						
						parent.aproveita.Enable( True )
						alertas.dia( parent, u"{ Aproveitamento de davs, com produtos de filiais diferentes }\n\n1 - Marque a opção de aproveita de dav com produtos de filiais diferentes\n2 - Refaça o processo de finalização\n"+(" "*160),"Aproveita de davs")
						return

				self.p.ajustarDav()
				items_adicionados=0

				"""  Nota fiscal complementer  """
				self.p.frete_proporcional = Decimal("0.00")
				self.p.acres_proporcional = Decimal("0.00")
				self.p.desco_proporcional = Decimal("0.00")
				
				for i in _result:

					_kitcon    = ""
					_iTeFil    = str( i[48] )

					codigo     = str( i[5] )
					produto    = str( i[7] )
					quantidade = nF.eliminaZeros(str( i[12] ))
					unidade    = str( i[8] )
					preco      = str( self.t.trunca(1,i[11]) )
					pcuni      = str( self.t.trunca(5,i[14]) )
					if login.filialLT[_iTeFil][19]=="2":	preco = str( self.t.trunca(3,i[11]) )
					clcom      = str( i[15] )
					cllar      = str( i[16] )
					clexp      = str( i[17] )
					clmet      = str( i[18] )
					ctcom      = str( i[19] )
					ctlar      = str( i[20] )
					ctexp      = str( i[21] )
					ctmet      = str( i[22] )
					sbToTal    = str( i[13] )
					UniPeca    = str( i[23] )
					mControle  = str( i[24] )
					mCorte     = str( i[25] )
					cEcf       = str( i[44] )

					_ippt      = str( i[60] )
					_fabr      = str( i[9] )
					_ende      = str( i[10] )
					_cbar      = str( i[6] )
					_cf        = str( i[59] )
					_tabela    = str( i[75] )
					_cusToU    = str( i[77] )
					_cusToT    = str( i[78] )
					_devolu    = ""
					_vlManu    = str( i[89] )
					_kitqTv    = str( i[92] ) #-: QT vendida do KIT
					es_local  = str( i[101] ) if self.p.TComa3.GetValue() else "0"
					quantidade_entrega_avulso = i[64]

					""" Validar subtotal { Verifica se os subtotais batem }"""
					#if login.filialLT[ _iTeFil ][19]=="2":	precop = Trunca.trunca(3, ( valorp + ( valorp * margem / 100 ) ) ) 2
					#if login.filialLT[ _iTeFil ][19]!="2":	precop = Trunca.trunca(1, ( valorp + ( valorp * margem / 100 ) ) ) 3
					sub_total_produto = ( Decimal(preco) * i[12] )
					if i[13] !=sub_total_produto:	sbToTal = nF.eliminaZeros(str(self.t.trunca(3,sub_total_produto)))

					self.p.frete_proporcional +=i[26]
					self.p.acres_proporcional +=i[27]
					self.p.desco_proporcional +=i[28]

					"""  Extrai o numero de series da devolucao  """
					codIden    = "" if not i[95] or ":" not in i[95].split("|")[0] else str( i[95].split('|')[0].split(':')[1].strip() ) #-: Codigo avulso de identificacao do item
					qunipecdev = str( i[96] ) #-: QT em unidade de peca devolvida

					"""  Reducao do preco do produto   """
					recalcular_orcamento = False
					if parent.vinculnfe.GetValue() and parent.reducao.GetValue() and self.p.TComa2.GetValue():	recalcular_orcamento, preco = True, str( self.t.trunca( 1, Decimal( preco ) * ( Decimal( parent.reducao.GetValue() ) / 100 )  ) )
					if parent.vinculnfe.GetValue() and parent.reducao.GetValue() and self.p.TComa2.GetValue():
						
						self.p.vincularemNFe = True
						self.p.vincularprNFe = Decimal( parent.reducao.GetValue() )

					if i[91] !=None and i[91] !="":	_kitcon = str( i[91] )

					"""  Devolucao com reducao valores na emissao da nfe  """
					if self.p.TComa3.GetValue() and nfe_reducao and ired_items and usar_orcamento:
						
					    for rd in ired_resul:

						if rd[0] == i[0]:

						    preco = str( self.t.trunca(1,rd[11]) )
						    pcuni = str( self.t.trunca(5,rd[14]) )
						    sbToTal = str( rd[13] )
						    UniPeca = str( rd[23] )
					
					_SalDev    = _qTd = _qOr = iditems = _qTpcDv = ""

					iditems = str( i[0] )
					if self.p.TComa3.GetValue() == True or self.p.TComa4.GetValue() == True:

						""" Guarda dados da devolucao p/Retorno da quantidade quando do cancelamento { ID-Item, NºDav,Codigo do Produto }"""
						_devolu = str(i[0])+"|"+str(i[2])+"|"+str(i[5])

						_qTd    = str( i[66] )
						_qOr    = str( i[12] )

						"""   Para manter a compatibilidade com pedidos q ja foram devolvidos anterirormente a esse ajustes 27-2-2015   """
						#if i[96] == 0 and i[66] !=0:	_SalDev = UniPeca = quantidade = str( Decimal( quantidade ) - Decimal( _qTd ) - quantidade_entrega_avulso )
						if i[96] == 0 and i[66] !=0:	_SalDev = UniPeca = quantidade = str( Decimal( quantidade ) - Decimal( _qTd ) )
						else:
						
							"""   Nova Forma de Devolucao de { na madeiras fica po qt peca e unidade fica norma } ajustes 27-2-2015   """
							UniPeca = str( Decimal( UniPeca ) - Decimal( qunipecdev ) )
							#_SalDev = quantidade = str( Decimal( quantidade ) - Decimal( _qTd ) - quantidade_entrega_avulso )
							_SalDev = quantidade = str( Decimal( quantidade ) - Decimal( _qTd ) )

						sbToTal = str( self.t.trunca(3, ( Decimal(quantidade) * Decimal(preco) ) ) )
						pcuni   = str( self.t.trunca(5,i[11]) )

					"""   Muda o codigo fiscal se a filial  for regimes diferentes   """

					if regime !="" or atualizaCodigoFiscal == True:

						for cff in rlsTa:

							"""  Altera se for pegar o pedido de outra filial  """
							if regime == "1" and codigo == cff.split('|')[0]:	_cf = cff.split('|')[7] if cff.split('|')[7] else cff.split('|')[8]
							#if regime == "3" and codigo == cff.split('|')[0]:	_cf = cff.split('|')[8] if cff.split('|')[8] else cff.split('|')[7]
							if regime in ["2","3"] and codigo == cff.split('|')[0]:	_cf = cff.split('|')[8] if cff.split('|')[8] else cff.split('|')[7]

							"""  Se recalcuar dav pelo caixa  """
							if atualizaCodigoFiscal == True and regimeT == "1" and codigo == cff.split('|')[0]:	_cf = cff.split('|')[7] if cff.split('|')[7] else cff.split('|')[8]
							#if atualizaCodigoFiscal == True and regimeT == "3" and codigo == cff.split('|')[0]:	_cf = cff.split('|')[8] if cff.split('|')[8] else cff.split('|')[7]
							if atualizaCodigoFiscal == True and regimeT in ["2","3"] and codigo == cff.split('|')[0]:	_cf = cff.split('|')[8] if cff.split('|')[8] else cff.split('|')[7]

					"""   Atualiza o preco do produto   """
					if self.p.TComa2.GetValue() == True and parent.aTualizap.GetValue() == True and lisTa !=[]:

						recalcular_orcamento = True
						for ap in lisTa:
							
							if codigo == ap.split('|')[0]:

								if  _tabela == "1":	preco = str( ap.split('|')[1] )
								if  _tabela == "2":	preco = str( ap.split('|')[2] )
								if  _tabela == "3":	preco = str( ap.split('|')[3] )
								if  _tabela == "4":	preco = str( ap.split('|')[4] )
								if  _tabela == "5":	preco = str( ap.split('|')[5] )
								if  _tabela == "6":	preco = str( ap.split('|')[6] )
								
								if Decimal( preco ) == 0:	preco = str( ap.split('|')[1] )

						"""  Reducao do preco do produto   """
						if parent.vinculnfe.GetValue() and parent.reducao.GetValue() and self.p.TComa2.GetValue():	recalcular_orcamento, preco = True, str( self.t.trunca( 1, Decimal( preco ) * ( Decimal( parent.reducao.GetValue() ) / 100 ) ) )

					#// Precos configurados para 2 casas decimais
					if len( login.filialLT[ _iTeFil ][35].split(";") ) >=66 and login.filialLT[ _iTeFil ][35].split(";")[65] == "T":	preco = format( Decimal( preco ) , '.2f' )

					if recalcular_orcamento:
						
						_qTd    = str( i[66] )
						_SalDev = quantidade = str( Decimal( quantidade ) - Decimal( _qTd ) )
						sbToTal = str( self.t.trunca(3, ( Decimal(quantidade) * Decimal(preco) ) ) )
						pcuni   = str( self.t.trunca(5,i[11]) )

					""" Ajuste para utilizar o orcamento para emitir uma nota fiscal complmentar """
					avancar_item=True
					if nota_complementar:
					    
					    avancar_item=True if len( _cf.split('.') )>=4 and _cf.split('.')[2] and _cf.split('.')[2][:1] in ['1','0'] and  _cf.split('.')[2][1:]=='000' and _cf.split('.')[3] and int(_cf.split('.')[3]) else False
					    
					if avancar_item:
					    
					    self.p.adicionarItem( codigo, produto, quantidade, unidade, preco, pcuni, clcom, cllar, clexp, clmet, ctcom, ctlar, ctexp, ctmet, sbToTal, UniPeca,\
					    mControle, mCorte, cEcf, _ippt, _fabr, _ende, _cbar, _cf, True, iditems, _qTd, _qOr, _SalDev, True, _tabela, _cusToU, _cusToT, _devolu, importacao = True,\
					    valorManual = _vlManu, auTorizacacao = False, moTAuT = "", kiTp = _kitcon, kiTv = _kitqTv, aTualizaPreco = parent.aTualizap.GetValue(), codigoAvulso = codIden,\
					    FilialITem = _iTeFil, per_desconto = "0.00", vlr_desconto = "0.00", vinculado = orcame, estoque_local = es_local, produto_servico='' )
					    items_adicionados+=1
					
					self.p.ndev.SetLabel( "Vincular: "+str( orcame ) )
			
				self.p.CaixaRecFrete = Decimal( parent.Frete.GetValue().replace(',','') )
				self.p.CaixaRecAcres = Decimal( parent.Acres.GetValue().replace(',','') )
				self.p.CaixaRecDesco = Decimal( parent.Desco.GetValue().replace(',','') )
				
				if nota_complementar and not items_adicionados:

				    alertas.dia( parent, u"{ Orçamento para emissão da NOTA FISCAL COMPLEMENTAR p/Ajuste do ICMS, vinculado ao DAV Selecionado }\n\n1-Não existe nenhum produto com ICMS para DESTACAR na emissão da nota fiscal\n"+(" "*230),"Aproveita de davs")				    
				    
				    return False
				    
				else:	return True
				
			else:	return False
			

"""   Calculo Separa do TribuTo   """
class CalcularTributos:

	def reCalcularTribuTos(self, parent, Temporario, addTemp, davaV, reducao ):
				
		if davaV != 'V':	return
		self.p = parent
		Trunca = truncagem()

		self.icmsdv     = 'F' #->[ imcs D->por Dentro F->por Fora ]
		self.icmsiA     = 'S' #->[ Adicionar Acrescimos na Base de Calculo ICMS ]
		self.icmsiF     = 'S' #->[ Adicionar Frete na Base de Calculo ICMS ]
		self.icmsiD     = 'S' #->[ Descontar Desconto na Base de Calculo do ICMS ]

		self.STiA       = 'S' #->[ Adicinoar Acrescimo na Base de Calculo da ST ]
		self.STiF       = 'N' #->[ Adicionar Frete na Base de Calculo da ST ]
		self.STiD       = 'N' #->[ Descontar Desconto na Base de Calculo da ST ]

		self.ToTalGeral = Decimal('0.00')
		valorRateioDesc = Decimal('0.00')
		valorRateio     = Decimal('0.00')

		percAcrescimos  = Decimal('0.00')
		percDescontos   = Decimal('0.00')
		percFrete       = Decimal('0.00')
		
		"""
			Partilha do ICMS
		"""
		aliqDesti       = Decimal('0.00') #---: Aliquota do Destini
		aliqInter       = Decimal('0.00') #---: Aliquota InterEstadual
		aliqFundP       = Decimal('0.00') #---: Aliquota do funda da pobreza
		
		percDifal       = Decimal('0.00') #---: Diferenca de aliquota  
		peICMOrig		= Decimal('0.00') #---: Percentual-Q Fica na origem
		peICMDesT       = Decimal('100.00') #-: Percentual-Q Fica no destino

		vlICMOrig       = Decimal('0.00') #---: Valor-Q Fica na origem
		vlICMDesT       = Decimal('0.00') #---: Valor-Q Fica no destino
		valFundoProb    = Decimal('0.00') #---: Fundo da Pobreza

		valTICMSParTo   = Decimal('0.00') #---: Valor Total do ICMS Partilha origem
		valTICMSParTd   = Decimal('0.00') #---: Valor Total do ICMS Partilha destino

		"""  ATualiza Percentuais origem, destino  """
		anoATual = datetime.datetime.now().strftime("%Y")
		if anoATual in login.parICMSE:	peICMOrig, peICMDesT = Decimal(login.parICMSE[anoATual][0]),Decimal(login.parICMSE[anoATual][1])

		ValorTIcms      = Decimal('0.00')
		ValorTRIcm      = Decimal('0.00')
		ValorTSBT       = Decimal('0.00')
		ValorTIPI       = Decimal('0.00')
		ValorTISS       = Decimal('0.00')

		valorSubTotal   = Decimal('0.00')
		valorTotal      = Decimal('0.00')
		valorDesconto   = Decimal('0.00')
		valorFrete      = Decimal('0.00')
		valorAcrescimo  = Decimal('0.00')

		IBPTValorP		= Decimal('0.00')
		MediaIBPT       = Decimal('0.00')
		
		vTIPI = Decimal('0.00')
		vTCOF = Decimal('0.00')
		
		FRToTal = Decimal('0.00')
		ACToTal = Decimal('0.00')
		DCToTal = Decimal('0.00')
		
		vFNibpT= vFIibpT= vESibpT= vMUibpT= Decimal("0.00")

		_frete = self.p.sTF.GetValue()		
		_acres = self.p.sTA.GetValue()
		_desco = self.p.sTD.GetValue()
		
		if self.p.parICMSp.GetValue() !="" and len( self.p.parICMSp.GetValue().split('-') ) == 3:	aliqDesti = Decimal( self.p.parICMSp.GetValue().split('-')[0].split("%")[0] )
		if self.p.parICMSp.GetValue() !="" and len( self.p.parICMSp.GetValue().split('-') ) == 3:	aliqInter = Decimal( self.p.parICMSp.GetValue().split('-')[1].split("%")[0] )
		if self.p.parICMSp.GetValue() !="" and len( self.p.parICMSp.GetValue().split('-') ) == 3:	percDifal = Decimal( self.p.parICMSp.GetValue().split('-')[2].split("%")[0] )
		
		indice = 0
		rindic = 0
		aindic = 0
		ordems = 1
		itens  = self.p.ListaPro.GetItemCount()

		""" Elimina todos os itens do arquivo temporario """
		if Temporario == True and addTemp == True:

			elimin = "DELETE FROM tdavs WHERE tm_cont='"+str( self.p.TempDav.GetLabel() )+"'"
			self.p.sql[2].execute( elimin )
			
		if itens > 0:

			""" Totaliza Frete,Acrescimo,Desconto para rateio """
			for raTeio in range( itens ):

				#// Totaliza para descontos apenas os produtos que nao tem marcarcacao para negar descontos
				if self.p.TComa3.GetValue():	valorRateioDesc += Decimal( self.p.ListaPro.GetItem(rindic, 6).GetText() )
				else:
					if self.p.ListaPro.GetItem(rindic, 93).GetText() !='T':	valorRateioDesc += Decimal( self.p.ListaPro.GetItem(rindic, 6).GetText() )
		
				valorRateio += Decimal( self.p.ListaPro.GetItem(rindic, 6).GetText() )
				rindic +=1

			valorAcrescimo = Trunca.trunca(3, Decimal( str(self.p.sTA.GetValue()).replace(',','') ) ) 
			valorDesconto  = Trunca.trunca(3, Decimal( str(self.p.sTD.GetValue()).replace(',','') ) )
			valorFrete     = Trunca.trunca(3, Decimal( str(self.p.sTF.GetValue()).replace(',','') ) )

			#// Tem produtos q nao tem descontos entao nao pode entrar no rateio do desconto
			if valorRateioDesc > 0 and valorDesconto  > 0:	percDescontos  = Trunca.arredonda(3, ( valorDesconto  / valorRateioDesc * 100 ) )

			if valorRateio > 0 and valorAcrescimo > 0:	percAcrescimos = Trunca.arredonda(3, ( valorAcrescimo / valorRateio * 100 ) ) 
			if valorRateio > 0 and valorFrete     > 0:	percFrete      = Trunca.arredonda(3, ( valorFrete     / valorRateio * 100 ) )

			""" Totaliza Rateio p/Acrescimo,Desconto,Frete p/Nao dar diferenca na Totalizacao da Nota  """
			for acdc in range( itens ):
				
				pvAcrescimo = Decimal('0.00')
				pvDesconto  = Decimal('0.00')
				pvFrete     = Decimal('0.00')

				adSubToTal = Decimal( self.p.ListaPro.GetItem(aindic, 6).GetText() )

				if valorFrete > 0 and percFrete > 0:
						
					pvFrete = Trunca.arredonda(2, ( adSubToTal * percFrete / 100 ) )
					FRToTal +=pvFrete

				if valorAcrescimo > 0 and percAcrescimos > 0:

					pvAcrescimo = Trunca.arredonda(2, ( adSubToTal * percAcrescimos / 100 ) )
					ACToTal +=pvAcrescimo

				if self.p.ListaPro.GetItem(aindic, 93).GetText() !='T' and valorDesconto > 0 and percDescontos > 0:

					pvDesconto = Trunca.arredonda(2, ( adSubToTal * percDescontos / 100 ) )
					DCToTal +=pvDesconto

				self.p.ListaPro.SetStringItem(aindic,19, str(percFrete) )			
				self.p.ListaPro.SetStringItem(aindic,20, str(percAcrescimos) )			
				self.p.ListaPro.SetStringItem(aindic,21, str(percDescontos) )			

				self.p.ListaPro.SetStringItem(aindic,22, str(pvFrete) )			
				self.p.ListaPro.SetStringItem(aindic,23, str(pvAcrescimo) )			
				self.p.ListaPro.SetStringItem(aindic,24, str(pvDesconto) )			
				aindic +=1

			"""  Ajuste de Valores de Rateio de Frete,Acrescimo,Desconto p/Nao da Rejeicao  na Nota """
			if FRToTal   > valorFrete:	self.p.ListaPro.SetStringItem(0,22, str(( Decimal(self.p.ListaPro.GetItem(0, 22).GetText()) - ( FRToTal - valorFrete ) )) )
			elif FRToTal < valorFrete:	self.p.ListaPro.SetStringItem(0,22, str(( Decimal(self.p.ListaPro.GetItem(0, 22).GetText()) + ( valorFrete - FRToTal ) )) )

			if ACToTal   > valorAcrescimo:	self.p.ListaPro.SetStringItem(0,23, str(( Decimal(self.p.ListaPro.GetItem(0, 23).GetText()) - ( ACToTal - valorAcrescimo ) )) )
			elif ACToTal < valorAcrescimo:	self.p.ListaPro.SetStringItem(0,23, str(( Decimal(self.p.ListaPro.GetItem(0, 23).GetText()) + ( valorAcrescimo - ACToTal ) )) )
			
			"""
			  Verifica o produto q pode receber o ajuste de desconto 
			  degrau 04-04-2018 o item 0 estava marcado para nao permitir desconto, como houve um sobra de 0,01 o sistema debitou do primeiro item como o primeiro item
			  nao permitia desconto o desconto ficou com -0,01  na emissao da nota deu erro de SCHEMA
			"""
			if valorDesconto:

				for indice_desconto in range( itens ):
					
					___st = Decimal( self.p.ListaPro.GetItem( indice_desconto,  6).GetText().replace(',', '') ) if self.p.ListaPro.GetItem( indice_desconto,  6 ).GetText() else Decimal("0.00")
					___vd = Decimal( self.p.ListaPro.GetItem( indice_desconto, 24).GetText().replace(',', '') ) if self.p.ListaPro.GetItem( indice_desconto, 24 ).GetText() else Decimal("0.00")
					
					if ___st and ___vd:

						if DCToTal   > valorDesconto:	self.p.ListaPro.SetStringItem( indice_desconto ,24, str(( Decimal(self.p.ListaPro.GetItem( indice_desconto, 24 ).GetText() ) - ( DCToTal - valorDesconto ) ) ) )
						elif DCToTal < valorDesconto:	self.p.ListaPro.SetStringItem( indice_desconto ,24, str(( Decimal(self.p.ListaPro.GetItem( indice_desconto, 24 ).GetText() ) + ( valorDesconto - DCToTal ) ) ) )
						break
			
			""" Recalcula Valores e Tributos """
			for i in range(itens):

				self.p.ListaPro.SetStringItem(indice,0,  str(ordems).zfill(3) )

				codigo = self.p.ListaPro.GetItem(indice, 1).GetText()
				descri = self.p.ListaPro.GetItem(indice, 2).GetText()
				quanti = self.p.ListaPro.GetItem(indice, 3).GetText()
				unidad = self.p.ListaPro.GetItem(indice, 4).GetText()
				contro = self.p.ListaPro.GetItem(indice,17).GetText()
				metrag = self.p.ListaPro.GetItem(indice,15).GetText()
				dTaEmi = self.p.ListaPro.GetItem(indice,51).GetText()
				HraEmi = self.p.ListaPro.GetItem(indice,52).GetText()
				FiliIT = self.p.ListaPro.GetItem(indice,69).GetText()
				
				icms  = Decimal(self.p.ListaPro.GetItem(indice, 25).GetText())
				ricm  = Decimal(self.p.ListaPro.GetItem(indice, 26).GetText())
				ipi   = Decimal(self.p.ListaPro.GetItem(indice, 27).GetText() )
				STIVA = Decimal(self.p.ListaPro.GetItem(indice, 28).GetText() )
				ibptp = Decimal(self.p.ListaPro.GetItem(indice, 48).GetText() )
				cst   = self.p.ListaPro.GetItem(indice, 47).GetText()
				dIBPT = self.p.ListaPro.GetItem(indice, 77).GetText() #--: Dados p/Calculo do IBPT Federal,Estadua,Municipal
				aliqFundP = self.p.ListaPro.GetItem(indice, 96).GetText() #--// Aliquota fundo de pobreza

				"""
					Troca da liquota do icms
					aliqInter
				"""
				if aliqInter !=None and aliqInter !="" and Decimal( aliqInter ) !=0 and icms !=0:	icms = Decimal( aliqInter )

				pcPIS = Decimal( self.p.ListaPro.GetItem(indice, 80).GetText() )
				pcCOF = Decimal( self.p.ListaPro.GetItem(indice, 81).GetText() )

				CoeficieIcms = Decimal('0.00')
				BaseCalcIcms = Decimal('0.00')
				ValorIcms    = Decimal('0.00')

				CoefReducao  = Decimal('0.00')
				BaseReducao  = Decimal('0.00')
				ValorReducao = Decimal('0.00')
		
				STBaseCalculo= Decimal('0.00')
				valorST      = Decimal('0.00')
		
				IPBaseCalculo= Decimal('0.00')
				valorIPI     = Decimal('0.00')

				ISBaseCalculo= Decimal('0.00')
				valorISS     = Decimal('0.00')
				vIBPT        = Decimal('0.00')

				PISBCalculo  = Decimal('0.00')
				valorPIS     = Decimal('0.00')

				COFBCalculo  = Decimal('0.00')
				valorCOF     = Decimal('0.00')
				
				suBToTal = self.p.ListaPro.GetItem(indice, 6).GetText()

				if Decimal( pcPIS ) !=0:

					PISBCalculo = Decimal( suBToTal )
					valorPIS    = str( Trunca.arredonda(2, ( PISBCalculo * Decimal( pcPIS ) /100 ) ) )
					
					vTIPI +=Decimal( valorPIS )
					
				if Decimal( pcCOF ) !=0:

					COFBCalculo = Decimal( suBToTal )
					valorCOF    = str( Trunca.arredonda(2, ( COFBCalculo * Decimal( pcCOF ) / 100 ) ) )
					
					vTCOF +=Decimal( valorCOF )
				
				vlFrete  = Decimal( self.p.ListaPro.GetItem(indice, 22).GetText() )
				vlAcres  = Decimal( self.p.ListaPro.GetItem(indice, 23).GetText() )
				vlDesco  = Decimal( self.p.ListaPro.GetItem(indice, 24).GetText() )

				"""  Nao adiciona o frete na base de calculo da nfe quando o sistema estiver configurado p/nao retear o frete  """
				if len( login.filialLT[ self.p.ListaPro.GetItem(indice, 69).GetText() ][35].split(';') ) >= 64 and login.filialLT[ self.p.ListaPro.GetItem(indice, 69).GetText() ][35].split(';')[63] == 'T':	self.icmsiF = "N"

				vlsAcres = (  vlFrete + vlAcres )

				if ipi > 0:

					IPBaseCalculo = Decimal(suBToTal)
					valorIPI      = Trunca.trunca(3, ( IPBaseCalculo * ipi / 100 ) )

				"""  Partilha do ICMS  """
				infParTilha = "" #------: Informacoe dos dados de partilha 
				if Decimal(icms) > 0 or percDifal > 0: #-: Calculo do ICMS por Fora ]

					CoeficieIcms    = ( Decimal(icms) / 100 )
					CodficienFCP    = ( Decimal( aliqFundP) / 100 ) if Decimal( aliqFundP ) else '0.00' #--// Coenficiente do pFCP
					BaseCalcIcms    = ( Decimal(suBToTal) + valorIPI )
					ImpostoNormal   = Trunca.arredonda(2, ( Decimal(suBToTal) * CoeficieIcms ) )
					
					if self.icmsiA == 'S':	BaseCalcIcms =  ( BaseCalcIcms + vlAcres )
					if self.icmsiF == 'S':	BaseCalcIcms =  ( BaseCalcIcms + vlFrete )
					if self.icmsiD == 'S':	BaseCalcIcms =  ( BaseCalcIcms - vlDesco  )
					
					ValorIcms       = Trunca.trunca(3, ( BaseCalcIcms * CoeficieIcms ) ) #--// Calculo do icms
					valFundoProb    = Trunca.trunca(3, ( BaseCalcIcms * CodficienFCP ) ) if Decimal( aliqFundP ) else '0.00' #--// Calculo do FCP

					"""  ParTilha ICMS  """
					if percDifal > 0:
							
						valICMSParT = Trunca.trunca(3, ( BaseCalcIcms * percDifal / 100 ) ) 

						if peICMOrig > 0:	vlICMOrig = Trunca.trunca(3, ( valICMSParT * peICMOrig / 100 ) ) 
						vlICMDesT   = ( valICMSParT -vlICMOrig )

						""" Se o objeto imcs for 0 e pq o e ST, entao sendo interestadual o sistema calcula apenas a partilha
							InterEstadual ST Zera Informacoes do ICMS Permancecer apenas os dados de partilha
						"""
						if Decimal( icms ) == 0:	vlICMOrig = vlICMDesT = Decimal("0.00")

						valTICMSParTo +=vlICMOrig
						valTICMSParTd +=vlICMDesT
							
						infParTilha = str( BaseCalcIcms )+";"+str( aliqFundP )+";"+str( aliqDesti )+";"+str( aliqInter )+";"+str( peICMDesT )+";"+str( valFundoProb )+";"+str( vlICMDesT )+";"+str( vlICMOrig )

						""" Se o objeto imcs for 0 e pq o e ST entao sendo interestadual o sistema calcula apenas a partulha
							InterEstadual ST Zera Informacoes do ICMS Permancecer apenas os dados de partilha
						"""
						if Decimal( icms ) == 0:	CoeficieIcms = BaseCalcIcms = ImpostoNormal = ValorIcms = Decimal('0.00')
					
					if self.icmsdv == "D": #-->[ Calcula o ICMS por Dentro ]

						CoeficieIcms   = ( 1 - ( Decimal(icms) / 100 ) )
						BaseCalcIcms   = Trunca.arredonda(2, ( Decimal(suBToTal) / CoeficieIcms ) )
						BaseCalcIcms    = ( BaseCalcIcms + valorIPI )

						if self.icmsiA == 'S':	BaseCalcIcms =  ( BaseCalcIcms + vlAcres )
						if self.icmsiF == 'S':	BaseCalcIcms =  ( BaseCalcIcms + vlFrete )
						if self.icmsiD == 'S':	BaseCalcIcms =  ( BaseCalcIcms - vlDesco  )
						ValorIcms    = Trunca.trunca(3, ( BaseCalcIcms * ( Decimal(icms) / 100 ) ) )
						valFundoProb = Trunca.trunca(3, ( BaseCalcIcms * CodficienFCP ) ) if Decimal( aliqFundP ) else '0.00' #--// Calculo do FCP

						"""  ParTilha ICMS  """
						if percDifal > 0:
								
							valICMSParT = Trunca.trunca(3, ( BaseCalcIcms * percDifal / 100 ) ) 

							if peICMOrig > 0:	vlICMOrig   = Trunca.trunca(3, ( valICMSParT * peICMOrig / 100 ) ) 
							vlICMDesT   = ( valICMSParT -vlICMOrig ) #self.Trunca.trunca(3, ( valICMSParT * peICMDesT / 100 ) ) 

							""" Se o objeto imcs for 0 e pq o e ST entao sendo interestadual o sistema calcula apenas a partulha
								InterEstadual ST Zera Informacoes do ICMS Permancecer apenas os dados de partilha
							"""
							if Decimal( icms ) == 0:	vlICMOrig = vlICMDesT = Decimal("0.00")

							valTICMSParTo +=vlICMOrig
							valTICMSParTd +=vlICMDesT

							infParTilha = str( BaseCalcIcms )+";"+str( aliqFundP )+";"+str( aliqDesti )+";"+str( aliqInter )+";"+str( peICMDesT )+";"+str( valFundoProb )+";"+str( vlICMDesT )+";"+str( vlICMOrig )

							""" Se o objeto imcs for 0 e pq o e ST entao sendo interestadual o sistema calcula apenas a partulha
								InterEstadual ST Zera Informacoes do ICMS Permancecer apenas os dados de partilha
							"""
							if Decimal( icms ) == 0:	CoeficieIcms = BaseCalcIcms = ImpostoNormal = ValorIcms = Decimal('0.00')
				

					if Decimal( ricm ) > 0: #-->[ Reducao da Base de Calculo ICMS ]

						CoefReducao  = Trunca.arredonda(2, ( Decimal( ricm ) / Decimal( icms ) ) )
						BaseReducao  = Trunca.arredonda(2, ( CoefReducao * Decimal(suBToTal) ) )
						ValorReducao = Trunca.arredonda(2, ( BaseReducao *  ( Decimal(icms) / 100 ) ) )

					if STIVA > 0: #->Substituicao Tributaria [ Indice de Valor Agregado ]

						STCoeficiente = ( 1 + ( STIVA /100 ) )
						STBaseCalculo = ( Decimal( suBToTal ) + valorIPI )
						if self.STiA == 'S':	STBaseCalculo = ( STBaseCalculo + vlAcres )
						if self.STiF == 'S':	STBaseCalculo = ( STBaseCalculo + vlFrete )
						if self.STiD == 'S':	STBaseCalculo = ( STBaseCalculo - vlDesco )
						STBaseCalculo = Trunca.arredonda(2, ( STBaseCalculo * STCoeficiente ) )
						valorST       = Trunca.trunca(3, ( STBaseCalculo * Decimal(icms) / 100 ) )
						
						valorST       = ( valorST - ValorIcms )

				""" Calculo do Impostometro Fonte: IBPT """
				imposToIBPT = ""
				if dIBPT !="":
					
					vTF= vIF= vES= vMU = Decimal("0.00")
					
					vSDesconT = ( Decimal(suBToTal) - vlDesco )
					iBpTDados = dIBPT.split("|")

					if iBpTDados[0] !="" and Decimal( iBpTDados[0] ) !=0:	vTF = Trunca.trunca( 3, ( vSDesconT * ( Decimal( iBpTDados[0] ) / 100 ) ) )
					if iBpTDados[1] !="" and Decimal( iBpTDados[1] ) !=0:	vIF = Trunca.trunca( 3, ( vSDesconT * ( Decimal( iBpTDados[1] ) / 100 ) ) )
					if iBpTDados[2] !="" and Decimal( iBpTDados[2] ) !=0:	vES = Trunca.trunca( 3, ( vSDesconT * ( Decimal( iBpTDados[2] ) / 100 ) ) )
					if iBpTDados[3] !="" and Decimal( iBpTDados[3] ) !=0:	vMU = Trunca.trunca( 3, ( vSDesconT * ( Decimal( iBpTDados[3] ) / 100 ) ) )
				
					imposToIBPT	= str( vTF )+"|"+str( vIF )+"|"+str( vES )+"|"+str( vMU )+"|"+iBpTDados[4]+"|"+iBpTDados[5]+"|"+iBpTDados[6]
				
					vFNibpT +=vTF
					vFIibpT +=vIF
					vESibpT +=vES
					vMUibpT +=vMU

				if ibptp !=0:
					
					vST   = ( Decimal(suBToTal) - vlDesco )
					vIBPT = Trunca.trunca(3,( vST * ( ibptp / 100 ) ) )
					IBPTValorP += vIBPT

				zera = False

				""" Regime Tributario """
				if login.filialLT[ FiliIT ][30].split(';')[11] != "1" and cst[1:3] == "30":	zera = True
				if login.filialLT[ FiliIT ][30].split(';')[11] == "1":
					
					if cst[1:4] == "202" or cst[1:4] == "203":	zera = True

				if zera == True:

					BaseCalcIcms  = Decimal("0.00")
					BaseReducao   = Decimal("0.00")
					ValorIcms     = Decimal("0.00")

				if cst and int( cst ) == 60:	BaseCalcIcms = ValorIcms = Decimal('0.00')

				self.p.ListaPro.SetStringItem(indice,25,  str(icms))
				self.p.ListaPro.SetStringItem(indice,31,  str(BaseCalcIcms))
				self.p.ListaPro.SetStringItem(indice,32,  str(BaseReducao))
				self.p.ListaPro.SetStringItem(indice,33,  str(IPBaseCalculo))
				self.p.ListaPro.SetStringItem(indice,34,  str(STBaseCalculo))
				self.p.ListaPro.SetStringItem(indice,35,  str(ISBaseCalculo))
				self.p.ListaPro.SetStringItem(indice,36,  str(ValorIcms))
				self.p.ListaPro.SetStringItem(indice,37,  str(ValorReducao))
				self.p.ListaPro.SetStringItem(indice,38,  str(valorIPI))
				self.p.ListaPro.SetStringItem(indice,39,  str(valorST))
				self.p.ListaPro.SetStringItem(indice,40,  str(valorISS))
				self.p.ListaPro.SetStringItem(indice,49,  str(vIBPT))
				self.p.ListaPro.SetStringItem(indice,78,  str( imposToIBPT ) )
                  
				self.p.ListaPro.SetStringItem(indice,82,  str( PISBCalculo ) )
				self.p.ListaPro.SetStringItem(indice,83,  str( COFBCalculo ) )
				self.p.ListaPro.SetStringItem(indice,84,  str( valorPIS ) )
				self.p.ListaPro.SetStringItem(indice,85,  str( valorCOF ) )
				self.p.ListaPro.SetStringItem(indice,86,  str( infParTilha ) )

				""" Tabela Temporaria """
				if Temporario == True and addTemp == True:
					
					if self.p.TComa2.GetValue() == True:	_TP = "O"
					else:	_TP = "D"
					
					if self.p.TComa3.GetValue() == True:	_TP = "V"
					if self.p.TComa4.GetValue() == True:	_TP = "F"
					if self.p.TComa5.GetValue() == True:	_TP = "C"

					_item   = str(self.p.ListaPro.GetItem(indice,  0).GetText())
					_cdprod = str(self.p.ListaPro.GetItem(indice,  1).GetText())
					_produt = self.p.ListaPro.GetItem(indice,  2).GetText()
					_quanti = str(self.p.ListaPro.GetItem(indice,  3).GetText())
					_unidad = self.p.ListaPro.GetItem(indice,  4).GetText()
					_precos = str(self.p.ListaPro.GetItem(indice,  5).GetText())
					_subToT = str(self.p.ListaPro.GetItem(indice,  6).GetText())
					_pcunid = str(self.p.ListaPro.GetItem(indice,  7).GetText())

					_clcomp = str(self.p.ListaPro.GetItem(indice,  8).GetText())
					_cllarg = str(self.p.ListaPro.GetItem(indice,  9).GetText())
					_clexpe = str(self.p.ListaPro.GetItem(indice, 10).GetText())
					_clmetr = str(self.p.ListaPro.GetItem(indice, 11).GetText())
                                                        
					_ctcomp = str(self.p.ListaPro.GetItem(indice, 12).GetText())
					_ctlarg = str(self.p.ListaPro.GetItem(indice, 13).GetText())
					_ctexpe = str(self.p.ListaPro.GetItem(indice, 14).GetText())
					_ctmetr = str(self.p.ListaPro.GetItem(indice, 15).GetText())

					_unpeca = str(self.p.ListaPro.GetItem(indice, 16).GetText()) #->Unidade de Pecas
					_medcon = str(self.p.ListaPro.GetItem(indice, 17).GetText()) #->Medidas de Controle
					_obscor = self.p.ListaPro.GetItem(indice, 18).GetText().upper() #->Observacao de Corte

					_ecfiat = str(self.p.ListaPro.GetItem(indice, 30).GetText()) #->Codificacao ECF I,F,N,T

					_fabric = self.p.ListaPro.GetItem(indice, 43).GetText() #-> Fabricante
					_endere = str(self.p.ListaPro.GetItem(indice, 44).GetText()) #-> Endereco
					_barras = str(self.p.ListaPro.GetItem(indice, 45).GetText()) #-> Codigo de Barras

					_pibpt  = str(self.p.ListaPro.GetItem(indice,48).GetText())
					_vibpt  = str(self.p.ListaPro.GetItem(indice,49).GetText())
					_fisca  = str(self.p.ListaPro.GetItem(indice,53).GetText())
					_login  = str(login.usalogin)
					_con    = str(self.p.TempDav.GetLabel()) #--:[ Numero do Controle { Dav-Controle Temporario } ]
					_tabela = str(self.p.ListaPro.GetItem(indice,64).GetText())

					_vCusto = str( self.p.ListaPro.GetItem(indice,65).GetText() ) #--:[ Valor de Custo do Produto ]
					_TCusto = str( self.p.ListaPro.GetItem(indice,66).GetText() ) #--:[ Valor Total do Custo ]
					_DDevol = str( self.p.ListaPro.GetItem(indice,67).GetText() ) #--:[ Dados da Devolucao ]
					_vlManu = str( self.p.ListaPro.GetItem(indice,72).GetText() ) #--:[ Valor Manual ]
					_auTorz = self.p.ListaPro.GetItem(indice,73).GetText() #--:[ Autorizacao Remoto-Local ]
					_vndkiT = str( self.p.ListaPro.GetItem(indice,74).GetText() ) #--:[ Codigo do Produto principal do KIT ]
					_qTvkiT = str( self.p.ListaPro.GetItem(indice,75).GetText() ) #--:[ Quantidade de KIT-Vendedido ]
					codigoI = self.p.ListaPro.GetItem(indice,79).GetText() #--:[ Codigo de identificacao avulso ]

					perdesc = str( self.p.ListaPro.GetItem(indice,87).GetText() ) #--:[ Percentual de desconto por produto ]
					vlrdesc = str( self.p.ListaPro.GetItem(indice,88).GetText() ) #--:[ Valor do desconto por produto ]

					dadosdv =  codigoI+"|"+perdesc+"|"+vlrdesc

					Igrava = "INSERT INTO tdavs (tm_item,tm_cont,tm_codi,tm_nome,tm_quan,tm_unid,tm_prec,tm_vlun,tm_clcm,tm_clla,\
					tm_clex,tm_clmt,tm_ctcm,tm_ctla,tm_ctex,tm_ctmt,tm_subt,tm_unpc,tm_mdct,tm_obsc,\
					tm_tiat,tm_pibp,tm_fabr,tm_ende,tm_barr,tm_cdfi,tm_logi,tm_lanc,tm_hora,tm_tipo,\
					tm_clie,tm_tabe,tm_cprc,tm_cust,tm_dado,tm_fili,tm_manu,tm_auto,tm_kitc,tm_qkiv,tm_ouin)\
					VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
					%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
					%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
					%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

					self.p.sql[2].execute(Igrava,(_item,_con,_cdprod,_produt,_quanti,_unidad,_precos,_pcunid,_clcomp,_cllarg,\
					_clexpe,_clmetr,_ctcomp,_ctlarg,_ctexpe,_ctmetr,_subToT,_unpeca,_medcon,_obscor,\
					_ecfiat,_pibpt,_fabric,_endere,_barras,_fisca,_login,dTaEmi,HraEmi,_TP,\
					self.p.clC.GetLabel(),_tabela,_vCusto,_TCusto,_DDevol,FiliIT,_vlManu,_auTorz,_vndkiT,_qTvkiT, dadosdv) )

					#--------[ F i m]
				
				indice +=1
				ordems +=1
				self.ToTalGeral +=Decimal(suBToTal)
				ValorTIcms      +=ValorIcms 
				ValorTRIcm      +=ValorReducao
				ValorTSBT       +=valorST
				ValorTIPI       +=valorIPI

			valorSubTotal = Decimal( format(self.ToTalGeral,'.2f') )
			Acrescimos    = ( valorAcrescimo  + valorFrete )
			valorTotal    = ( ( valorSubTotal + Acrescimos + ValorTSBT + ValorTIPI ) - valorDesconto )
			#valorTotal    = ( ( valorSubTotal + Acrescimos + ValorTSBT + ValorTIPI + Decimal( valorPIS ) + Decimal( valorCOF ) ) - valorDesconto )

			if IBPTValorP !=0:	MediaIBPT = Trunca.arredonda(2, ( IBPTValorP / ( valorSubTotal - valorDesconto ) * 100 ) )

		""" Atualiza Campos """
		self.p.sT. SetValue(format(valorSubTotal,','))
		self.p.Tg. SetValue(format(valorTotal,','))
		self.p.sTD.SetValue(format(valorDesconto,','))
		self.p.sTF.SetValue(format(valorFrete,','))
		self.p.sTA.SetValue(format(valorAcrescimo,','))

		self.p.ICM.SetValue(format(ValorTIcms,','))
		self.p.DIC.SetValue(format(ValorTRIcm,','))
		self.p.IPI.SetValue(format(ValorTIPI ,','))
		self.p.SBT.SetValue(format(ValorTSBT ,','))

		self.p.ibpVFd.SetValue( format(vFNibpT,',') )
		self.p.ibpVFi.SetValue( format(vFIibpT,',') )
		self.p.ibpVEs.SetValue( format(vESibpT,',') )
		self.p.ibpVMu.SetValue( format(vMUibpT,',') )
		
		self.p.PIS.SetValue( format(vTIPI,',') )
		self.p.COF.SetValue( format(vTCOF,',') )

		"""   Totaliza Partilha { Origem-Destino }   """
		self.p.parvlTor.SetValue( format(valTICMSParTo,',') )
		self.p.parvlTds.SetValue( format(valTICMSParTd,',') )
        
		self.p.vpIBPT.SetLabel("Valor Aprox.Tributos\n  "+format(IBPTValorP,',')+" ("+str(MediaIBPT)+"%)")
			
		self.p.aTualizaValorGeral( valorTotal )

		""" Grava no Arquivo Temporario """
		if Temporario == True:

			try:	self.p.sql[1].commit()
			except Exception, _reTornos:	self.p.sql[1].rollback()
		
		if self.p.TComa3.GetValue() != True and self.p.TComa4.GetValue() != True and self.p.ToTalGeral == 0:	self.p.NovoDav(wx.EVT_BUTTON)

	def retornaPrecos( self, Filial, lisTa, Tipo = 1 ):
		
		pc1 = pc2 = pc3 = pc4 = pc5 = pc6 = "0.00"
		lsT = ""
		lsF = ""
		rTr = False
		
		for i in lisTa.split("\n"):
						
			if i !="":

				if i.split("|")[0].split(";")[0] != Filial:	lsF +=i+"\n"
				if i.split("|")[0].split(";")[0] == Filial:

					pc = i.split("|")[1].split(";")
					if Decimal( pc[0] ) !=0:

						pc1,pc2,pc3,pc4,pc5,pc6 = pc[0],pc[1],pc[2],pc[3],pc[4],pc[5]
						lsT = i
						rTr = True
						
		if Tipo == 1:	return rTr,pc1,pc2,pc3,pc4,pc5,pc6
		if Tipo == 2:	return lsT,lsF

	#----------------------------------------------------#
	#--: Funcao p/Calcular os Tributos q compoe a NFs :--#
	#----------------------------------------------------#
	def calcularTributosNFs( self, par, Filial, sql, _op, codFiscal="", clEstado = "" ):
		
		self.p = par
		Trunca = truncagem()
		
		esTadoFil = str( login.filialLT[ Filial ][6].lower() ) #--------------: Estado da Filial
		regimeTrb = login.filialLT[ Filial ][30].split(';')[11] #-----: Regime Tributario
		TabncmIPB = diretorios.aTualPsT+"/srv/"+esTadoFil+"ncm.csv" #-: Caminha da Tabela do NCM p/Retirar IBPT

		"""  Verifica a existencia da tabela  """
		if os.path.exists( TabncmIPB ) == True:	IBPTTabela = open(TabncmIPB,"r")
		else:	IBPTTabela = ""

		peICMOrig = Decimal("0.00") #-: Percentual do icms interestadua da origem
		peICMDest = Decimal("0.00") #-: Percentual do icms interestadua do destino
		if len( codFiscal.split('.') ) >= 4:	cFiscal = codFiscal.split('.')
		else:	cFiscal = ""
		
		cFcNCM = '' if cFiscal == "" else cFiscal[0] #-: Codigo Fiscal:	NCM
		cFCFOP = ''	if cFiscal == "" else cFiscal[1] #-: Codigo Fiscal:	CFOP	
		cFcCST = ''	if cFiscal == "" else cFiscal[2] #-: Codigo Fiscal:	CST

		"""  Se tiver nao tiver cadastrado o codigo fical no cadastor de codigos ficais e estiver no campo do procduto utiliza esses dados  """
		imICMS = Decimal("0.00") if cFiscal == "" else cFiscal[3][:len(cFiscal[3])-2]+'.'+cFiscal[3][len(cFiscal[3])-2:] #-: Imposto: Aliquota ICMS
		impMVA = Decimal("0.00") #-: Imposto: Aliquota MVA
		impIPI = Decimal("0.00") #-: Imposto: Aliquota IPI
		impISS = Decimal("0.00") #-: Imposto: Aliquota ISS
		imRBIC = Decimal("0.00") #-: Imposto: Aliquota da Reducao da base de calculos do icms
		imRBST = Decimal("0.00") #-: Imposto: Aliquota da Reducao da base de calculos da substituicao tributaria

		imnaFD = Decimal("0.00") #-: IBPT-Nacional Federal
		imImpF = Decimal("0.00") #-: IBPT-Importado Federal
		imESTA = Decimal("0.00") #-: IBPT-Estadual
		imMUNI = Decimal("0.00") #-: IBPT-Municipal

		#--------------------------------------#
		# ATualiza Percentuais origem, destino #
		#--------------------------------------#	
		anoATual = datetime.datetime.now().strftime("%Y")
		if anoATual in login.parICMSE:	peICMOrig,peICMDest = Decimal(login.parICMSE[anoATual][0]),Decimal(login.parICMSE[anoATual][1])
		else:

			"""  Se o ano nao for localizado pega o ultimo ano da lista   """
			ulTano = ""
			for picm in login.parICMSE:	ulTano = picm
			if ulTano !="":	peICMOrig, peICMDest = Decimal(login.parICMSE[ulTano][0]),Decimal(login.parICMSE[ulTano][1])

		#-------------------------#
		# Validar o Codigo Fiscal #
		#-------------------------#	
		if len( login.filialLT[ Filial ][30].split(";") ) >= 15 and login.filialLT[ Filial ][30].split(";")[14] != "T" and codFiscal == "":
			
			alertas.dia(self.p,u"Código Fiscal, estar vazio...\n"+(" "*90),"Localizando Codificação Fiscal")
			return False,""
			
		if len( login.filialLT[ Filial ][30].split(";") ) >= 15 and login.filialLT[ Filial ][30].split(";")[14] != "T" and codFiscal != "":

			rT  = sql[2].execute("SELECT * FROM tributos WHERE cd_codi='"+str( codFiscal )+"'")
			if rT == 0 and not self.p.vincularemNFe:	alertas.dia(self.p,u"Código Fiscal "+str( codFiscal )+u", não localizado\n\n1 - Cadastro de produtos varrer codigos fiscais e atualizar\n"+(" "*150),"Localizando Codificação Fiscal")
			else:

				TbT = sql[2].fetchone()

				"""  Quando for vincular orcamento ao pedido p/reducao na emissao da nfe/nfce  """
				if self.p.vincularemNFe and not TbT and len( codFiscal.split(".") ) >= 4:

					cFcNCM, cFCFOP, cFcCST, imICMS = codFiscal.split(".")
					impMVA = imRBIC = imRBST = imICMS = Decimal("0.00")

				else:	
					cFcNCM, cFCFOP, cFcCST = TbT[3],TbT[4],TbT[5]
					imICMS, impMVA, impIPI, impISS, imRBIC, imRBST = TbT[9],TbT[11],TbT[10],TbT[15],TbT[18],TbT[19]

				"""  Estado diferente do emissor  """
				if esTadoFil !='' and clEstado !="" and esTadoFil.upper() != clEstado.upper():	impMVA = TbT[12]

				lCST1 = ["102","103","300","400"]
				
				cdcsT = cFcCST[1:] if len( cFcCST ) == 4 else cFcCST

				if regimeTrb == "1":
					
					if cdcsT == "101":	impMVA = imRBIC = imRBST = imICMS = Decimal("0.00")
					if cdcsT in lCST1:	impMVA = imRBIC = imRBST = imICMS = Decimal("0.00")
				else:
					
					if int( cdcsT ) == 0:	impMVA = imRBIC = imRBST = Decimal("0.00")
					if int( cdcsT ) == 60:	impMVA = imRBIC = imRBST =imICMS = "0.00"
					if int( cdcsT ) == 51 or int( cdcsT ) == 20:	impMVA = imRBST = "0.00"

		"""  Estado diferente do emissor  """
		if esTadoFil !='' and clEstado !="" and esTadoFil.upper() != clEstado.upper() and cFCFOP !="":
			
			cFCFOP = "6"+cFCFOP[1:] #-// CFOP 6405-fora do estado nao existe e foi substituido por 6403 fora do estado
			if cFCFOP == "6405":	cFCFOP = "6403"

		#-------------------------------------#
		# Retorno dos dados da Tabela do IBPT #
		#-------------------------------------#
		retorno_ibpt = True
		if IBPTTabela:	dadosIBPT = nF.retornoIBPT( IBPTTabela, codFiscal.split(".")[0], opcao=1 )
		else:

			alertas.dia( par ,"Tabela do ibpt p/estado "+str( esTadoFil.upper() )+", não localizada...\n"+(" "*120),"Tabela do IBPT")
			dadosIBPT = '|||||'
			retorno_ibpt = False

		codFisc = cFcNCM, cFCFOP, cFcCST
		imposto = imICMS, impMVA, impIPI, impISS, imRBIC, imRBST

		return retorno_ibpt ,codFisc,imposto,dadosIBPT

	def finalizaRecalculo(self, parent, par ):

		conn = sqldb()
		sql  = conn.dbc("DAVs, Consulta de Clientes", fil = parent.fcFilial, janela = parent.painel )
		grva = True
		
		if sql[0] == True:
		
			_mensagem = mens.showmsg("Ajuste-Recalcular DAV...\nAtualizando em Controle\n\nAguarde...")

			try:

				dadosAnterior = [''] if not sql[2].execute("SELECT cr_hist FROM cdavs WHERE cr_ndav='"+str( par.caixaDavNumeroRec )+"'") else sql[2].fetchone()

				lsTProduTos = parent.adicionarItemsLista( parent.fcFilial )
				tb, bs, pa, ib, tg = par.TotalizaGravacaoDav( lsTProduTos )

				vFr, vAC, vDC, vIC, vDI, vIP, vST, vIS, vPI, vCO, TOP = tb[0],tb[1],tb[2],tb[3],tb[4],tb[5],tb[6],tb[7],tb[8],tb[9],tb[10]
				BaseIcms, BaseRicm, BaseIPI, BaseST, BaseISS, vlCusTo, BasePIS, BaseCOF = bs[0],bs[1],bs[2],bs[3],bs[4],bs[5],bs[6],bs[7]
				FundoPobreza, ICMSPaOrigem, ICMSPDestino = pa[0],pa[1],pa[2]
				ibvFN, ibvFI, ibvES, ibvMU = ib[0],ib[1],ib[2],ib[3]

				da = dadosAnterior[0].decode("UTF-8") if type( dadosAnterior[0] ) == str else dadosAnterior[0]	
				dadosAlterado = da + u'\n\nAlteração realizado pelo caixa: '+datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin+"\nFrete: "+str( vFr )+'\nAcrescimo: '+str( vAC )+'\nDescontos: '+str( vDC )

				dadosIBPT, TON, ToTalizaParTilha, IBP = tg[0], tg[1], tg[2], tg[3]

				atDavs = "UPDATE cdavs SET cr_vfre='"+str(vFr)+"',cr_vacr='"+str(vAC)+"',cr_vdes='"+str(vDC)+"',cr_vcim='"+str(vIC)+"',cr_vric='"+str(vDI)+"',\
				cr_vipi='"+str(vIP)+"',cr_vsub='"+str(vST)+"',cr_viss='"+str(vIS)+"',cr_bcim='"+str(BaseIcms)+"',cr_bric='"+str(BaseRicm)+"',cr_bipi='"+str(BaseIPI)+"',\
				cr_bsub='"+str(BaseST)+"',cr_biss='"+str(BaseISS)+"',cr_tpro='"+str(TOP)+"',cr_tnot='"+str(TON)+"',cr_pibc='"+str(BasePIS)+"',cr_cobc='"+str(BaseCOF)+"',\
				cr_pivl='"+str(vPI)+"',cr_covl='"+str(vCO)+"',cr_ibpt='"+str(IBP)+"',cr_hist='"+dadosAlterado+"',cr_cust='"+str(vlCusTo)+"',cr_dibp='"+str(dadosIBPT)+"',cr_part='"+str(ToTalizaParTilha)+"' WHERE cr_ndav='"+str( par.caixaDavNumeroRec )+"'"

				sql[2].execute( atDavs )
				
				for iTems in range( len( lsTProduTos ) ):


					_item   = str(lsTProduTos[iTems][0])
					_cdprod = lsTProduTos[iTems][1]
					_produt = lsTProduTos[iTems][2]

					_vfrete = str(lsTProduTos[iTems][22]) #->Valor do Frete
					_vacres = str(lsTProduTos[iTems][23]) #->Valor do Acrescimo
					_vdesco = str(lsTProduTos[iTems][24]) #->Valor do Desconto
					_peicms = str(lsTProduTos[iTems][25]) #->Percentual Rateio do ICMS
					_pricms = str(lsTProduTos[iTems][26]) #-> Reducao ICMS
					_peripi = str(lsTProduTos[iTems][27]) #-> IPI
					_pesubt = str(lsTProduTos[iTems][28]) #-> ST MVA
					_periss = str(lsTProduTos[iTems][29]) #-> ISS
					_bcicms = str(lsTProduTos[iTems][31]) #->Base de Calculo ICMS
					_bcricm = str(lsTProduTos[iTems][32]) #-> Reducao Icms
					_bcaipi = str(lsTProduTos[iTems][33]) #-> IPI
					_bcsubt = str(lsTProduTos[iTems][34]) #-> SBT
					_bcaiss = str(lsTProduTos[iTems][35]) #-> ISS
					_vlicms = str(lsTProduTos[iTems][36]) #->Valor ICMS
					_vlricm = str(lsTProduTos[iTems][37]) #-> Reducao do ICMS
					_vlripi	= str(lsTProduTos[iTems][38]) #-> iPI 
					_vlrsbt = str(lsTProduTos[iTems][39]) #-> SBT
					_vrliss = str(lsTProduTos[iTems][40]) #-> ISS
					perPIS  =  str(lsTProduTos[iTems][80]) #--:Percentual PIS
					perCOF  =  str(lsTProduTos[iTems][81]) #--:Percentual COFINS
					BasPIS  =  str(lsTProduTos[iTems][82]) #--:BaseCalculo PIS
					BasCOF  =  str(lsTProduTos[iTems][83]) #--:BaseCalculo COFINS
					ValPIS  =  str(lsTProduTos[iTems][84]) #--:Valor PIS
					ValCOF  =  str(lsTProduTos[iTems][85]) #--:Valor COFINS

					_NCM  = str(lsTProduTos[iTems][42]) #-: NCM
					_CFOP = str(lsTProduTos[iTems][46]) #-: CFOP
					_CST  = str(lsTProduTos[iTems][47]) #-: CST
					_CFIS = str(lsTProduTos[iTems][53]) #-: Codigo Fiscal

					_pibpt  = str(lsTProduTos[iTems][48])
					_vibpt  = str(lsTProduTos[iTems][49])
					
					_pCusto = str(lsTProduTos[iTems][65])
					_TCusto = str(lsTProduTos[iTems][66])
					_daibpT = str(lsTProduTos[iTems][78]) #--:Dados do IBPT

					parTIC  =  str(lsTProduTos[iTems][86]) #--:Partilha do ICMS
					_mensagem = mens.showmsg("Ajuste-Recalcular DAV...\nProduto: "+ _produt +"\n\nAguarde...")

					grITems = "UPDATE idavs SET it_vfre='"+str(_vfrete)+"',it_vacr='"+str(_vacres)+"',it_vdes='"+str(_vdesco)+"',it_pcim='"+str(_peicms)+"',\
					it_pric='"+str(_pricms)+"',it_pipi='"+str(_peripi)+"',it_psub='"+str(_pesubt)+"',it_piss='"+str(_periss)+"',it_bcim='"+str(_bcicms)+"',\
					it_bric='"+str(_bcricm)+"',it_bipi='"+str(_bcaipi)+"',it_bsub='"+str(_bcsubt)+"',it_biss='"+str(_bcaiss)+"',it_vcim='"+str(_vlicms)+"',\
					it_vric='"+str(_vlricm)+"',it_vipi='"+str(_vlripi)+"',it_vsub='"+str(_vlrsbt)+"',it_viss='"+str(_vrliss)+"', it_pper='"+str(perPIS)+"',\
					it_cper='"+str(perCOF)+"',it_pbas='"+str(BasPIS)+"',it_cbas='"+str(BasCOF)+"',it_pval='"+str(ValPIS)+"',it_cval='"+str(ValCOF)+"',\
					it_ncmc='"+str(_NCM)+"',it_cfop='"+str( _CFOP )+"',it_cstc='"+str(_CST)+"',it_cdfi='"+str(_CFIS)+"',\
					it_pibp='"+str(_pibpt)+"',it_vibp='"+str(_vibpt)+"',it_cprc='"+str(_pCusto)+"',it_ctot='"+str(_TCusto)+"',it_dibp='"+str(_daibpT)+"',it_part='"+str(parTIC)+"' \
					WHERE it_ndav='"+str( par.caixaDavNumeroRec )+"' and it_codi='"+str( _cdprod )+"' and it_item='"+str( _item )+"'"

					sql[2].execute( grITems )

				sql[1].commit()

			except Exception as erro:

				if type( erro ) !=unicode:	erro = str( erro )
				sql[1].rollback()
				grva = False

			conn.cls( sql[1] )
			del _mensagem
		
		if grva == False:	alertas.dia( parent,"Ajuste-Recalcular DAV\n\nErro: "+ erro +"\n"+(" "*140),"Caixa: Ajuste-Recalcuar" )
		if grva == True:	par.sair(wx.EVT_BUTTON)
		
	
class QuemComprouSelecionado(wx.Frame):
	
	filial = ""
	def __init__(self, parent,id):
	
		self.p = parent

		wx.Frame.__init__(self, parent, id, 'Relação de clientes que comprou o produto selecionado', size=(820,285), style = wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,-1)

		self.ClientesCompra = wx.ListCtrl(self.painel, 200,pos=(0,0), size=(700,238),
									style=wx.LC_REPORT
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.ClientesCompra.SetBackgroundColour('#E5E5E8')
		self.ClientesCompra.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ClientesCompra.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.davConsulta)

		self.ClientesCompra.InsertColumn(0, 'Numero DAV', width=90)
		self.ClientesCompra.InsertColumn(1, 'Descrição dos clientes', width=315)
		self.ClientesCompra.InsertColumn(2, 'Quem vendeu', width=180)
		self.ClientesCompra.InsertColumn(3, 'Quantidade', format=wx.LIST_ALIGN_LEFT,width=100)
		self.ClientesCompra.InsertColumn(4, 'Codigo do cliente',  width=200)

		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_ENTER_WINDOW,self.atualizaProduto)
		self.Bind(wx.EVT_LEAVE_WINDOW,self.atualizaProduto)

		self.sair = wx.BitmapButton(self.painel, 241, wx.Bitmap("icons/go_forward.png",  wx.BITMAP_TYPE_ANY), pos=(703, 0), size=(35,30))
		self.rele = wx.BitmapButton(self.painel, 242, wx.Bitmap("imagens/reler16.png",   wx.BITMAP_TYPE_ANY), pos=(703,40), size=(35,30))
		self.view = wx.BitmapButton(self.painel, 243, wx.Bitmap("imagens/estorno16.png", wx.BITMAP_TYPE_ANY), pos=(703,80), size=(35,30))

		self.qcomprou = GenBitmapTextButton(self.painel,-1,label=' Iniciar consulta\nQuem comprou', pos=(703,257),size=(118,26), bitmap=wx.Bitmap("imagens/frente.png", wx.BITMAP_TYPE_ANY))
		self.qcomprou.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		wx.StaticText(self.painel,-1,"Selecione um periodo\nIncial-Final",pos=(703,120)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Codigo - Descrição do produto",pos=(3,245)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(703,148), size=(119,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(703,175), size=(119,25))

		self.qcperiodo = wx.CheckBox(self.painel, 503, "Pesquisa p/periodo", pos=(703,200))
		self.qcperiodo.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.qclientes = wx.CheckBox(self.painel, 504, "Mostrar apenas\nClientesCadastrados", pos=(703,222))
		self.qclientes.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.qclientes.SetValue( True )

		self.produto = wx.TextCtrl(self.painel,-1,'',pos=(0,258),size=(518,27), style = wx.TE_READONLY)
		self.produto.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.produto.SetBackgroundColour('#E5E5E5')
		self.produto.SetForegroundColour('#1E677F')

		self.vendedor = wx.ComboBox(self.painel, -1, '', pos=(520,258), size = (180,27), choices = [''] + login.venda + [''],style=wx.NO_BORDER|wx.CB_READONLY)

		self.forderna = wx.CheckBox(self.painel, 513, "Ordernar vendas por cliente", pos=(375,236))
		self.fcliente = wx.CheckBox(self.painel, 512, "Filtrar o cliente selecionado", pos=(520,236))
		self.forderna.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fcliente.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.sair.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.rele.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.view.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ClientesCompra.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.sair.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.rele.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.view.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ClientesCompra.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.qcomprou.Bind(wx.EVT_BUTTON, self.levantar )
		self.rele.Bind(wx.EVT_BUTTON, self.davConsulta)
		self.view.Bind(wx.EVT_BUTTON, self.informacoesCliente )
		self.sair.Bind(wx.EVT_BUTTON, self.voltar)
	
	def voltar(self,event):	self.Destroy()
	def atualizaProduto(self,event):

		indice  = self.p.list_ctrl.GetFocusedItem()
		codigo  = self.p.list_ctrl.GetItem( indice, 0 ).GetText()
		produto = self.p.list_ctrl.GetItem( indice, 1 ).GetText()
		self.produto.SetValue( codigo+'-'+produto)

	def levantar( self, event ):
			
		indice  = self.p.list_ctrl.GetFocusedItem()
		codigo  = self.p.list_ctrl.GetItem( indice, 0 ).GetText()
		produto = self.p.list_ctrl.GetItem( indice, 1 ).GetText()
		self.produto.SetValue( codigo+'-'+produto)

		conn = sqldb()
		sql  = conn.dbc("Retaguarda, Quem comprou o produto selecionado { Filial: "+str( self.filial )+" }", fil = str( self.filial ), janela = self.painel )

		if sql[0] == True: 
		
			inicial = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			final   = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

			__cs = "SELECT it_ndav, it_cdcl, it_quan,it_nmvd,it_lanc,it_horl,it_clie FROM idavs WHERE it_codi='"+ codigo +"' and it_canc='' and it_tped='1' ORDER BY it_lanc DESC"
			if self.forderna.GetValue():	__cs = "SELECT it_ndav, it_cdcl, it_quan,it_nmvd,it_lanc,it_horl,it_clie FROM idavs WHERE it_codi='"+ codigo +"' and it_canc='' and it_tped='1' ORDER BY it_cdcl, it_lanc DESC"
			if self.qclientes.GetValue():	__cs = __cs.replace("WHERE","WHERE it_cdcl!='' and ")
			if self.qcperiodo.GetValue():	__cs = __cs.replace("WHERE","WHERE it_lanc >='"+inicial+"' and it_lanc <='"+final+"' and")
			if self.fcliente.GetValue() and self.ClientesCompra.GetItemCount():
				
				cliente = self.ClientesCompra.GetItem( self.ClientesCompra.GetFocusedItem(), 4 ).GetText()
				if cliente:	__cs = __cs.replace("WHERE","WHERE it_cdcl='"+ cliente +"' and")
			
			if self.vendedor.GetValue() and len( self.vendedor.GetValue().split('-') ) >=2:

				vendedor = self.vendedor.GetValue().split('-')[1]
				if vendedor:	__cs = __cs.replace("WHERE","WHERE it_nmvd='"+ vendedor +"' and")
				
			sql[2].execute( __cs )
			_resul = sql[2].fetchall()
			conn.cls( sql[1] )

			self.ClientesCompra.DeleteAllItems()
			self.ClientesCompra.Refresh()
			indice = 0
			for i in _resul:
					
				self.ClientesCompra.InsertStringItem(indice, i[0] )
				self.ClientesCompra.SetStringItem(indice,1, i[6] )
				self.ClientesCompra.SetStringItem(indice,2, str( i[4].strftime("%d/%m/%Y") )+" "+ str( i[5] )+" "+i[3] )
				self.ClientesCompra.SetStringItem(indice,3, format( i[2], ',' ) )
				self.ClientesCompra.SetStringItem(indice,4, i[1] )
				if indice % 2:	self.ClientesCompra.SetItemBackgroundColour( indice, '#DFDFE8')
				indice +=1

	def davConsulta(self,event):
		
		numero_dav = self.ClientesCompra.GetItem( self.ClientesCompra.GetFocusedItem(), 0 ).GetText()
		self.p.parente.impre.impressaoDav( numero_dav, self, True, True, "", "", servidor = self.filial, codigoModulo = "616", enviarEmail = "608",recibo=False, vlunitario=True)

	def informacoesCliente(self,event):

		if not self.ClientesCompra.GetItemCount():	alertas.dia( self, "Lista de compras do produto selecionado vazia...\n"+(" "*140),"Lista de quem comprou o produto selecionado")
		else:
			
			codigo = self.ClientesCompra.GetItem( self.ClientesCompra.GetFocusedItem(), 4 ).GetText().strip()
			if codigo:

				conn = sqldb()
				sql  = conn.dbc("Retaguarda, Quem comprou o produto selecionado { Filial: "+str( self.filial )+" }", fil = str( self.filial ), janela = self.painel )
				ach  = ""

				if sql[0]:

					if sql[2].execute("SELECT cl_nomecl,cl_fantas,cl_telef1,cl_telef2,cl_telef3,cl_seguim,cl_redeso,cl_emails FROM clientes WHERE cl_codigo='"+ codigo +"'"):
						
						__d = sql[2].fetchone()
						_e1 = __d[6] if __d[6] else ""
						_e2 = __d[7] if __d[7] else ""
						
						ach = "Seguimento: "+__d[5] + "\n"+\
						      "  Fantasia: "+__d[1] + "\n"+\
						      " Descrição: "+__d[0] + "\n"+\
						      "Telefone_1: "+__d[2] + "\n"+\
						      "Telefone_2: "+__d[3] + "\n"+\
						      "Telefone_3: "+__d[4] + "\n"+\
						      "     Redes: "+_e1 + "\n"+\
						      "    Emails: "+_e2
					
					conn.cls( sql[1] )
				
					if ach:

						MostrarHistorico.hs = ach
						MostrarHistorico.TP = ""
						MostrarHistorico.TT = "Retaguarda"
						MostrarHistorico.AQ = ""
						MostrarHistorico.FL = self.filial
						MostrarHistorico.GD = ""

						his_frame=MostrarHistorico(parent=self,id=-1)
						his_frame.Centre()
						his_frame.Show()
						
					else:	alertas.dia( self, "Cliente não localizado no cadastro de clientes...\n"+(" "*140),"Lista de quem comprou o produto selecionado")
					
			else:	alertas.dia( self, "Codigo do cliente vazio...\n"+(" "*120),"Lista de quem comprou o produto selecionado")

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 241:	sb.mstatus(u"  Sair - voltar",0)
		elif event.GetId() == 242:	sb.mstatus(u"  Visualizar o dav, imprimir",0)
		elif event.GetId() == 243:	sb.mstatus(u"  Mostra dados do cliente, telefone, email etc...",0)
		elif event.GetId() == 200:	sb.mstatus(u"  click duplo, Visualizar o dav, imprimir",0)
	
		event.Skip()

	def OnLeaveWindow(self,event):

		sb.mstatus("  Retaguarda de relação de clientes que comprou o produto selecioando",0)
		event.Skip()
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#2186E9") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.DrawRotatedText("Filial: "+ self.filial, 760, 108, 90)
	
		dc.DrawRotatedText("Quem comprou",780, 108, 90)
		dc.DrawRotatedText("O produto",   795, 108, 90)
		dc.DrawRotatedText("Selecionado", 810, 108, 90)

class RelacaoReservas(wx.Frame):

	def __init__(self, parent,id):
	
		self.p = parent

		wx.Frame.__init__(self, parent, id, 'Relação do produto selecionado pra venda em reserva temporaria',size=(650,212), style = wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,-1)
		self.reserva_venda = wx.ListCtrl(self.painel, 200,pos=(0,37), size=(610,175),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.reserva_venda.SetBackgroundColour('#8F9B9E')
		self.reserva_venda.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.reserva_venda.InsertColumn(0, 'Filial', width=80)
		self.reserva_venda.InsertColumn(1, 'Data reserva', format=wx.LIST_ALIGN_LEFT,width=110)
		self.reserva_venda.InsertColumn(2, 'Hora reserva', format=wx.LIST_ALIGN_LEFT,width=110)
		self.reserva_venda.InsertColumn(3, 'Usuario vendedor', width=150)
		self.reserva_venda.InsertColumn(4, 'Quantidade reservada', format=wx.LIST_ALIGN_LEFT, width=150)

		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		wx.StaticText(self.painel,-1,"Quantidade",pos=(3,2)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Estoque fisico",pos=(90,2)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Reserva temporaria",pos=(180,2)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Saldo de estoque",pos=(288,2)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		wx.StaticText(self.painel,-1,"Produto selecionado em reserva temporaria\nse o tempo de reserva for muito alto\nconsulte o vendedor p/liberação",pos=(388,0)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		__q = wx.TextCtrl(self.painel,-1, self.infor.split('|')[0], pos=(0,14),size=(80,20),style=wx.ALIGN_RIGHT)
		__q.SetBackgroundColour('#E5E5E5')
		__q.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		__f = wx.TextCtrl(self.painel,-1,self.infor.split('|')[1], pos=(87,14),size=(80,20),style=wx.ALIGN_RIGHT)
		__f.SetBackgroundColour('#E5E5E5')
		__f.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		__r = wx.TextCtrl(self.painel,-1,self.infor.split('|')[2], pos=(177,14),size=(100,20),style=wx.ALIGN_RIGHT)
		__r.SetBackgroundColour('#E5E5E5')
		__r.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		__s = wx.TextCtrl(self.painel,-1,self.infor.split('|')[3], pos=(286,14),size=(90,20),style=wx.ALIGN_RIGHT)
		__s.SetBackgroundColour('#E5E5E5')
		__s.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
		indice = 0
		for i in self.lista.split('\n'):
			
			if i:
				
				_fl, _dt, _hr, _us, _qt = i.split('|')

				self.reserva_venda.InsertStringItem( indice, _fl )
				self.reserva_venda.SetStringItem( indice,1, _dt )
				self.reserva_venda.SetStringItem( indice,2, _hr )
				self.reserva_venda.SetStringItem( indice,3, _us )
				self.reserva_venda.SetStringItem( indice,4, _qt )
				indice +=1

		sair = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/voltap.png", wx.BITMAP_TYPE_ANY), pos=(612, 182), size=(38,30))				
		sair.Bind(wx.EVT_BUTTON, self.saida)
		
	def saida(self,event):	self.Destroy()
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#2186E9") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.DrawRotatedText("Retaguarda reserva temporaria", 613, 180, 90)
		dc.DrawRotatedText("Codigo: "+self.codig, 626,130, 90)
		dc.DrawRotatedText("Filial: "+self.filia, 639,130, 90)

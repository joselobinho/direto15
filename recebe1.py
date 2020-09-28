#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import datetime

from cdavs      import impressao
from decimal    import *
from conectar   import sqldb,formasPagamentos,dialogos,menssagem,truncagem,cores,socorrencia,numeracao,login,sbarra,TelNumeric,dadosCheque,regBandeira,srateio,consultarCliente,MostrarHistorico,autorizacoes,diretorios
from produtof   import fornecedores
from relatorio  import relatorioSistema,extrato,RelatorioBordero
from retaguarda import formarecebimentos
from apagar     import contasApagar
from contacorrente  import gravacaoLancamentos

from wx.lib.buttons import GenBitmapTextButton

alertas = dialogos()
forma   = formasPagamentos()
sb      = sbarra()
mens    = menssagem()
soco    = socorrencia()
forma   = formasPagamentos()
bordero = RelatorioBordero()
impress = impressao()
extrcli = extrato()
contaco = gravacaoLancamentos()
nF      = numeracao()

class consultaReceber(wx.Frame):
	
	nTitulo = ''
	flconrc = ''
	
	def __init__(self, parent,id):
		
		self.p = parent
		self.R = numeracao()
		mkn    = wx.lib.masked.NumCtrl

		wx.Frame.__init__(self, parent, id, '{ Contas A Receber } Consulta-Edição de Títulos', size=(670,482), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.Aven = self.Afpg = self.Avlr = self.Ancm = self.Aban = self.Aage = self.Achq = self.Ahis = self.Acon = self.Abnd = self.Acom = ''
		self.Acpf = self.Acor = ''

		wx.StaticText(self.painel,-1, "Nº Registro",          pos=(21,   5)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "CPF-CNPJ",             pos=(143,  5)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Descrição do Cliente", pos=(263,  5)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Vencimento",           pos=(21,  50)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Forma de Pagamento",   pos=(143, 50)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Bandeiras",            pos=(373, 50)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Valor da Parcela",     pos=(21, 100)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Nº Comprovante",       pos=(143,100)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, "Banco",     pos=(263,100)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Agência",   pos=(333,100)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Nº Conta",  pos=(433,100)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Nº Cheque", pos=(543,100)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Comp",      pos=(623,100)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, "CPF-CNPJ",  pos=(21,145)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Descrição do Correntista", pos=(143,145)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "{ Novo Historico }",       pos=(21,205)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1, "{ Historico Antigo de Alterações }", pos=(21,315)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1, "Filial", pos=(623,145)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		nh = wx.StaticText(self.painel,-1, "Historico de Alteração", pos=(235,205))
		nh.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		nh.SetForegroundColour('#125290')

		self.TTI = wx.StaticText(self.painel,-1, "", pos=(21,183))
		self.TTI.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TTI.SetForegroundColour('#883535')

		self._frp = login.pgALRC
		
		self.rgc = wx.TextCtrl(self.painel,-1, pos=(18, 18), size=(100,20), style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.doc = wx.TextCtrl(self.painel,-1, pos=(140,18), size=(100,20), style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.nmc = wx.TextCtrl(self.painel,-1, pos=(260,18), size=(406,20), style=wx.TE_READONLY)

		self.ven = wx.DatePickerCtrl(self.painel,-1,     pos=(18, 63),  size=(120,27), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.fpg = wx.ComboBox(self.painel, -1, '',      pos=(140,63),  size=(220,27), choices = self._frp, style=wx.NO_BORDER|wx.CB_READONLY)
		self.fbn = wx.ComboBox(self.painel, -1, '',      pos=(370,63),  size=(180,27), choices = login.pgLBan,      style=wx.NO_BORDER|wx.CB_READONLY)
		self.vpc = mkn(self.painel, -1,  value = '0.00', pos=(18, 115), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)
		self.vpc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ncm = wx.TextCtrl(self.painel,-1, pos=(140,115), size=(100,20), style = wx.ALIGN_RIGHT) #-:Numero do comprovante
		self.ban = wx.TextCtrl(self.painel,-1, pos=(260,115), size=(60, 20), style = wx.ALIGN_RIGHT) #-:Numero do Banco
		self.age = wx.TextCtrl(self.painel,-1, pos=(330,115), size=(90, 20), style = wx.ALIGN_RIGHT) #-:Agencia
		self.con = wx.TextCtrl(self.painel,-1, pos=(430,115), size=(100,20), style = wx.ALIGN_RIGHT) #-:Conta Corrente
		self.che = wx.TextCtrl(self.painel,-1, pos=(540,115), size=(73, 20), style = wx.ALIGN_RIGHT) #-:Numero do Cheque
		self.com = wx.TextCtrl(self.painel,-1, pos=(620,115), size=(43, 20), style = wx.ALIGN_RIGHT) #-:Numero da Compensacao
		self.fil = wx.TextCtrl(self.painel,-1, pos=(620,160), size=(43, 20), style = wx.ALIGN_RIGHT|wx.TE_READONLY) #-:Filial do Cliente

		self.cpf = wx.TextCtrl(self.painel,-1, pos=(18,160),  size=(120,20)) #-:CPF-CNPJ
		self.cor = wx.TextCtrl(self.painel,-1, pos=(140,160), size=(473,20)) #-:Nome do correntista
		self.his = wx.TextCtrl(self.painel,-1, pos=(18,225),  size=(644, 80), style = wx.TE_MULTILINE|wx.TE_DONTWRAP) #-:Historico novo
		self.han = wx.TextCtrl(self.painel,-1, pos=(18,335),  size=(644,130), style = wx.TE_MULTILINE|wx.TE_DONTWRAP) #-:Historico antigo

		self.rgc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.rgc.SetBackgroundColour('#E5E5E5')
		self.rgc.SetForegroundColour('#125290')
		self.doc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.doc.SetBackgroundColour('#E5E5E5')
		self.doc.SetForegroundColour('#125290')
		self.nmc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nmc.SetBackgroundColour('#E5E5E5')
		self.nmc.SetForegroundColour('#125290')

		self.ncm.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ncm.SetBackgroundColour('#BFBFBF')
		self.ban.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ban.SetBackgroundColour('#E5E5E5')
		self.age.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.age.SetBackgroundColour('#E5E5E5')
		self.che.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.che.SetBackgroundColour('#E5E5E5')
		self.con.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.con.SetBackgroundColour('#E5E5E5')
		self.com.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.com.SetBackgroundColour('#E5E5E5')

		self.fil.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.fil.SetBackgroundColour('#7F7F7F')
		self.fil.SetForegroundColour('#FFFFFF')

		self.cpf.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cpf.SetBackgroundColour('#E5E5E5')
		self.cor.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cor.SetBackgroundColour('#E5E5E5')

		self.his.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.his.SetBackgroundColour('#4D4D4D')
		self.his.SetForegroundColour('#90EE90')

		self.han.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.han.SetBackgroundColour('#7F7F7F')
		self.han.SetForegroundColour('#F7F7F7')

		voltar = wx.BitmapButton(self.painel,-1, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(569,50), size=(43,40))
		self.gravar = wx.BitmapButton(self.painel,-1, wx.Bitmap("imagens/savem.png",  wx.BITMAP_TYPE_ANY), pos=(622,50), size=(43,40))
		
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		self.gravar.Bind(wx.EVT_BUTTON, self.GravarAlteracoes )
		
		self.fpg.Bind(wx.EVT_COMBOBOX, self.evCombo)
		self.buscarTitulo()

		if self.nTitulo[3] in [ '1', '2', '4', '5' ]:	self.gravar.Enable(False)	

	def sair(self,event):	self.Destroy()
	def evCombo(self,event):

		""" Seleciona bandeiras, vinculada a forma de pagamento """
		
		if self.fpg.GetValue()[:2] == "04" or self.fpg.GetValue()[:2] == "05":	ema = True
		else:	ema = False
		
		if self.fpg.GetValue()[:2] == "02" or self.fpg.GetValue()[:2] == "03":	ena = True
		else:	ena = False
		
		self.ban.Enable(ena)
		self.age.Enable(ena)
		self.con.Enable(ena)
		self.che.Enable(ena)
		self.com.Enable(ena)
		self.cpf.Enable(ena)
		self.cor.Enable(ena)
		self.ncm.Enable(ema)
		
	def buscarTitulo(self):

		if self.nTitulo[0] ==  '':	self.gravar.Enable(False)
		else:
			
			conn = sqldb()
			sql  = conn.dbc("Contas Arecebe, Consultar-Editar", fil = self.flconrc, janela = self.painel )
			
			if sql[0] == True:
				
				achar = "SELECT * FROM receber WHERE rc_ndocum='"+str(self.nTitulo[0])+"' and rc_nparce='"+str(self.nTitulo[1])+"' and rc_regist='"+str(self.nTitulo[2])+"'"
				nRegi = sql[2].execute(achar)
				result = sql[2].fetchall()
				conn.cls(sql[1])
			
				if nRegi !=0:
					
					self.rgc.SetValue(result[0][11])
					self.doc.SetValue(result[0][14])
					self.fil.SetValue(result[0][25])
					self.TTI.SetLabel("Emissão: "+str(result[0][1])+" {"+str(result[0][2])+"} "+str( format(result[0][7],"%d/%m/%Y") )+" "+str(result[0][8])+" ["+str(result[0][9])+"-"+str(result[0][10])+"]")
					dadosCheque = ''

					if result[0][5]  !=None and result[0][5]  != '':	self.vpc.SetValue(str(result[0][5]))
					if result[0][58] !=None and result[0][58] != '':	self.ncm.SetValue(result[0][58])
					if result[0][30] !=None and result[0][30] != '':	self.ban.SetValue(result[0][30])
					if result[0][31] !=None and result[0][31] != '':	self.age.SetValue(result[0][31])
					if result[0][32] !=None and result[0][32] != '':	self.con.SetValue(result[0][32])
					if result[0][33] !=None and result[0][33] != '':	self.che.SetValue(result[0][33])
					if result[0][57] !=None and result[0][57] != '':	self.com.SetValue(result[0][57])
					if result[0][34] !=None and result[0][34] != '':	dadosCheque = "Dados do Cheque:\n"+result[0][34]+"\n\n"
					if result[0][28] !=None and result[0][28] != '':	self.cpf.SetValue(result[0][28])
					if result[0][29] !=None and result[0][29] != '':	self.cor.SetValue(result[0][29])
					if result[0][66] !=None and result[0][66] != '':	dadosCheque = "Dados das Alterações:\n"+result[0][66]

					self.han.SetValue(dadosCheque)
					if result[0][13] !='':	self.nmc.SetValue("{ "+result[0][13]+" }  "+result[0][12])
					else:	self.nmc.SetValue(result[0][12])

					d,m,y = format(result[0][26],"%d/%m/%Y").split('/')
					self.ven.SetValue(wx.DateTimeFromDMY(int(d), ( int(m) - 1 ), int(y)))

					fp = 0
					if result[0][6][:2] == "02":	fp = 0 
					if result[0][6][:2] == "03":	fp = 1 
					if result[0][6][:2] == "04":	fp = 2 
					if result[0][6][:2] == "05":	fp = 3 
					if result[0][6][:2] == "06":	fp = 4 
					if result[0][6][:2] == "07":	fp = 5 
					if result[0][6][:2] == "08":	fp = 6
					if result[0][6][:2] == "10":	fp = 7 
					if result[0][6][:2] == "11":	fp = 8 
					if result[0][6][:2] == "12":	fp = 9 
					 
					if fp in login.pgALRC:	self.fpg.SetValue(self._frp[fp])

					""" Guarda Valores Antigos """
					self.Aven = format(result[0][26],"%d/%m/%Y") #-:Vencimento
					self.Afpg = result[0][6] #---------------------:Forma de Pagamento
					self.Avlr = result[0][5] #---------------------:Valor
					self.Abnd = result[0][27] #--------------------:Bandeira	
					self.Aban = result[0][30] #--------------------:Numero do Banco
					self.Acon = result[0][32] #--------------------:Conta Corrente 
					self.Aage = result[0][31] #--------------------:Agencia
					self.Achq = result[0][33] #--------------------:Numero do Cheque
					self.Ancm = result[0][58] #--------------------:Numero do Comprovante
					self.Acom = result[0][57] #--------------------:Numero da Compensacao
					self.Ahis = result[0][66] #--------------------:Historico Antigo
					self.Acpf = result[0][28] #--------------------:CPF-Correntista
					self.Acor = result[0][29] #--------------------:Nome-Correntista

					self.fbn.SetValue( result[0][27] )
					self.fpg.SetValue( result[0][6] )
					self.ncm.SetValue( result[0][58] )
					self.ban.SetValue( result[0][30] )
					self.age.SetValue( result[0][31] )
					self.con.SetValue( result[0][32] )
					self.che.SetValue( result[0][33] )
					self.com.SetValue( result[0][57] )
					self.cpf.SetValue( result[0][28] )
					self.cor.SetValue( result[0][29] )

					""" Permitir Alterar Aberto,Estornado """
					if result[0][35] !="" and result[0][35] !="2":	self.gravar.Enable(False)
					self.evCombo(wx.EVT_BUTTON)

	def GravarAlteracoes(self,event):

		if self.fpg.GetValue() == '':
			alertas.dia(self.painel,"Forma de Recebimento Vazio...\n"+(" "*80),"Contas Areceber: Alteração de Títulos")
			return

		if self.cpf.GetValue() !='' and self.R.cpfcnpj(self.cpf.GetValue())[0] == False:
			alertas.dia(self.painel,"CPF-CNPJ do correntista inválido\n"+(" "*80),"Contas Areceber: Alteração de Títulos")
			return

		dTAlteracao = datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin
		dadosAltera = u"Dados Alterados  [ "+dTAlteracao+u" ]\nUltima Alteração [ Dados Anteriror a ultima alteração ]\n\n"
		
		if self.Aven:	dadosAltera += "Vencimento: "+str(self.Aven)+"\n" #----------:Vencimento
		if self.Afpg:	dadosAltera += "Forma de Pagamento: "+str(self.Afpg)+"\n" #--:Forma de Pagamento
		if self.Avlr:	dadosAltera += "Valor da Parcela: "+str(self.Avlr)+"\n" #----:Valor
		if self.Abnd:	dadosAltera += "Bandeira: "+str(self.Abnd)+"\n" #------------:Bandeira	
		if self.Aban:	dadosAltera += u"Nº Banco: "+str(self.Aban)+"\n" #------------:Numero do Banco
		if self.Aage:	dadosAltera += "Agencia: "+str(self.Aage)+"\n" #-------------:Agencia
		if self.Acon:	dadosAltera += "Conta Corrente: "+str(self.Acon)+"\n" #------:Conta Corrente 
		if self.Achq:	dadosAltera += u"Nº Cheque: "+str(self.Achq)+"\n" #-----------:Numero do Cheque
		if self.Acom:	dadosAltera += u"Nº Compensação: "+str(self.Acom)+"\n" #------:Numero da Compensacao
		if self.Ancm:	dadosAltera += u"Nº Comprovante "+str(self.Ancm)+"\n" #-------:Numero do Comprovante
		if self.Acpf:	dadosAltera += "CPF-CNPJ-Correntista "+str(self.Acpf)+"\n" #-:Numero do Comprovante
		if self.Acor:	dadosAltera += "Nome Correntista "+str(self.Acor)+"\n" #-----:Numero do Comprovante

		if self.his.GetValue() and self.his.GetValue() !="None":	dadosAltera += "\n\nHistorico:\n"+self.his.GetValue()
		if self.han.GetValue() and self.han.GetValue() !="None":	dadosAltera += "\n\n"+self.han.GetValue()

		_ven = _fpg = _fbn = _vpc = _ncm = _ban = _age = _con = _che = _com = _cpf = _cor = ''
		
		_ven = datetime.datetime.strptime(self.ven.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y-%m-%d")
		_avn = datetime.datetime.strptime(self.ven.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
		_fpg = self.fpg.GetValue()
		_vpc = self.vpc.GetValue()

		if _fpg[:2] == "04" or _fpg[:2] == "05" or _fpg[:2] == "08" or _fpg[:2] == "11":	_fbn = self.fbn.GetValue() #-:Carta D/C, Financeira, Deposito em conta
		if _fpg[:2] == "04" or _fpg[:2] == "05":	_ncm = self.ncm.GetValue() #-:Cartao D/C { Nº Comprovante }

		if _fpg[:2] == "02" or _fpg[:2] == "03":

			_ban = self.ban.GetValue()
			_age = self.age.GetValue()
			_con = self.con.GetValue()
			_che = self.che.GetValue()
			_com = self.com.GetValue()
			_cpf = self.cpf.GetValue()
			_cor = self.cor.GetValue()
			_ncm = self.ncm.GetValue()

		TT = self.nTitulo[0]
		PC = self.nTitulo[1]
		IL = self.nTitulo[2]
		
		self.dados_alterados = ""

		if str( self.Aven ) != str( _avn ):	self.dados_alterados +="Vencimento........: "+str( _avn )+' Anteriror: '+str( self.Aven )+'\n'
		if str( self.Afpg ) != str( self.fpg.GetValue() ):	self.dados_alterados +="Forma de pagamento: "+str( self.fpg.GetValue() )+' Anteriror: '+str( self.Afpg )+'\n'
		if str( self.Avlr ) != str( self.vpc.GetValue() ):	self.dados_alterados +="Valor da parcela..: "+str( self.vpc.GetValue() )+' Anteriror: '+str( self.Avlr )+'\n'
		if str( self.Abnd ) != str( self.fbn.GetValue() ):	self.dados_alterados +="Cartao bandeira...: "+str( self.fbn.GetValue() )+' Anteriror: '+str( self.Abnd )+'\n'

		if _ban and self.Aban:	self.dados_alterados +="Banco.............: "+str( self.ban.GetValue() )+' Anteriror: '+str( _ban )+'\n'
		if _age and self.Aage:	self.dados_alterados +="Agencia...........: "+str( self.age.GetValue() )+' Anteriror: '+str( _age )+'\n'
		if _con and self.Acon:	self.dados_alterados +="Conta corrente....: "+str( self.con.GetValue() )+' Anteriror: '+str( _con )+'\n'
		if _che and self.Achq:	self.dados_alterados +="Numero cheque.....: "+str( self.che.GetValue() )+' Anteriror: '+str( _che )+'\n'
		if _com and self.Acom:	self.dados_alterados +="Compensacao.......: "+str( self.com.GetValue() )+' Anteriror: '+str( _com )+'\n'
		if _cpf and self.Acpf:	self.dados_alterados +="CPF-CNPJ..........: "+str( self.cpf.GetValue() )+' Anteriror: '+str( _cpf )+'\n'
		if _cor and self.Acor:	self.dados_alterados +="Nome correntista..: "+str( self.cor.GetValue() )+' Anteriror: '+str( _cor )+'\n'
		if _ncm and self.Ancm:	self.dados_alterados +="Numero comprovante: "+str( self.ncm.GetValue() )+' Anteriror: '+str( _ncm )+'\n'

		self.lista_alteracao =  _vpc, _fpg, _ven, _fbn, _cpf, _cor, _ban, _age, _con, _che, _com, dadosAltera, _ncm, TT, PC, IL

		if not self.dados_alterados:	alertas.dia( self, "Não houve alterações!!\n"+(" "*100),"Contas Areceber")
		if self.dados_alterados and len( login.filialLT[ self.flconrc ][35].split(";") ) >=49 and login.filialLT[ self.flconrc ][35].split(";")[48] == 'T':

			receb = wx.MessageDialog(self.painel,"{ Remoto }>->Confirme para gravar as alterações do título...\n"+(" "*100),"Contas Areceber: Alterações de Títulos",wx.YES_NO|wx.NO_DEFAULT)
			if receb.ShowModal() ==  wx.ID_YES:


				cliente = "Numero registro: "+str( self.rgc.GetValue() )+'\n'+\
				"CPF-CNPJ.......: "+str( self.doc.GetValue() )+'\n'+\
				"Nome do cliente: "+str( self.nmc.GetValue() )
				
				autorizacoes._inform = cliente+'\n\n{ Contas Areceber }-->Dados alterados:\n'+str( self.dados_alterados )
				autorizacoes._autori = '' #dadosAltera
				autorizacoes.auTAnTe = ''
				autorizacoes._cabeca = ''
				autorizacoes._Tmpcmd = ''
				autorizacoes.moduloP = 50
													
				autorizacoes.filiala = self.flconrc
				auto_frame = autorizacoes(parent=self,id=-1)
				auto_frame.Centre()
				auto_frame.Show()	

		else:
			
			receb = wx.MessageDialog(self.painel,"{ Local }>->Confirme para gravar as alterações do título...\n"+(" "*100),"Contas Areceber: Alterações de Títulos",wx.YES_NO|wx.NO_DEFAULT)
			if receb.ShowModal() ==  wx.ID_YES:	self.salvarAlteracao( '' )

	def salvarAlteracao(self, autorizador ):
			
			_l = self.lista_alteracao
			_a = ""
			if autorizador and self.dados_alterados:	_a = "{ Pedido de autorizacao remoto }\n"+self.dados_alterados+"\n"+autorizador+"\n\n"
			
			conn = sqldb()
			sql  = conn.dbc("Caixa: Consulta de DAVs", fil = self.flconrc, janela = self.painel )

			if sql[0] == True:
				
				grva = False
				try:
					
					gravar = "UPDATE receber SET rc_apagar=%s,rc_formap=%s,rc_vencim=%s,rc_bandei=%s,rc_chdocu=%s,\
					rc_chcorr=%s,rc_chbanc=%s,rc_chagen=%s,rc_chcont=%s,rc_chnume=%s,\
					rc_chcomp=%s,rc_histor=%s,rc_autori=%s WHERE rc_ndocum=%s and rc_nparce=%s and rc_regist=%s"

					grv = sql[2].execute(gravar,(_l[0],_l[1],_l[2],_l[3],_l[4],_l[5],_l[6],_l[7],_l[8],_l[9],_l[10],_a+_l[11],_l[12],_l[13],_l[14],_l[15]))

					sql[1].commit()
					grva = True

				except Exception, _reTornos:
					sql[1].rollback()
		
				conn.cls(sql[1])

				if grva == False:	alertas.dia(self.painel,u"Alteração do título não concluida !!\n \nRetorno: "+str(_reTornos),"Contas Areceber: Alteração de Títulos")	
				if grva == True:	alertas.dia(self.painel,u"Alteração do título concluida !!\n","Contas Areceber: Alteração de Títulos")	
				if grva == True:	self.sair(wx.EVT_BUTTON)
			
	def desenho(self,event):
		
		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#A52A2A") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Contas Areceber { Alteração de Títulos }", 0,478, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(13, 1,   655, 475, 0) #-->[ Consulta ]
		dc.DrawRoundedRectangle(16, 95,  649, 100, 0) #-->[ Consulta ]
		dc.DrawRoundedRectangle(16, 220, 649, 88,  3) #-->[ Consulta ]
		dc.DrawRoundedRectangle(16, 330, 649, 140, 3) #-->[ Consulta ]

class DescontoTitulo(wx.Frame):
	
	Filial = ''
	
	def __init__(self, parent,id):
		
		self.p = parent
		self.s = False
		self.R = numeracao()

		self.Bnfr = self.Bidf = self.Bdoc = ''
		wx.Frame.__init__(self, parent, id, 'Contas A Receber: Desconto de Títulos { Portador }', size=(900,535), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style=wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)
		
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		self.cadDesconto = DSListCtrl(self.painel, 300 ,pos=(16,2), size=(880,345),
							style=wx.LC_REPORT
							|wx.LC_VIRTUAL
							|wx.BORDER_SUNKEN
							|wx.LC_HRULES
							|wx.LC_VRULES
							|wx.LC_SINGLE_SEL
							)
		self.cadDesconto.SetBackgroundColour('#BEA0A0')
		self.cadDesconto.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.cadDesconto.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.SelecionarItem)
		self.cadDesconto.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)

		#----------:[ Cadastro de Banco ]
		self.ListaBanco = wx.ListCtrl(self.painel, 400, pos=(450,420), size=(446,108),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaBanco.SetBackgroundColour('#D2BDBD')
		self.ListaBanco.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ListaBanco.InsertColumn(0, 'Registro',  width=60)
		self.ListaBanco.InsertColumn(1, 'Descrição', width=200)
		self.ListaBanco.InsertColumn(2, 'Nº Banco',  width=60)
		self.ListaBanco.InsertColumn(3, 'Agência',   width=60)
		self.ListaBanco.InsertColumn(4, 'Nº Conta',  width=80)
		self.ListaBanco.InsertColumn(5, 'CPF-CNPJ',  width=110)

		wx.StaticText(self.painel,-1, "Data Inicial", pos=(153,485)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Data Final",   pos=(313,485)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Fornecedor-Banco",   pos=(20, 353)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Ocorrências:", pos=(450,353)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Valor Total:", pos=(730,353)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		wx.StaticText(self.painel,-1, "Banco",        pos=(453,370)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Agência",      pos=(503,370)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Nº Conta",     pos=(573,370)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Comp",         pos=(643,370)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Nº Cheque",    pos=(693,370)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Boleto {Nosso Número}", pos=(763,370)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.TTs = wx.StaticText(self.painel,-1, "", pos=(695,353))
		self.TTs.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TTs.SetForegroundColour('#256EB5')

		fil = wx.StaticText(self.painel,-1, "Filial: "+str( self.Filial ), pos=(353,450))
		fil.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		fil.SetForegroundColour('#7F7F7F')

		""" Nome Correntista """
		self.cor = wx.StaticText(self.painel,-1, pos=(453,405))
		self.cor.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cor.SetForegroundColour('#005400')

		self.cha = wx.CheckBox(self.painel, -1,  "Cheque Avista   ", pos=(18,395))
		self.chp = wx.CheckBox(self.painel, -1,  "Cheque Predatado", pos=(18,420))
		self.bol = wx.CheckBox(self.painel, -1,  "Boleto          ", pos=(18,445))
		self.fat = wx.CheckBox(self.painel, -1,  "Carteira        ", pos=(18,470))

		self.dep = wx.RadioButton(self.painel,-1,"Deposito",  pos=(150,395),style=wx.RB_GROUP)
		self.des = wx.RadioButton(self.painel,-1,"Desconto ", pos=(150,420))
		self.pag = wx.RadioButton(self.painel,-1,"Pagamento", pos=(150,445))

		self.liq = wx.CheckBox(self.painel, -1,  "Liquidar Títulos", pos=(18,502))

		self.dindicial = wx.DatePickerCtrl(self.painel,-1,  pos=(150,498), size=(130,27), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1,  pos=(310,498), size=(130,27))

		self.oco = wx.TextCtrl(self.painel,-1,'',pos=(520,348),size=(95,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.oco.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.oco.SetBackgroundColour('#E5E5E5')
		self.oco.SetForegroundColour('#256EB5')

		self.vTT = wx.TextCtrl(self.painel,-1,'0.00',pos=(797,348),size=(100,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.vTT.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vTT.SetBackgroundColour('#E5E5E5')
		self.vTT.SetForegroundColour('#256EB5')
		
		self.nmf = wx.TextCtrl(self.painel,200,'',pos=(18,365),size=(392,22),style=wx.TE_PROCESS_ENTER)
		self.nmf.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.nmf.SetBackgroundColour('#E5E5E5')
		self.nmf.SetForegroundColour('#256EB5')

		self.ban = wx.TextCtrl(self.painel,-1,'',pos=(450,383),size=(40,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.ban.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ban.SetBackgroundColour('#BFBFBF')
		self.ban.SetForegroundColour('#005400')

		self.age = wx.TextCtrl(self.painel,-1,'',pos=(500,383),size=(60,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.age.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.age.SetBackgroundColour('#BFBFBF')
		self.age.SetForegroundColour('#005400')

		self.ncc = wx.TextCtrl(self.painel,-1,'',pos=(570,383),size=(60,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.ncc.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ncc.SetBackgroundColour('#BFBFBF')
		self.ncc.SetForegroundColour('#005400')

		self.ncp = wx.TextCtrl(self.painel,-1,'',pos=(640,383),size=(40,18), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.ncp.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ncp.SetBackgroundColour('#BFBFBF')
		self.ncp.SetForegroundColour('#005400')

		self.nch = wx.TextCtrl(self.painel,-1,'',pos=(690,383),size=(60,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.nch.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nch.SetBackgroundColour('#BFBFBF')
		self.nch.SetForegroundColour('#005400')

		self.nos = wx.TextCtrl(self.painel,-1,'',pos=(760,383),size=(137,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.nos.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nos.SetBackgroundColour('#BFBFBF')
		self.nos.SetForegroundColour('#005400')

		self.cha.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.chp.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.bol.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fat.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.liq.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.dep.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.des.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pag.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.procfr = wx.BitmapButton(self.painel,100, wx.Bitmap("imagens/procurapp.png",  wx.BITMAP_TYPE_ANY), pos=(413,359), size=(30,28))

		voltar = wx.BitmapButton(self.painel,101, wx.Bitmap("imagens/voltam.png",   wx.BITMAP_TYPE_ANY), pos=(250,400), size=(40,38))
		procur = wx.BitmapButton(self.painel,102, wx.Bitmap("imagens/procurap.png", wx.BITMAP_TYPE_ANY), pos=(300,400), size=(40,38))
		editar = wx.BitmapButton(self.painel,103, wx.Bitmap("imagens/alterarm.png", wx.BITMAP_TYPE_ANY), pos=(350,400), size=(40,38))
		gravar = wx.BitmapButton(self.painel,104, wx.Bitmap("imagens/savem.png",    wx.BITMAP_TYPE_ANY), pos=(400,400), size=(40,38))

		self.secall = wx.BitmapButton(self.painel,105, wx.Bitmap("imagens/selectall.png",  wx.BITMAP_TYPE_ANY), pos=(250,440), size=(40,38))
		fornec = wx.BitmapButton(self.painel,106, wx.Bitmap("imagens/fornecedor.png", wx.BITMAP_TYPE_ANY), pos=(300,440), size=(40,38))

		self.cha.SetValue(True)
		self.chp.SetValue(True)

		self.nmf.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.procfr.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.secall.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.cadDesconto.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ListaBanco.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		procur.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		editar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		gravar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		fornec.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.nmf.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.procfr.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.secall.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.cadDesconto.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ListaBanco.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		procur.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		editar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		gravar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		fornec.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		fornec.Bind(wx.EVT_BUTTON, self.fornecedor)
		procur.Bind(wx.EVT_BUTTON, self.selecionar)
		editar.Bind(wx.EVT_BUTTON, self.edicaoTitulo)
		gravar.Bind(wx.EVT_BUTTON, self.gravarBordero)
		
		self.procfr.Bind(wx.EVT_BUTTON, self.pesquisaFornecedor)
		self.secall.Bind(wx.EVT_BUTTON, self.selecionaTudo)
		
		self.nmf.Bind(wx.EVT_TEXT_ENTER, self.pesquisaFornecedor)
		self.nmf.Bind(wx.EVT_LEFT_DCLICK, self.pesquisaFornecedor)

		self.cha.Bind(wx.EVT_CHECKBOX, self.evCombo)
		self.chp.Bind(wx.EVT_CHECKBOX, self.evCombo)
		self.bol.Bind(wx.EVT_CHECKBOX, self.evCombo)
		self.fat.Bind(wx.EVT_CHECKBOX, self.evCombo)

		self.dep.Bind(wx.EVT_RADIOBUTTON, self.evRadio)
		self.des.Bind(wx.EVT_RADIOBUTTON, self.evRadio)
		self.pag.Bind(wx.EVT_RADIOBUTTON, self.evRadio)
 
		self.evRadio(wx.EVT_BUTTON)
		self.R.selBancos(self, Filiais = self.Filial )
		self.selecionar(wx.EVT_BUTTON)
		
	def sair(self,event):	self.Destroy()
	def evCombo(self,event):	self.selecionar(wx.EVT_BUTTON)
	def evRadio(self,event):
		
		_fr = _bf = _bn = True
		if self.dep.GetValue() == True:	_fr = _bf = False
		if self.des.GetValue() == True:	_fr = _bf = False
		if self.pag.GetValue() == True:	_bn = False

		self.nmf.Enable( _fr )
		self.procfr.Enable( _bf )
		self.ListaBanco.Enable( _bn )

	def passagem(self,event):

		indice = self.cadDesconto.GetFocusedItem()
		nCor   = ''
		if self.cadDesconto.GetItem(indice,16).GetText() != "":	nCor = "Correntista:  "+self.cadDesconto.GetItem(indice,16).GetText()
		self.ban.SetValue(self.cadDesconto.GetItem(indice,10).GetText())
		self.age.SetValue(self.cadDesconto.GetItem(indice,11).GetText())
		self.ncc.SetValue(self.cadDesconto.GetItem(indice,12).GetText())
		self.ncp.SetValue(self.cadDesconto.GetItem(indice,13).GetText())
		self.nch.SetValue(self.cadDesconto.GetItem(indice,14).GetText())
		self.cor.SetLabel(nCor)
		self.nos.SetValue(self.cadDesconto.GetItem(indice,16).GetText())

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	sb.mstatus(u"  Procura Fornecedor",0)
		elif event.GetId() == 101:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 102:	sb.mstatus(u"  Procurar Titulos por data de Vencimento",0)
		elif event.GetId() == 103:	sb.mstatus(u"  Editar Título { Alterar }",0)
		elif event.GetId() == 104:	sb.mstatus(u"  Gravar-Salvar-Finalizar Títulos Selecionados",0)
		elif event.GetId() == 105:	sb.mstatus(u"  Marca e Desmaca Todos os Títulos para Desconto,Deposito e/ou Pagamentos",0)
		elif event.GetId() == 106:	sb.mstatus(u"  Acesso ao Cadastro de Fornecedores",0)
		elif event.GetId() == 200:	sb.mstatus(u"  Entre com Nome do Fornecedor para Procurar",0)
		elif event.GetId() == 300:	sb.mstatus(u"  Click Duplo para Marcar-Desmarca Títulos para Desconto,Deposito e/ou Pagamentos",0)
		elif event.GetId() == 400:	sb.mstatus(u"  Click para Selecionar o Banco",0)
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Contas a Receber: Desconto de Títulos { Portador }",0)
		event.Skip()

	def edicaoTitulo(self,event):
		
		indice = self.cadDesconto.GetFocusedItem()
		nTiTul = self.cadDesconto.GetItem(indice, 2).GetText().split('/')[0]
		nLanca = self.cadDesconto.GetItem(indice, 2).GetText().split('/')[1]
		idLanc = self.cadDesconto.GetItem(indice,17).GetText()
		status = self.cadDesconto.GetItem(indice, 7).GetText()
		
		consultaReceber.nTitulo = nTiTul,nLanca,idLanc,status
		consultaReceber.flconrc = self.Filial

		edit_frame=consultaReceber(parent=self,id=-1)
		edit_frame.Centre()
		edit_frame.Show()

	def fornecedor(self,event):

		fornecedores.pesquisa = False
		fornecedores.NomeFilial = self.Filial
		fornecedores.transportar= False
		
		for_frame=fornecedores(parent=self,id=-1)
		for_frame.Centre()
		for_frame.Show()

	def SelecionarItem(self,event):	self.selecao(2)
	def selecionaTudo(self,event):
		
		if self.s == False:
			self.secall.SetBitmapLabel (wx.Bitmap('imagens/unselect.png'))
			self.s = True

		elif self.s == True:
			self.secall.SetBitmapLabel (wx.Bitmap('imagens/selectall.png'))
			self.s = False

		self.selecao(1)
		
	def selecao(self,_op):

		rgAtua = self.cadDesconto.GetFocusedItem()
		nRegis = self.cadDesconto.GetItemCount()
		indice = 0

		_registros = 0
		relacao = {}

		_baixa = "BAIXA"
		if self.s == False:	_baixa = ''
		
		for i in range(nRegis):

			if _op == 2:
				
				_baixa = ""
				if indice == rgAtua:	_baixa = "BAIXA"
				if self.cadDesconto.GetItem(indice,9).GetText() == "BAIXA":	_baixa = "BAIXA"
				if self.cadDesconto.GetItem(indice,9).GetText() == "BAIXA" and indice == rgAtua:	_baixa = ""
				 
			a0 = self.cadDesconto.GetItem(indice,0).GetText()				
			a1 = self.cadDesconto.GetItem(indice,1).GetText()				
			a2 = self.cadDesconto.GetItem(indice,2).GetText()				
			a3 = self.cadDesconto.GetItem(indice,3).GetText()				
			a4 = self.cadDesconto.GetItem(indice,4).GetText()				
			a5 = self.cadDesconto.GetItem(indice,5).GetText()				
			a6 = self.cadDesconto.GetItem(indice,6).GetText()				
			a7 = self.cadDesconto.GetItem(indice,7).GetText()
			a8 = self.cadDesconto.GetItem(indice,8).GetText()
			a9 = self.cadDesconto.GetItem(indice,9).GetText()
			a10= self.cadDesconto.GetItem(indice,10).GetText()
			a11= self.cadDesconto.GetItem(indice,11).GetText()
			a12= self.cadDesconto.GetItem(indice,12).GetText()
			a13= self.cadDesconto.GetItem(indice,13).GetText()
			a14= self.cadDesconto.GetItem(indice,14).GetText()
			a15= self.cadDesconto.GetItem(indice,15).GetText()
			a16= self.cadDesconto.GetItem(indice,16).GetText()
			a17= self.cadDesconto.GetItem(indice,17).GetText()
			a18= self.cadDesconto.GetItem(indice,18).GetText()
			indice +=1

			relacao[_registros] = a0, a1, a2, a3, a4, a5, a6, a7, a8, _baixa, a10, a11, a12, a13, a14, a15, a16, a17, a18
			_registros +=1

		DSListCtrl.itemDataMap  = relacao
		DSListCtrl.itemIndexMap = relacao.keys()
		
		self.cadDesconto.Refresh()
		self.Totaliza()

	def Totaliza(self):

		nRegis = self.cadDesconto.GetItemCount()
		indice = 0
		nTiTu  = 0
		valor  = Decimal('0.00')
		
		for i in range(nRegis):
			
			if self.cadDesconto.GetItem(indice,9).GetText() == "BAIXA":
				
				valor += Decimal( self.cadDesconto.GetItem(indice,1).GetText().replace(',','') )
				nTiTu +=1

			indice +=1
		self.vTT.SetValue(format(valor,','))
		self.TTs.SetLabel("{ "+str(nTiTu)+" }")
		
	def pesquisaFornecedor(self,event):

		fornecedores.pesquisa = True
		fornecedores.nmFornecedor = self.nmf.GetValue()
		fornecedores.NomeFilial   = self.Filial
		fornecedores.transportar  = False

		frp_frame=fornecedores(parent=self,id=event.GetId())
		frp_frame.Centre()
		frp_frame.Show()

	def ajustafrn(self, __dc, __ft, __nm, __ie, __im, __cn, __id, __rp, __pc ):

		self.nmf.SetValue(__nm)
		self.Bnfr = __nm #-:Nome do Fornecedor 
		self.Bidf = __id #-:Numero do Registro
		self.Bdoc = __dc #-:CPF-CNPJ
	
	def selecionar(self,event):
		
		conn = sqldb()
		sql  = conn.dbc("Caixa: Consulta de DAVs", fil = self.Filial, janela = self.painel )
		if sql[0] == True:

			dI = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			dF = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

			achei = "SELECT * FROM receber WHERE rc_vencim>='"+str( dI )+"' and rc_vencim<='"+str( dF )+"' and rc_status='' and rc_border='' ORDER BY rc_vencim"

			lsele = sql[2].execute(achei)
			lista = sql[2].fetchall()
			conn.cls(sql[1])

			condicao = ""
			_registros = 0
			relacao = {}
				
			for i in lista:
				
				avancar = False
				if self.cha.GetValue() == True and i[6][:2] == "02":	avancar = True
				if self.chp.GetValue() == True and i[6][:2] == "03":	avancar = True
				if self.bol.GetValue() == True and i[6][:2] == "06":	avancar = True
				if self.fat.GetValue() == True and i[6][:2] == "07":	avancar = True

				if avancar == True:

					lanca = format(i[7],"%d/%m/%Y")+' '+str(i[8])+' '+str(i[10])
					venci = format(i[26],"%d/%m/%Y")
					valor = format(i[5],',')

					relacao[_registros] = venci, valor, i[1]+"/"+i[3], i[59], i[6], i[13], i[12], i[35], lanca, '', i[30], i[31], i[32], i[57], i[33], i[29], i[67], i[0], i[24]
					_registros +=1

			self.cadDesconto.SetItemCount(_registros)
			DSListCtrl.itemDataMap  = relacao
			DSListCtrl.itemIndexMap = relacao.keys()
			self.oco.SetValue(str(_registros))

	def gravarBordero(self,event):

		if len( self.TTs.GetLabel().split(' ') ) <= 1 or self.cadDesconto.GetItemCount() == 0:
			
			alertas.dia(self.painel,u"Nenhum Título Selecionado e/ou Lista vazia...\n"+(" "*120),"Contas Areceber: Desconto de Títulos { Portador }")
			return

		nR = self.TTs.GetLabel().split(' ')[1]

		nRegis = self.cadDesconto.GetItemCount()
		nBanco = self.ListaBanco.GetFocusedItem()
		indice = 0
		relaca = ""
		TipoDs = ""
		grvDes = False
		
		EMD = datetime.datetime.now().strftime("%Y-%m-%d") #---------->[ Data de Recebimento ]
		DHO = datetime.datetime.now().strftime("%T") #---------------->[ Hora do Recebimento ]

		if self.dep.GetValue() == True or self.des.GetValue() == True:

			INS = self.ListaBanco.GetItem( nBanco, 1 ).GetText() #-:Nome do Fornecedor 
			REG = self.ListaBanco.GetItem( nBanco, 0 ).GetText() #-:Numero do Registro
			DOC = self.ListaBanco.GetItem( nBanco, 5 ).GetText() #-:CPF-CNPJ

			if self.dep.GetValue() == True:	TipoDs = u"{ Deposito }"
			if self.des.GetValue() == True:	TipoDs = u"{ Desconto }"
		
		if self.pag.GetValue() == True:

			INS = self.Bnfr #-:Nome do Fornecedor 
			REG = self.Bidf #-:Numero do Registro
			DOC = self.Bdoc #-:CPF-CNPJ
			TipoDs = u"{ Pagamentos }"
			
			""" Pagamentos sem registros """
			if REG == '' and DOC == '' and self.nmf.GetValue() == '':
				alertas.dia(self.painel,TipoDs+u"\n\nPagamento sem registro do portador\nEntre com o nome do portador no campo fonecedor-Banco\n"+(" "*110),u"Contas Areceber: Desconto de Títulos { Portador }")
				return
		
			if REG == '' and DOC == '' and self.nmf.GetValue() !='':

				bai = wx.MessageDialog(self.painel,u"{ Pagamentos SEM REGISTRO }\n\nNome do portador: "+str( self.nmf.GetValue().upper() )+u"\nConfirme para continuar...\n"+(" "*120),u"Contas Areceber: Desconts { Pagamentos }",wx.YES_NO|wx.NO_DEFAULT)
				if bai.ShowModal() !=  wx.ID_YES:	return
				INS = self.nmf.GetValue()
				REG = u"Sem Reg"
				DOC = u"Sem Registro"

		moTivo = ""
		if INS == '':	moTivo += u"1 - Nome do Fornecedor-Banco, Estar vazio\n"
		if REG == '':	moTivo += u"2 - Sem Numero de Registro p/Fornecedor-Banco\n"
		if DOC == '':	moTivo += u"3 - CPF-CNPJ do Fornecedor-Banco, Estar vazio\n"

		if moTivo != "":
			
			alertas.dia(self.painel,TipoDs+"\n\n"+moTivo+(" "*100),u"Contas Areceber: Desconto de Títulos { Portador }")
			return

		""" Gravar Dados """
		if   self.dep.GetValue() == True or self.des.GetValue() == True:
			informa = TipoDs+u"\nDados do Banco:\n\nNºRegistro: "+REG+"\nCPF-CNPJ: "+DOC+u"\nDescrição: "+INS+u"\n\n\nConfirme para finalizar procedimento!!"

		elif self.pag.GetValue() == True:
			informa = TipoDs+u"\nDados do Fornecedor:\n\nNºRegistro: "+REG+u"\nCPF-CNPJ: "+DOC+u"\nDescrição: "+INS+u"\n\n\nConfirme para finalizar procedimento!!"

		liquidacao = u"[ Transferencia de títulos para "+ TipoDs +" ]\n\n"
		if self.liq.GetValue():	liquidacao = u"[ Transferencia de títulos para "+ TipoDs +u" com liquidação automatica ]\n\n"

		""" Confirmacao """
		receber = wx.MessageDialog(self.painel,liquidacao+informa+"\n"+(" "*160),u"Contas Areceber: Desconto de Títulos { Portador }",wx.YES_NO|wx.NO_DEFAULT)
		if receber.ShowModal() ==  wx.ID_YES:

			vlr = self.vTT.GetValue().replace(',','')
			relaca  +=nR+"|"+vlr
			
			for r in range(nRegis):
				
				if self.cadDesconto.GetItem(indice,9).GetText() == "BAIXA":	relaca +='|'+self.cadDesconto.GetItem(indice,2).GetText()
				indice +=1
			
			nBordero = self.R.numero("9","Número do Bordero",self.painel, self.Filial )
			indice   = 0

			if nBordero !=0:

				brdo = str(nBordero).zfill(10)

				if self.dep.GetValue() == True:	Tpg = "1"
				if self.des.GetValue() == True:	Tpg = "2"
				if self.pag.GetValue() == True:	Tpg = "3"
				
				conn  = sqldb()
				sql   = conn.dbc(u"Contas Areceber: Bordero de Desconto-Pagamento", fil = self.Filial, janela = self.painel )

				if sql[0] == True:
					
					try:
						
						for i in range(nRegis):
							
							if self.cadDesconto.GetItem( i, 9 ).GetText() == "BAIXA":
															
								nTiTulo = self.cadDesconto.GetItem( i, 2).GetText().split('/')
								gravar_baixas = "UPDATE receber SET rc_border=%s,rc_databo=%s,rc_horabo=%s,rc_loginu=%s,rc_uscodi=%s,\
								rc_instit=%s,rc_rginst=%s,rc_docins=%s,rc_borrtt=%s,rc_tipods=%s WHERE rc_ndocum=%s and rc_nparce=%s"

								gravar_liquidacao = "UPDATE receber SET rc_bxcaix=%s,rc_bxlogi=%s,rc_vlbaix=%s,rc_dtbaix=%s,rc_hsbaix=%s,\
								rc_formar=%s,rc_status=%s,rc_canest=%s,rc_recebi=%s,rc_baixat=%s,rc_modulo=%s,rc_acresc=%s,\
								rc_border=%s,rc_databo=%s,rc_horabo=%s,rc_loginu=%s,rc_uscodi=%s,\
								rc_instit=%s,rc_rginst=%s,rc_docins=%s,rc_borrtt=%s,rc_tipods=%s WHERE rc_ndocum=%s and rc_nparce=%s"

								valor = "insert into ocorren (oc_docu,oc_usar,oc_corr,oc_tipo,oc_inde)\
								values (%s,%s,%s,%s,%s)"			

								ven = str( self.cadDesconto.GetItem( i, 0 ).GetText() )
								vlr = str( self.cadDesconto.GetItem( i, 1 ).GetText().replace(',','') )
								fRc = self.cadDesconto.GetItem( i, 4 ).GetText()
								fll = str( self.cadDesconto.GetItem( i, 18 ).GetText() )

								usa = login.usalogin
								cus = login.uscodigo

								_lan  = datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin
								_tip  = "Contas AReceber"
								_oco  = "Liquidacao de titulos em bordero\n"+\
								"Lancamento: "+nTiTulo[0]+\
								"\n\nDAV/Comanda: "+nTiTulo[0]+\
								"\nVencimento: "+ven+\
								"\nValor: "+vlr+\
								"\nForma Pagamento: "+fRc+\
								"\nValor Baixado: "+vlr
		
								if self.liq.GetValue():

									sql[2].execute( gravar_liquidacao, ( cus, usa, vlr, EMD, DHO, fRc, '2', 'Baixa por liquidacao', '1', '2', login.rcmodulo, '0.00',\
									str(nBordero).zfill(10),EMD,DHO,login.usalogin,login.uscodigo,INS,REG,DOC,relaca,Tpg, nTiTulo[0], nTiTulo[1] ) )

									sql[2].execute( valor, ( nTiTulo[0], _lan, _oco, _tip, fll ) )

								else:
									sql[2].execute( gravar_baixas, ( str(nBordero).zfill(10),EMD,DHO,login.usalogin,login.uscodigo,INS,REG,DOC,relaca,Tpg, nTiTulo[0], nTiTulo[1] ) )
									
							indice +=1	

						sql[1].commit()
						grvDes = True
					
					except Exception as _reTornos:

						if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
						sql[1].rollback()

					conn.cls(sql[1])
					
					if grvDes == False:	alertas.dia(self.painel,u"Inclusão do bordero em desconto-pagamento não concluida\n\nRetorno: "+ _reTornos +(" "*160),u"Contas Areceber: Desconto de Títulos { Portador }")	
					if grvDes == True:
						
						alertas.dia(self.painel,TipoDs+u"\n\nBordero Nº "+brdo+"\n"+(" "*160),u"Contas Areceber: Desconto de Títulos { Portador }")	
						self.sair(wx.EVT_BUTTON)
		
	def desenho(self,event):
		
		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#D03F3F") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Contas Areceber: Desconto de Títulos { Portador }", 0,532, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(16, 350,  430, 40, 2) #-->[ Consulta ]
		dc.DrawRoundedRectangle(16, 393,  430, 135, 2) #-->[ Consulta ]

class DSListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
       		
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

		self.il = wx.ImageList(16, 16)
		for k,v in diretorios.pasta_icons.items():
			s="self.%s= self.il.Add(wx.Bitmap(%s))" % (k,v)
			exec(s)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr2 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour("#BD9999")
		self.attr2.SetBackgroundColour("#C4DAC4")

		self.InsertColumn(0, u'Vencimento', format=wx.LIST_ALIGN_LEFT, width=120)
		self.InsertColumn(1, u'Valor',      format=wx.LIST_ALIGN_LEFT, width=90)
		self.InsertColumn(2, u'Nº Título',  format=wx.LIST_ALIGN_LEFT, width=130)
		self.InsertColumn(3, u'NFe-NF',     format=wx.LIST_ALIGN_LEFT, width=60)
		self.InsertColumn(4, u'Forma de Pagamento', width=170)
		self.InsertColumn(5, u'Fantasia',   width=180)
		self.InsertColumn(6, u'Descrição do Cliente', width=500)
		self.InsertColumn(7, u'Status',               width=50)
		self.InsertColumn(8, u'Emissão',              width=200)
		self.InsertColumn(9, u'Baixar',               width=70)
		self.InsertColumn(10,u'Nº Banco',  width=70)
		self.InsertColumn(11,u'Agência',   width=70)
		self.InsertColumn(12,u'Nº Conta',  width=70)
		self.InsertColumn(13,u'Comp',      width=70)
		self.InsertColumn(14,u'Nº Cheque', width=70)
		self.InsertColumn(15,u'Nome Correntista', width=500)
		self.InsertColumn(16,u'Nº Boleto',        width=200)
		self.InsertColumn(17,u'ID-Lançamento',    width=200)
		self.InsertColumn(18,u'Filial',    width=100)
			
	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index

			return lista

		except Exception, _reTornos:	pass

	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		if self.itemIndexMap != []:

			index=self.itemIndexMap[item]
			if self.itemDataMap[index][9] == "BAIXA":	return self.attr2
			else:
				if item % 2:	return self.attr1

	def GetListCtrl(self):	return self			

	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		if self.itemDataMap[index][9] == "BAIXA":	return self.w_idx
		else:	return self.i_orc
			

class RelatorioDiversos(wx.Frame):

	_id = ''
	Filial = ''
	docume = ''
	nomecl = ''

	def __init__(self, parent,id):
		
		self.p = parent
		self.p.Disable()
		self.guardafili = self.Filial

		self.vlrcha = self.vlrchp = self.vlrcdb = self.vlrccr = self.vlrbol = self.vlrcar = self.vlrdep = Decimal('0.00')
		self.vlrfin = self.vlrtic = self.vlrpgc = self.vlrloc = self.vlrdin = self.TAreceber = self.vlTLiq = Decimal('0.00')

		""" Borderô """
		self.som = self.fvb = self.vlb = self.mvb = self.TCb = "" 

		wx.Frame.__init__(self, parent, id, 'Contas Areceber: Cheques Estornados', size=(950,530), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.CHQEstornado = CHQListCtrl(self.painel, 300 ,pos=(12,0), size=(938,270),
						style=wx.LC_REPORT
						|wx.LC_VIRTUAL
						|wx.BORDER_SUNKEN
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)

		self.CHQEstornado.SetBackgroundColour('#6D8298')
		self.CHQEstornado.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.CHQEstornado.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.CHQEstornado.Bind(wx.EVT_RIGHT_DOWN, self.passagem) #-: Pressionamento da Tecla Direita do Mouse
		self.CHQEstornado.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.gravarAlterar)

		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		wx.StaticText(self.painel,-1, u"Tipo de Relação-Relatório", pos=(18, 275)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Forma de Pagamento",  pos=(18, 315)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Período Inicial",     pos=(18, 407)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Período Final",       pos=(18, 451)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Nº Autorização",      pos=(345,450)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Nome da Bandeira",    pos=(483,450)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Relação de Usuários", pos=(693,450)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Relação de filiais\nLocais-Remoto", pos=(500,275)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self._oc = wx.StaticText(self.painel,-1,u"Ocorrências", pos=(170,275))
		self._oc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self._oc.SetForegroundColour('#1C5E9D')

		direto = wx.StaticText(self.painel,-1,u"D I R E T O", pos=(863,500))
		direto.SetFont(wx.Font(12,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		direto.SetForegroundColour('#BFBFBF')

		if str( self.p.bdnBo.GetValue() ).strip() !="":
			
			self.brd = wx.StaticText(self.painel,-1,u"Nº Borderô: { "+str( self.p.bdnBo.GetValue() )+" }", pos=(790,280))
			self.brd.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.brd.SetForegroundColour('#1C5E9D')

		self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(15,420), size=(120,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(15,464), size=(120,25))
		self.dindicial.SetValue(self.p.dindicial.GetValue())
		self.datafinal.SetValue(self.p.datafinal.GetValue())

		self.historico = wx.TextCtrl(self.painel,-1,value='', pos=(300,305), size=(558,118),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.historico.SetForegroundColour('#DEDE96')
		self.historico.SetBackgroundColour('#6D8298')
		self.historico.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.comprovan = wx.TextCtrl(self.painel,200,value="",pos=(342,462),size=(123,22))
		self.comprovan.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		self.comprovan.SetForegroundColour('#4D4D4D')
		self.comprovan.SetBackgroundColour('#E5E5E5')

		self.bandeiras = wx.TextCtrl(self.painel,201,value="",pos=(480,462),size=(200,22), style = wx.TE_READONLY)
		self.bandeiras.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		self.bandeiras.SetForegroundColour('#4D4D4D')
		self.bandeiras.SetBackgroundColour('#E5E5E5')

		informecliente = str( self.docume ) +' '+ str( self.nomecl )
		self.pesquisa_periodo = wx.CheckBox(self.painel, 115 , "Pesquisar período",   pos=(14,357))
		self.totaliza_cliente = wx.CheckBox(self.painel, 117 , "Totalizar p/cliente", pos=(14,380))
		
		self.rFilial = wx.CheckBox(self.painel, 114 , "Filtrar por filial: { "+str( self.Filial )+" }", pos=(300,275))
		self.fclient = wx.CheckBox(self.painel, 124 , "Filtrar cliente: { "+str( informecliente[:100] )+" }", pos=(299,425))

		self.carteira = wx.CheckBox(self.painel, 125 , "Utilizar no relatorio de contas recebidas para filtrar o carteira das baixas", pos=(14,500))
		self.carteira.Enable(False)

		self.pesquisa_periodo.SetFont(wx.Font(8.5, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.totaliza_cliente.SetFont(wx.Font(8.5, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.rFilial.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fclient.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.carteira.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fclient.SetForegroundColour("#11799A")

		self.pesquisa_periodo.SetValue( True )
		self.rFilial.SetValue(True)
		self.comprovan.SetMaxLength(20)
		
		self.salvar = wx.BitmapButton(self.painel, 202, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(860,385), size=(40,38))				
		voltar = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltap.png",      wx.BITMAP_TYPE_ANY), pos=(860,345), size=(40,38))
		previe = wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/maximize32.png",  wx.BITMAP_TYPE_ANY), pos=(903,305), size=(40,38))				
		relato = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/report32.png",    wx.BITMAP_TYPE_ANY), pos=(903,345), size=(40,38))				
		self.ToTali = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/somar24.png",wx.BITMAP_TYPE_ANY), pos=(903,385), size=(40,38))				

		self.procur = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/relerp.png",     wx.BITMAP_TYPE_ANY), pos=(299,461), size=(40,26))				
		
		self.dCheque = wx.RadioButton(self.painel,500,"Dados do Cheque",  pos=(148,375),style=wx.RB_GROUP)
		self.dCancel = wx.RadioButton(self.painel,501,"Cancelamento ",    pos=(148,398))
		self.dRelaTi = wx.RadioButton(self.painel,502,"Titulos Baixados", pos=(148,421))
		self.dEstorn = wx.RadioButton(self.painel,503,"Obs Estorno ",     pos=(148,444))
		self.dCompro = wx.RadioButton(self.painel,504,"Comprovantes",     pos=(148,467))

		self.relvende = wx.RadioButton(self.painel,-1,"Vendedor", pos=(854,442),style=wx.RB_GROUP)
		self.relcaixa = wx.RadioButton(self.painel,-1,"Caixa",    pos=(854,467))
		
		self.relacao = ['01-Cheques Estornados','02-Contas AReceber','03-Contas Recebidas','04-Conferência dos Cartões','05-Boletos Emitidos','06-Borderô Selecionado','07-Relatório de Liquidação','08-Extrato do cliente']
		self.relator = wx.ComboBox(self.painel, -1, '',  pos=(15, 287), size=(278,27), choices = self.relacao, style=wx.NO_BORDER|wx.CB_READONLY)
		self.formapg = wx.ComboBox(self.painel, -1, '',  pos=(15, 328), size=(278,27), choices = self.p.formaspgt, style=wx.NO_BORDER|wx.CB_READONLY)
		self.vendedo = wx.ComboBox(self.painel, -1, '',  pos=(690,463), size=(160,27), choices = login.venda, style=wx.NO_BORDER|wx.CB_READONLY)

		relaFil = [""]+login.ciaRelac
		self.rlfilia = wx.ComboBox(self.painel, -1, '',  pos=(590, 275), size=(354,27), choices = relaFil,style=wx.NO_BORDER|wx.CB_READONLY)
		self.rlfilia.SetValue( self.p.rfilia.GetValue() )

		self.dCheque.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.dCancel.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.dRelaTi.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.dEstorn.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.dCompro.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.relvende.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.relcaixa.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		relato.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		previe.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.salvar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ToTali.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		relato.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		previe.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.salvar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ToTali.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.salvar.Bind(wx.EVT_BUTTON, self.gravarAlteracao)
		self.ToTali.Bind(wx.EVT_BUTTON, self.ToTaliza)
		self.procur.Bind(wx.EVT_BUTTON, self.selecionar)

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		previe.Bind(wx.EVT_BUTTON, self.aumentar)
		relato.Bind(wx.EVT_BUTTON, self.relatorios)
		
		self.dCheque.Bind(wx.EVT_RADIOBUTTON, self.observacao)
		self.dCancel.Bind(wx.EVT_RADIOBUTTON, self.observacao)
		self.dRelaTi.Bind(wx.EVT_RADIOBUTTON, self.observacao)
		self.dEstorn.Bind(wx.EVT_RADIOBUTTON, self.observacao)
		self.dCompro.Bind(wx.EVT_RADIOBUTTON, self.observacao)
		self.totaliza_cliente.Bind(wx.EVT_CHECKBOX, self.selecionar)
		self.relator.Bind(wx.EVT_COMBOBOX, self.comBox)
		self.formapg.Bind(wx.EVT_COMBOBOX, self.selecionar)
		self.vendedo.Bind(wx.EVT_COMBOBOX, self.selecionar)
		self.rFilial.Bind(wx.EVT_CHECKBOX, self.selecionar)
		self.rlfilia.Bind(wx.EVT_COMBOBOX, self.alteraFilial)

		self.bandeiras.Bind(wx.EVT_LEFT_DCLICK,  self.rBandeiras)
		self.comprovan.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.carteira.Bind(wx.EVT_CHECKBOX, self.ajusteFormas)

		self.configura()
		self.alteraFilial( wx.EVT_BUTTON )

	def ajusteFormas(self,event):
	    
	    if self.relator.GetValue().split('-')[0] == "03":
		
		if self.carteira.GetValue():
		    self.formapg.SetValue('')
		    self.formapg.Enable(False)
		    
		else:	self.formapg.Enable(True)
	    
		self.selecionar(wx.EVT_BUTTON)
		
	def alteraFilial( self, event ):
		
		RelatorioDiversos.Filial = self.rlfilia.GetValue().split('-')[0]
		
		self.rFilial.SetLabel( "Filtrar por Filial: { "+str( self.Filial )+" }" )
		self.p.rfilia.SetValue( self.rlfilia.GetValue() )

		if self.rlfilia.GetValue():	self.rFilial.SetValue( True )
		else:	self.rFilial.SetValue( False )
		if len( login.usaparam.split(";") ) >= 6 and login.usaparam.split(";")[5] == "T":	self.rFilial.Enable( False ) 

		self.p.filialRelacao( 900 )

	def sair(self,event):
		
		self.p.rfilia.SetValue( self.guardafili )
		self.p.filialRelacao( 900 )
		self.p.Enable()
		self.Destroy()

	def relatorios(self,event):

		if RelatorioDiversos._id == "08":

			mfilial = self.Filial if self.Filial else login.identifi
			if self.docume:	extrcli.extratocliente( self.docume, self, Filial = mfilial, NomeCliente = self.nomecl, fpagamento = self.formapg.GetValue() )

			self.formapg.SetValue('')
			
		elif self.CHQEstornado.GetItemCount() == 0:	alertas.dia(self.painel,u"Sem registro na lista...\n"+(" "*80),"Contas AReceber: Relação e Relatorios")
		
		else:
		
			mfilial = self.Filial
			if not self.rlfilia.GetValue():	mfilial = login.identifi
		
			rlT = relatorioSistema()
			rlT.AreceberDiversos( self.dindicial.GetValue(), self.datafinal.GetValue(), self, RelatorioDiversos._id, "CA", self.rFilial.GetValue(), Filial = mfilial )
		
	def comBox(self,event):

		RelatorioDiversos._id = self.relator.GetValue().split('-')[0]
		self.historico.SetValue('')
		
		if RelatorioDiversos._id == "08":
			
			self.CHQEstornado.DeleteAllItems()
			self.CHQEstornado.Refresh()

			self.configura()
			
		else:

			self.configura()
			self.selecionar(wx.EVT_BUTTON)
		
	def configura(self):

		self.comprovan.Enable(False)
		self.bandeiras.Enable(False)
		self.comprovan.Enable(False)
		self.salvar.Enable(False)
		self.formapg.Enable(False)
		self.fclient.Enable(False)
		self.fclient.SetValue(False)
		self.pesquisa_periodo.Enable( True )
		self.relvende.Enable( True )
		self.relcaixa.Enable( True )
		self.vendedo.Enable( True )
		self.rlfilia.Enable( True )
		self.rFilial.Enable( True )
		self.totaliza_cliente.SetValue( False )
		self.totaliza_cliente.Enable( False )
		self.carteira.Enable(False)

		simples = True
		
		if RelatorioDiversos._id == "01": #5002:
			
			self.definicao()
			self.SetTitle(u"Contas Areceber: Cheques Estornados")
			self.historico.SetBackgroundColour('#4D4D4D')
			self.CHQEstornado.SetBackgroundColour('#6D8298')
			self.carteira.SetValue(False)
			
		if RelatorioDiversos._id == "02": #5037:
	
			self.definicao()
			self.SetTitle(u"Contas Areceber: Relação de Contas Areceber")
			self.historico.SetBackgroundColour('#405164')
			self.CHQEstornado.SetBackgroundColour('#5E7FA2')
			self.formapg.Enable(True)
			if self.docume:	self.fclient.Enable( True )
			self.totaliza_cliente.Enable( True )
			self.carteira.SetValue(False)

		if RelatorioDiversos._id == "03": #5033:
			
			self.definicao()
			self.SetTitle(u"Contas Areceber: Relação de Contas Recebidas")
			self.historico.SetBackgroundColour('#33557B')
			self.CHQEstornado.SetBackgroundColour('#6892BE')
			self.formapg.Enable(True)
			self.carteira.Enable(True)

			if self.docume:	self.fclient.Enable( True )

		if RelatorioDiversos._id == "04": #5102:
			
			self.definicao()
			self.SetTitle(u"Contas Areceber: Conferência dos Cartões { Créditos e Débitos }")
			self.historico.SetBackgroundColour('#596C81')
			self.CHQEstornado.SetBackgroundColour('#89AACC')

			self.comprovan.Enable(True)
			self.bandeiras.Enable(True)
			self.comprovan.Enable(True)
			self.salvar.Enable(True)
			self.carteira.SetValue(False)

		if RelatorioDiversos._id == "05": #5106:
			
			self.definicao()
			self.SetTitle(u"Contas Areceber: Boletos Emitidos")
			self.historico.SetBackgroundColour('#596C81')
			self.CHQEstornado.SetBackgroundColour('#89AACC')
			self.carteira.SetValue(False)

		if RelatorioDiversos._id == "06": #1000:
			
			self.definicao()
			self.SetTitle(u"Contas Areceber: Borderô")
			self.historico.SetBackgroundColour('#596C81')
			self.CHQEstornado.SetBackgroundColour('#89AACC')
			self.carteira.SetValue(False)

			simples = False

		if RelatorioDiversos._id == "07": #1001:
			
			self.formapg.Enable(True)
			self.definicao()
			self.SetTitle(u"Contas Areceber: Liquidação de Títulos")
			self.historico.SetBackgroundColour('#596C81')
			self.CHQEstornado.SetBackgroundColour('#89AACC')
			if self.docume:	self.fclient.Enable( True )
			self.carteira.SetValue(False)

		if RelatorioDiversos._id == "08":
		    simples = False
		    self.carteira.SetValue(False)

		if RelatorioDiversos._id == "07":	simples = False
		self.ToTali.Enable( simples )
		
		if RelatorioDiversos._id == "07":	simples = True
		self.procur.Enable( simples )
		
		if RelatorioDiversos._id == "07":	simples = False
		self.dCheque.Enable( simples )
		self.dCancel.Enable( simples )
		self.dRelaTi.Enable( simples )
		self.dEstorn.Enable( simples )
		self.dCompro.Enable( simples )
		
		if RelatorioDiversos._id == "07":	simples = True
		self.dindicial.Enable( simples )
		self.datafinal.Enable( simples )

		if RelatorioDiversos._id == "08":
			
			self.definicao()
			self.SetTitle(u"Contas Areceber: Extrato do cliente")
			self.historico.SetBackgroundColour('#346575')
			self.CHQEstornado.SetBackgroundColour('#346575')
			self.formapg.Enable( True )

			self.relvende.Enable( simples )
			self.relcaixa.Enable( simples )
		
			self.vendedo.Enable( simples )
			self.rlfilia.Enable( simples )
			self.rFilial.Enable( simples )
			self.pesquisa_periodo.Enable( simples )

	def definicao(self):

		self.CHQEstornado = CHQListCtrl(self.painel, 300 ,pos=(15,0), size=(935,270),
						style=wx.LC_REPORT
						|wx.LC_VIRTUAL
						|wx.BORDER_SUNKEN
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)

		self.CHQEstornado.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.CHQEstornado.Bind(wx.EVT_RIGHT_DOWN, self.passagem) #-: Pressionamento da Tecla Direita do Mouse
		self.CHQEstornado.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.gravarAlterar)

	def gravarAlterar(self,event):
		
		if self._id == "04":	self.rBandeiras(wx.EVT_BUTTON)
		
	def passagem(self,event):

		indice = self.CHQEstornado.GetFocusedItem()
		estorn = self.CHQEstornado.GetItem(indice,3).GetText()
		motivo = self.CHQEstornado.GetItem(indice,6).GetText()
		
		_esTorno = ""
		if estorn !='':	_esTorno +="Estorno de Cheques: { "+str(estorn)+" }\n"
		if motivo !='':	_esTorno +="Motivo do Estorno:\n"+str(motivo)
		
		if self._id == "01":	self.historico.SetValue(_esTorno)

		if self._id == "03":

			_em = self.CHQEstornado.GetItem(indice,2).GetText()
			_vc = self.CHQEstornado.GetItem(indice,3).GetText()
			_pg = self.CHQEstornado.GetItem(indice,4).GetText()
			_vl = self.CHQEstornado.GetItem(indice,5).GetText()
			_fp = self.CHQEstornado.GetItem(indice,9).GetText()
			_fr = self.CHQEstornado.GetItem(indice,10).GetText()
			_st = self.CHQEstornado.GetItem(indice,7).GetText()

			_hs = ""
			if _st == "2":	_hs = "{ Baixa por Liquidação }\n\n"
			_hs += "Emissão.............: "+  str( _em )+\
				   "\nVencimento..........: "+str( _vc )+\
				   "\nRecebimento.........: "+str( _pg )+\
				   "\nForma de Recebimento: "+str( _fr )+"   Valor Recebido: "+str( _vl )
				   
			self.historico.SetValue(_hs)

	def aumentar(self,event):

		MostrarHistorico.TP = ""
		MostrarHistorico.hs = self.historico.GetValue()
		MostrarHistorico.TT = "Contas AReceber"
		MostrarHistorico.AQ = ""
		MostrarHistorico.FL = self.Filial

		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()
		
	def observacao(self,event):

		if self.CHQEstornado.GetItemCount() == 0:	alertas.dia(self.painel,u"Sem registro na lista...\n"+(" "*80),"Contas AReceber: Relação e Relatorios")
		else:
			indice = self.CHQEstornado.GetFocusedItem()
			if self._id == "04":	numdav = self.CHQEstornado.GetItem(indice,1).GetText().split('/')
			else:	numdav = self.CHQEstornado.GetItem(indice,1).GetText().split('/')
			
			_dav = numdav[0]
			_par = numdav[1]

			
			conn = sqldb()
			sql  = conn.dbc("Contas AReceber Relação e Relatorios", fil = self.Filial, janela = self.painel )
			
			if sql[0] == True:	

				_receber = "SELECT * FROM receber WHERE rc_ndocum='"+str( _dav )+"' and rc_nparce='"+str( _par )+"'"
				_car = sql[2].execute(_receber)
				_res = sql[2].fetchall()
				conn.cls(sql[1])

				__hisT = "Sem Historico..."
				if self._id == "04" and _res[0][66] and _res[0][66] !='':	__hisT = ( str(_res[0][66]) )
			
				if self._id != "04" and self.dCheque.GetValue() == True: # and _res[0][34] and _res[0][34] !='':
			
					__hisT = "{ Dados do Cheque }"
					if _res[0][26] != None:	__hisT += "\nVencimento......: "+str( _res[0][26].strftime("%d/%m/%Y") )
					if _res[0][28] != None:	__hisT += "\nDocumento.......: "+str( _res[0][28] )
					if _res[0][33] != None:	__hisT += "\nNº Cheque.......: "+str( _res[0][33] )
					if _res[0][30] != None:	__hisT += "\nNº Banco........: "+str( _res[0][30] )
					if _res[0][31] != None:	__hisT += "\nNº Agência......: "+str( _res[0][31] )
					if _res[0][32] != None:	__hisT += "\nNº Conta........: "+str( _res[0][32] )
					if _res[0][29] != None:	__hisT += "\nNome Correntista: "+str( _res[0][29] )

					if _res[0][34] and _res[0][34] !='':	__hisT += "\n\n{ Informações do Cheque }\n"+str( _res[0][34] )
						
				if self._id != "04" and self.dCancel.GetValue() == True and _res[0][36] and _res[0][36] !='':	__hisT = _res[0][36]	
				if self._id != "04" and self.dRelaTi.GetValue() == True and _res[0][52] and _res[0][52] !='':
						
					_ordem = 1
					nTiTul = 1
					__hisT = "{ Relação de Titulos }\n"
					_saida = _res[0][52].split('|')
					for i in _saida:
						if _ordem !=1:
							if i !='':
								__hisT +="\n"+str(nTiTul).zfill(3)+" - "+i
								nTiTul +=1
								
						_ordem +=1

				if self._id != "04" and self.dEstorn.GetValue() == True and _res[0][63] and _res[0][63] !='':	__hisT = _res[0][63]	
				if self._id != "04" and self.dCompro.GetValue() == True and _res[0][64] and _res[0][64] !='':
						
					__hisT = "{ Comprovantes de Pagamento }\n"
					__rela = _res[0][64].split('|')
					for i in __rela:
						_rl = i.split(';')
						if _rl[0] !='':	__hisT +="\n"+_rl[0]+" "+_rl[1]+" "+_rl[2]+" "+_rl[4]

				self.historico.SetValue(__hisT)

	def ToTaliza(self,event):

		if self._id != "08":
			
			nRegis = self.CHQEstornado.GetItemCount()

			self.vlrcha = self.vlrchp = self.vlrcdb = self.vlrccr = self.vlrbol = self.vlrcar = self.vlrdep = Decimal('0.00')
			self.vlrfin = self.vlrtic = self.vlrpgc = self.vlrloc = self.vlrdin = Decimal('0.00')
			
			self.TAreceber = Decimal('0.00')
			
			if nRegis !=0:
				
				indice = 0
				for i in range(nRegis):

					vlr = Decimal('0.00')
					
					if   self._id == "04" or self._id == "05" and self.CHQEstornado.GetItem(indice,8).GetText() !='':	vlr = Decimal( self.CHQEstornado.GetItem(indice,8).GetText().replace(',','') )
					elif self._id == "07":	vlr = Decimal( self.CHQEstornado.GetItem(indice,4).GetText().replace(',','') )
					elif self._id == "02":	vlr = Decimal( self.CHQEstornado.GetItem(indice,5).GetText().replace(',','') )
					elif self._id == "01":	vlr = Decimal( self.CHQEstornado.GetItem(indice,5).GetText().replace(',','') )
					elif self._id == "03":	vlr = Decimal( self.CHQEstornado.GetItem(indice,5).GetText().replace(',','') )
					elif self._id == "05":	vlr = Decimal( self.CHQEstornado.GetItem(indice,8).GetText().replace(',','') )
					else:
						
						if self.CHQEstornado.GetItem(indice,8).GetText() !='':	vlr = Decimal( self.CHQEstornado.GetItem(indice,5).GetText().replace(',','') )

					frm = self.CHQEstornado.GetItem(indice,4).GetText().split('-')[0]
					
					if self._id == "01":	frm = self.CHQEstornado.GetItem( indice,  9 ).GetText().split('-')[0]
					if self._id == "03":	frm = self.CHQEstornado.GetItem( indice, 10 ).GetText().split('-')[0]
					if self._id == "02":	frm = self.CHQEstornado.GetItem( indice,  4 ).GetText().split('-')[0]
					if self._id == "04":	frm = self.CHQEstornado.GetItem( indice,  4 ).GetText().split('-')[0]
					if self._id == "07":	frm = self.CHQEstornado.GetItem( indice,  6 ).GetText().split('-')[0]
					if self._id == "05":	frm = "06"

					if frm == "01": self.vlrdin += vlr
					if frm == "02":	self.vlrcha += vlr
					if frm == "03":	self.vlrchp += vlr
					if frm == "04":	self.vlrccr += vlr
					if frm == "05":	self.vlrcdb += vlr
					if frm == "06":	self.vlrbol += vlr
					if frm == "07":	self.vlrcar += vlr
					if frm == "08":	self.vlrfin += vlr
					if frm == "09":	self.vlrtic += vlr
					if frm == "10":	self.vlrpgc += vlr
					if frm == "11":	self.vlrdep += vlr
					if frm == "12":	self.vlrloc += vlr

					self.TAreceber += vlr
					indice +=1
				
				Totalizar = "Cartão de Crédito: "+format( self.vlrccr, ',' )+(" "*15)+"Total AReceber: "+format( self.TAreceber, ',' )+\
				"\nCartao de Débito.: "+format( self.vlrcdb ,',' )+"\nCheque Avista....: "+format( self.vlrcha, ',' )+\
				"\nCheque Predatado.: "+format( self.vlrchp ,',' )+"\nFaturado Boleto..: "+format( self.vlrbol, ',' )+\
				"\nFaturado Carteira: "+format( self.vlrcar ,',' )+"\nFinanceira.......: "+format( self.vlrfin, ',' )+\
				"\nTickete..........: "+format( self.vlrtic ,',' )+"\nPGTO c/Crédito...: "+format( self.vlrpgc, ',' )+\
				"\nDeposito em Conta: "+format( self.vlrdep ,',' )+"\nReceber Local....: "+format( self.vlrloc, ',' )+\
				"\nDinheiro.........: "+format( self.vlrdin ,',' )
				
				self.historico.SetValue(Totalizar)
			
	def rBandeiras(self,event):

		indice = self.CHQEstornado.GetFocusedItem()
		fpagam = str(self.CHQEstornado.GetItem(indice,4).GetText())
		if fpagam !='':	fpagam = "00 "+fpagam

		if fpagam == '':	alertas.dia(self.painel,u"Forma de Pagamento Vazio !!\n"+(" "*90),"Contas Areceber: Conferência")
		else:
			regBandeira.pagamento = fpagam
			regBandeira.moduloCha = "CFR"

			ban_frame=regBandeira(parent=self,id=-1)
			ban_frame.Centre()
			ban_frame.Show()

	def receberPagamento(self,_bd,_au):

		if _bd !='':	self.bandeiras.SetValue(_bd)
		if _au !='':	self.comprovan.SetValue(_au)

	def TlNum(self,event):

		if self.CHQEstornado.GetItemCount() == 0:	alertas.dia(self.painel,u"Lista de Cartões Vazio !!\n"+(" "*90),"Contas Areceber: Conferência")
		else:
			TelNumeric.decimais = 5
			tel_frame=TelNumeric(parent=self,id=event.GetId())
			tel_frame.Centre()
			tel_frame.Show()

	def Tvalores(self,valor,idfy):	self.comprovan.SetValue(valor)

	def gravarAlteracao(self,event):

		indice = self.CHQEstornado.GetFocusedItem()
		numdav = self.CHQEstornado.GetItem(indice,1).GetText()
		bandei = self.CHQEstornado.GetItem(indice,5).GetText()
		
		if self.CHQEstornado.GetItemCount() == 0:	alertas.dia(self.painel,u"Lista de Cartões Vazio !!\n"+(" "*90),"Contas Areceber: Conferência")
		else:

			if self.bandeiras.GetValue() == '' and bandei == '':	alertas.dia(self.painel,u"Bandeira estar Vazio !!\n"+(" "*90),"Contas Areceber: Conferência")
			else:
				_dav = numdav.split('/')[0]
				_par = numdav.split('/')[1]
				ET   = datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin

				_auT = self.comprovan.GetValue()
				_ban = self.bandeiras.GetValue()
				_grv = 0
				_sva = True

				if _ban == '':	_ban = bandei
				
				confirma = wx.MessageDialog(self.painel,"Nº DAV: "+str( _dav )+"  Parcela Nº: "+str( _par )+"\n\nNº Autorização: "+str( _auT )+"\nBandeira: "+str( _ban )+"\n\n\nConfirme para Alterar !!\n"+(" "*100),"Contas Areceber: Conferência de Cartões",wx.YES_NO|wx.NO_DEFAULT)
				if confirma.ShowModal() ==  wx.ID_YES:
				
					conn = sqldb()
					sql  = conn.dbc("Caixa: Recebimento { Coleta do Créditos e Débitos }", fil = self.Filial, janela = self.painel )
							
					if sql[0] == True:

						achar = "SELECT rc_bandei,rc_autori,rc_histor FROM receber WHERE rc_ndocum='"+str( _dav )+"' and rc_nparce='"+str( _par )+"'"
						histo = ""
						if sql[2].execute(achar) !=0:
							
							_hist = sql[2].fetchall()
							_bd = _au = _hi = ""
							if _hist[0][0] !=None:	_bd = _hist[0][0]
							if _hist[0][1] !=None:	_au = _hist[0][1]
							if _hist[0][2] !=None:	_hi = _hist[0][2]

							histo = "Conferência do Cartão de Crédito: {"+str( ET )+"}\n\nNº Autorização: "+str( _au )+" Nova Autorização: "+str( _auT )+"\nBandeira: "+str( _bd )+" Nova Bandeira: "+str( _ban )+"\n\n"+_hi
							
						try:
							
							_sal = "UPDATE receber SET rc_bandei=%s,rc_autori=%s,rc_histor=%s WHERE rc_ndocum=%s and rc_nparce=%s"
							_grv = sql[2].execute( _sal, ( _ban, _auT, histo, _dav, _par ))
							
							sql[1].commit()

						except Exception, _reTornos:
							_sva = False
							sql[1].rollback()
						
						conn.cls(sql[1])

						if _sva == False:	alertas.dia(self.painel,u"Processo Interrompido...\n\nRetorno: "+str( _reTornos )+"\n"+(" "*120),"Contas Areceber: Conferência de Cartões")
						else:
							self.selecionar(wx.EVT_BUTTON)
							self.CHQEstornado.Select(indice)
							self.CHQEstornado.Focus(indice)
							
							self.comprovan.SetValue('')
							self.bandeiras.SetValue('')
			
	def selecionar(self,event):

		if not self.rlfilia.GetValue():	self.rFilial.SetValue( False )
		if not self.relator.GetValue():
			
			alertas.dia( self, "Selecione um relatório...\n"+(" "*100),"Relatórios")
			return

		if RelatorioDiversos._id != "08":

			dI = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			dF = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			
			conn = sqldb()
			sql  = conn.dbc("Contas Areceber: Selecionando Títulos", fil = self.Filial, janela = self.painel )
			
			if sql[0] == True:	
				
				""" Consulta Contas a Receber """
				if self.pesquisa_periodo.GetValue() == True:	_receber = "SELECT * FROM receber WHERE rc_dtlanc>='"+str( dI )+"' and rc_dtlanc<='"+str( dF )+"' ORDER BY rc_vencim"
				else:	_receber = "SELECT * FROM receber WHERE rc_regist!=0 ORDER BY rc_vencim"
				
				if self.rFilial.GetValue() == True:	_receber = _receber.replace("WHERE","WHERE rc_indefi='"+str( self.Filial )+"' and")
				
				if self._id =="01":	_receber = _receber.replace('ORDER BY rc_vencim',"and rc_status='' and rc_estorn='1' and ( rc_formap like '02-%' or rc_formap like '03-%' ) ORDER BY rc_dtlanc")
				if self._id == "02":

					_receber = _receber.replace('ORDER BY rc_vencim',"and rc_status='' ORDER BY rc_vencim")
					_receber = _receber.replace('rc_dtlanc','rc_vencim')
					
					if self.docume and self.fclient.GetValue():	_receber = _receber.replace('ORDER BY rc_vencim',"and rc_cpfcnp='"+str( self.docume )+"' ORDER BY rc_vencim")

					#// Totalizar o relatorio de contas areceber por cliente
					if self.totaliza_cliente.GetValue():	_receber = _receber.replace('ORDER BY rc_vencim',"ORDER BY rc_clnome,rc_vencim")

				if self._id == "03":

					_receber = _receber.replace('ORDER BY rc_vencim',"and ( rc_status='1' or rc_status='2' ) ORDER BY rc_dtbaix")
					if self.docume and self.fclient.GetValue():	_receber = _receber.replace('ORDER BY rc_dtbaix',"and rc_cpfcnp='"+str( self.docume )+"' ORDER BY rc_dtbaix")
					_receber = _receber.replace('rc_dtlanc','rc_dtbaix')

				if self._id == "04":	_receber = _receber.replace('ORDER BY rc_vencim',"and ( rc_status='' or rc_status='3') and ( rc_formap like '04-%' or rc_formap like '05-%' ) ORDER BY rc_dtlanc")

				if self._id == "05":

					_receber = _receber.replace('ORDER BY rc_vencim',"and ( rc_status='' or rc_status='3') and rc_nosson!='' ORDER BY rc_dtlanc")
					_receber = _receber.replace('rc_dtlanc','rc_dtbole')

				if self._id == "06" and  self.p.bdnBo.GetValue().strip() !='':
					
					_receber = "SELECT * FROM receber WHERE rc_border='"+str( self.p.bdnBo.GetValue() ).strip()+"' ORDER BY rc_vencim"
					if self.rFilial.GetValue() == True:	_receber = _receber.replace("WHERE","WHERE rc_indefi='"+str( self.Filial )+"' and")
					
					vT = "SELECT SUM(rc_apagar) FROM receber WHERE rc_border='"+str( self.p.bdnBo.GetValue() ).strip()+"'"
					TT = sql[2].execute( vT )
					vL = sql[2].fetchall()

					self.vlb = format( vL[0][0], ',' )

				if self._id == "07":
					
					_receber = "SELECT * FROM receber WHERE rc_dtbaix>='"+str( dI )+"' and rc_dtbaix<='"+str( dF )+"' and rc_baixat='1' ORDER BY rc_dtbaix,rc_formap"
					if self.rFilial.GetValue() == True:	_receber = _receber.replace("WHERE","WHERE rc_indefi='"+str( self.Filial )+"' and")
					if self.docume and self.fclient.GetValue():	_receber = _receber.replace("WHERE","WHERE rc_cpfcnp='"+str( self.docume )+"' and")


				if self.formapg.GetValue() !='':	_receber = _receber.replace('ORDER BY',"and rc_formap like '"+str( self.formapg.GetValue()[:3] )+"%' ORDER BY")
				if self.relvende.GetValue() and self.vendedo.GetValue():	_receber = _receber.replace('ORDER BY',"and rc_vended='"+str( self.vendedo.GetValue().split('-')[1] )+"' ORDER BY")
				if self.relcaixa.GetValue() and self.vendedo.GetValue():	_receber = _receber.replace('ORDER BY',"and rc_bxlogi='"+str( self.vendedo.GetValue().split('-')[1] )+"' ORDER BY")

				_car = sql[2].execute( _receber )
				_rca = sql[2].fetchall()

				if self._id == "06" and  self.p.bdnBo.GetValue().strip() == '':
					
					self.historico.SetValue("\n\n\n\n"+(" "*23)+"Nº DE B O R D E R Ô   V A Z I O")
					_car = 0

				_ToTalCRT  = self.vlTLiq = Decimal('0.00')
				_registros = 0
				relacao = {}
				ordem = 1
				lista_baixas = []
				if _car !=0:
					
					primeiro_cliente = _rca[0][12]
					valor_total_cliente = Decimal('0.00')
					indice = 0
					qlanca = 0
					lista_filtra_carteira = []
					for i in _rca:

						""" Retorna com o percentual da comissao do cartao """
						comissa = vReceber = vRecebid = "0.00"
						if i[27] !='':	comissa = nF.rTComisBand( i[27] )
						if Decimal( comissa ) > 0 and i[5]  > 0:	vReceber = format( ( i[5]  * Decimal( comissa ) / 100 ), ',' )
						if Decimal( comissa ) > 0 and i[18] > 0:	vRecebid = format( ( i[18] * Decimal( comissa ) / 100 ), ',' )

						emissao = estorno = motivoe = vencime = pagamen = nossoNumero = emibole = ''

						if i[7] != None:	emissao = i[7].strftime("%d/%m/%Y")+" "+str(i[8])+" "+str(i[10])+" { "+str( i[56] )+" }"
						if i[63]!= None:	motivoe = i[63]
						if i[26]!= None:	vencime = i[26].strftime("%d/%m/%Y")
						if i[19]!= None:	pagamen = i[19].strftime("%d/%m/%Y")+" "+str(i[20])+" "+str(i[17])
						if i[63]!= None and len(i[63].split('|')) > 1:	estorno = i[63].split('|')[0]
						if i[63]!= None and len(i[63].split('|')) > 1:	motivoe = i[63].split('|')[1]
						if i[79]!= None and i[79] !='':	nossoNumero = i[79].zfill(8)
						if i[82] != None:	emibole = i[82].strftime("%d/%m/%Y")

						"""  Calcula valor liquido para cartao  """
						cartao_liquido = i[5]
						comissao_cartao = Decimal('0.00')
						if self._id == "03":	cartao_liquido = i[18]

						if i[27] and i[27].split("-")[0]:	cartao_liquido, comissao_cartao = nF.retornaLiquidoCartao( i[27], cartao_liquido )
						else:	comissao_cartao = Decimal('0.00')
						""" //-------------------------------------------------// """
						
						if self._id == "05" and i[82] != None:	emissao = i[82].strftime("%d/%m/%Y")+" "+str(i[83])+" "+str(i[10])

						if self._id == "03":
						    
							if self.carteira.GetValue(): #//-> Emissao com filtro por carteira
						
							    if i[6].split('-')[0]=='07' and not i[52]:
								
								__relaTorio = str(i[1])+';'+str(i[3])+';'+str(i[5])+';'+str(i[6])+';'+str(i[7])+';'+str(i[8])+';'+str(i[10])+';'+str(i[12].replace(';',' '))+';'+str(i[17])+';'+\
								str(cartao_liquido)+';'+str(i[19])+';'+str(i[20])+';'+str(i[21])+';'+str(i[24])+';'+str(i[26])+';'+str(i[27])+';'+str(i[33])+';'+str(i[58])+';'+str(i[63])+';'+str(i[59])+";"+str(comissao_cartao)

							else:
							    __relaTorio = str(i[1])+';'+str(i[3])+';'+str(i[5])+';'+str(i[6])+';'+str(i[7])+';'+str(i[8])+';'+str(i[10])+';'+str(i[12].replace(';',' '))+';'+str(i[17])+';'+\
							    str(cartao_liquido)+';'+str(i[19])+';'+str(i[20])+';'+str(i[21])+';'+str(i[24])+';'+str(i[26])+';'+str(i[27])+';'+str(i[33])+';'+str(i[58])+';'+str(i[63])+';'+str(i[59])+";"+str(comissao_cartao)
							
						elif self._id == "05":

							__relaTorio = str(i[1])+';'+str(i[3])+';'+str(i[5])+';'+str(i[81])+';'+str(i[7])+';'+str(i[8])+';'+str(i[10])+';'+str(i[12].replace(';',' '))+';'+str(i[17])+';'+\
							str(i[18])+';'+str(i[19])+';'+str(i[20])+';'+str(i[21])+';'+str(i[24])+';'+str(i[26])+';'+str(i[79])+';'+str(i[33])+';'+str(i[58])+';'+str(i[63])+';'+str(i[59])+";"+emibole

						elif self._id == "06":	pass
						else:

							__vlr = i[5]
							if self._id == "02":	__vlr = cartao_liquido

							valor = Decimal('0.00')
							lancamentos = 0

							totalizar = False
							qlanca +=1
							valor_total_cliente += __vlr

							if self.totaliza_cliente.GetValue() and indice == ( len( _rca ) - 1 ):	totalizar = True
							if indice < ( len( _rca ) - 1 ) and _rca[indice+1][12] !=i[12]:	totalizar = True

							indice +=1
														
							if totalizar:	

								valor = valor_total_cliente
								lancamentos = qlanca
								
								qlanca = 0
								valor_total_cliente = Decimal('0.00')
							
							primeiro_cliente = i[12]	
								
							__relaTorio = str(i[1])+';'+str(i[3])+';'+str( __vlr )+';'+str(i[6])+';'+str(i[7])+';'+str(i[8])+';'+str(i[10])+';'+str(i[12].replace(';',' ') )+';'+str(i[17])+';'+\
							str(i[18])+';'+str(i[19])+';'+str(i[20])+';'+str(i[21])+';'+str(i[24])+';'+str(i[26])+';'+str(i[27])+';'+str(i[33])+';'+str(i[58])+';'+str(i[63])+';'+str(i[59])+';'+str( valor )+';'+str( lancamentos )+";"+str( comissao_cartao )

						if self._id == "01":	relacao[_registros] = str( i[24] ),str( i[1]+'/'+i[3]),emissao,estorno,str(i[12]),format(i[5],','),motivoe,str(i[35]),str(i[54]),str(i[6]),'','','',__relaTorio
						if self._id == "02":	relacao[_registros] = str( i[24] ),str( i[1]+'/'+i[3]),emissao,vencime,str(i[6]),format(cartao_liquido,','),str(i[59]),str(i[12]),str(i[35]),str(i[54]),'','','',__relaTorio
						if self._id == "03":
						    
						    if self.carteira.GetValue(): #//-> Emissao com filtro por carteira
							if i[64] and '07-Carteira' in i[64]:

							    if i[6].split('-')[0]=='07' and i[53]=='1':

								relacao[_registros] = str( i[24] ),str( i[1]+'/'+i[3]),emissao,vencime,pagamen,format( cartao_liquido,','),str(i[59]),str(i[12]),str(i[35]),str(i[54]),str(i[6]),'Liquidacao',str(i[38]),''

							    else:
								
								if i[64]:

								    if i[1] not in lista_baixas:
									
									lista_baixas.append(i[1])
									numero_lancamento = i[64][:-1]
									    
									self.valor_total_lancamentos = Decimal()
									relacao_pagamentos = '|'.join( self.relacionarPagamentos(i[1],sql) )
									__relaTorio = numero_lancamento +'<>'+ relacao_pagamentos
									    
									fbaixado = i[21] if len(relacao_pagamentos.split('|')) == 1 else 'Diversos'	
									relacao[_registros] = str( i[24] ),str( i[1]+'/'+i[3]),emissao,vencime,pagamen,format( self.valor_total_lancamentos,','),str(i[59]),str(i[12]),str(i[35]),str(i[54]),str(i[6]),fbaixado,str(i[38]),__relaTorio
									_registros +=1

						    else:
							relacao[_registros] = str( i[24] ),str( i[1]+'/'+i[3]),emissao,vencime,pagamen,format( cartao_liquido,','),str(i[59]),str(i[12]),str(i[35]),str(i[54]),str(i[6]),str(i[21]),str(i[38]),__relaTorio
						    
						if self._id == "04":	relacao[_registros] = str( i[24] ),str( i[1]+'/'+i[3]),emissao,vencime,i[6],i[27],i[58],i[59],format(i[5],','),i[12],'','','',__relaTorio
						if self._id == "05":	relacao[_registros] = str( i[24] ),str( i[1]+'/'+i[3]),emissao,vencime,i[81],nossoNumero,i[58],i[59],format(i[5],','),i[12],'','','',__relaTorio

						if self._id == "06":

							self.som = 0 #-------------------------: Soma das DaTas
							self.TCb = _car #----------------------: QT TiTulos Cheque
							self.mvb = format( i[70],"%d/%m/%Y") #-: DaTa do Movimento
							self.fvb = str( i[74] ) #--------------: Favorecido
			
							if i[26] != None:

								_ven = format( i[26],"%d/%m/%Y" )
								self.som += int( _ven.replace('/','') )

							relacao[_registros] = str(i[24]),str( ordem ).zfill(3),str( nF.conversao( i[28], 4 ) ),str(i[57]),str(i[30]),str(i[31]),str(i[32]),str(i[33]),str(i[67]),format(i[05],','),str(i[29]),str(i[74]),nF.conversao( str( i[26] ), 3 ),str( i[1]+'-'+i[3] )

						if self._id == "07":

							dBaixa = format( i[19],"%d/%m/%Y") #-: DaTa da Baixa
							dVenci = format( i[26],"%d/%m/%Y") #-: DaTa do Movimento

							relacao[_registros] = str(i[24]),str(i[1]+"-"+i[3]),dVenci,dBaixa+" "+str( i[20] )+' '+str( i[17] ),format( i[18],',' ),str( i[12].replace(';',' ') ),str( i[21] ),str(i[53]),str(i[54]),str(i[37])
							self.vlTLiq += i[18]

						_registros +=1
						ordem +=1

					if self._id == "06":
						
						hs = "Nº Lote/Borderô...: "+str( self.p.bdnBo.GetValue() ).strip()+\
							 "\nSomatorio.........: "+str( self.som )+\
							 "\nNº Cheques/Boletos: "+str( self.TCb )+\
							 "\nData do Movimento.: "+str( self.mvb )+\
							 "\nValor Total.......: "+str( self.vlb )+\
							 "\nFavorecido........: "+str( self.fvb )

						self.historico.SetValue( hs )

					if self._id == "07":

						hs = "{ Liquidação }"+\
							 "\nValor Total: "+format( self.vlTLiq, ',' )

						self.historico.SetValue( hs )
				conn.cls(sql[1])

				if self.carteira.GetValue() and self._id == "03":	_car = len(relacao)
				self.CHQEstornado.SetItemCount(_car)
				CHQListCtrl.itemDataMap  = relacao
				CHQListCtrl.itemIndexMap = relacao.keys()
				self._oc.SetLabel(u"Ocorrências {"+str( _car )+"}")
				self.ToTaliza(wx.EVT_BUTTON)
	
	def relacionarPagamentos(self, numero, sql ):
	    relacao =[]
	    self.valor_total_lancamentos = Decimal()
	    if sql[2].execute("SELECT rc_vlbaix,rc_nparce,rc_formar FROM receber WHERE rc_ndocum='"+ numero +"'"):
		
		for i in sql[2].fetchall():
		    relacao.append(format(i[0],',')+';'+i[2])
		    self.valor_total_lancamentos +=i[0]
		    
	    return relacao

	def emissaoVencimento(self,numero,sql):

	    n, p = numero.split('/')
	    em = vc = ""
	    if sql[2].execute("SELECT rc_dtlanc,rc_hslanc,rc_loginc,rc_vencim FROM receber WHERE rc_ndocum='"+ n +"' and rc_nparce='"+ p +"'"):
		rs = sql[2].fetchone()
		em = format(rs[0],"%d/%m/%Y")+' '+str(rs[1])+' '+rs[2]
		vc = format(rs[3],"%d/%m/%Y")
	    return em,vc

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 101:	sb.mstatus(u"  Emissão do Relatório",0)
		elif event.GetId() == 104:	sb.mstatus(u"  Aumentar Janela de Visualização",0)
		elif event.GetId() == 103:	sb.mstatus(u"  Totalizar Valores da Lista",0)
		elif event.GetId() == 202:	sb.mstatus(u"  Salvar-Gravar Nº Autorização e Bandeira do Cartão",0)
		event.Skip()

	def OnLeaveWindow(self,event):

		sb.mstatus("  Contas a Receber: Emissão de Relação e Relatorios",0)
		event.Skip()
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
		
		dc.SetTextForeground("#2323A5")
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.DrawRotatedText("Contas Areceber: Relatorios { D i v e r s o s }", 0, 525, 90)

		dc.SetTextForeground("#7F7F7F")
		dc.SetFont(wx.Font(7.5, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.DrawRotatedText("Contas\nReceber", 867, 345, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		dc.DrawRoundedRectangle( 12, 271, 933, 222, 3)


class CHQListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):

		_ID = RelatorioDiversos._id
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		
		self.il = wx.ImageList(16, 16)
		for k,v in diretorios.pasta_icons.items():
			s="self.%s= self.il.Add(wx.Bitmap(%s))" % (k,v)
			exec(s)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr2 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour('#7C8B9B')
		self.attr2.SetBackgroundColour('#ACC6D0')

		if _ID == "01": #-: Relacao de Cheques Estornados

			self.InsertColumn(0, 'Filial', width=80)
			self.InsertColumn(1, 'Nº Dav-Controle', format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(2, 'Emissão', width=95)
			self.InsertColumn(3, 'Estorno', width=95)
			self.InsertColumn(4, 'Descrição do Cliente', width=400)
			self.InsertColumn(5, 'Valor', format=wx.LIST_ALIGN_LEFT,  width=95)
			self.InsertColumn(6, 'Motivo do Estorno',    width=400)
			self.InsertColumn(7, 'Status',  width=50)
			self.InsertColumn(8, 'Estorno', width=60)
			self.InsertColumn(9, 'Forma de Pagamento', width=200)
			self.InsertColumn(10,'', width=1)
			self.InsertColumn(11,'', width=1)
			self.InsertColumn(12,'', width=1)
			self.InsertColumn(13,'Dados do Relatorio', width=200)

		elif _ID == "02": #-: Contas AReceber

			self.InsertColumn(0, 'Filial', width=80)
			self.InsertColumn(1, 'Nº Dav-Controle', format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(2, 'Emissão', width=95)
			self.InsertColumn(3, 'Vencimento', width=95)
			self.InsertColumn(4, 'Forma de Pagamento', width=150)
			self.InsertColumn(5, 'Valor', format=wx.LIST_ALIGN_LEFT, width=95)
			self.InsertColumn(6, 'NotaFiscal', format=wx.LIST_ALIGN_LEFT,width=70)
			self.InsertColumn(7, 'Descrição do Cliente', width=400)
			self.InsertColumn(8, 'Status',  width=50)
			self.InsertColumn(9, 'Estorno', width=60)
			self.InsertColumn(10,'', width=1)
			self.InsertColumn(11,'', width=1)
			self.InsertColumn(12,'', width=1)
			self.InsertColumn(13,'Dados do Relatorio', width=200)

		elif _ID == "03": #-: Contas Recebidas

			self.InsertColumn(0, 'Filial', width=80)
			self.InsertColumn(1, 'Nº Dav-Controle', format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(2, 'Emissão', width=95)
			self.InsertColumn(3, 'Vencimento', width=95)
			self.InsertColumn(4, 'Pagamento',  width=95)
			self.InsertColumn(5, 'Valor Baixado', format=wx.LIST_ALIGN_LEFT, width=95)
			self.InsertColumn(6, 'NotaFiscal', format=wx.LIST_ALIGN_LEFT,width=70)
			self.InsertColumn(7, 'Descrição do Cliente', width=400)
			self.InsertColumn(8, 'Status',  width=50)
			self.InsertColumn(9, 'Estorno', width=60)
			self.InsertColumn(10,'Forma de Pagamento', width=200)
			self.InsertColumn(11,'Forma da Baixa',     width=200)
			self.InsertColumn(12,'Bandeira da Baixa',  width=200)
			self.InsertColumn(13,'Dados do Relatorio', width=200)

		elif _ID == "04": #-: Conferencia de Cartoes

			self.InsertColumn(0, 'Filial', width=80)
			self.InsertColumn(1, 'Nº Dav-Controle', format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(2, 'Emissão', width=95)
			self.InsertColumn(3, 'Vencimento', width=85)
			self.InsertColumn(4, 'Forma de Pagamento', width=147)
			self.InsertColumn(5, 'Bandeira', width=125)
			self.InsertColumn(6, 'Autorização', format=wx.LIST_ALIGN_LEFT,width=90)
			self.InsertColumn(7, 'NotaFiscal', format=wx.LIST_ALIGN_LEFT,width=70)
			self.InsertColumn(8, 'Valor',format=wx.LIST_ALIGN_LEFT, width=90)
			self.InsertColumn(9, 'Descrição do Cliente', width=400)
			self.InsertColumn(10,'', width=1)
			self.InsertColumn(11,'', width=1)
			self.InsertColumn(12,'', width=1)
			self.InsertColumn(13,'Dados do Relatorio', width=200)

		elif _ID == "05": #-: Conferencia de Cartoes

			self.InsertColumn(0, 'Filial', width=80)
			self.InsertColumn(1, 'Nº Dav-Controle', format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(2, 'Emissão', width=95)
			self.InsertColumn(3, 'Vencimento', width=85)
			self.InsertColumn(4, 'BCO-AG-CC-Carteira', width=150)
			self.InsertColumn(5, 'Nosso Numero', width=125)
			self.InsertColumn(6, 'COO/NFCe',width=95)
			self.InsertColumn(7, 'NotaFiscal', format=wx.LIST_ALIGN_LEFT,width=70)
			self.InsertColumn(8, 'Valor',format=wx.LIST_ALIGN_LEFT, width=90)
			self.InsertColumn(9, 'Descrição do Cliente', width=400)
			self.InsertColumn(10,'', width=1)
			self.InsertColumn(11,'', width=1)
			self.InsertColumn(12,'', width=1)
			self.InsertColumn(13,'Dados do Relatorio', width=200)

		elif _ID == "06": #-: Borderô

			self.InsertColumn(0, 'Filial', width=80)
			self.InsertColumn(1, 'SEQ', format=wx.LIST_ALIGN_LEFT, width=40)
			self.InsertColumn(2, 'CPF-CNPJ', format=wx.LIST_ALIGN_LEFT, width=150)
			self.InsertColumn(3, 'Comp', width=40)
			self.InsertColumn(4, 'Banco', width=60)
			self.InsertColumn(5, 'Agência', width=60)
			self.InsertColumn(6, 'Nº Conta',width=90)
			self.InsertColumn(7, 'Nº Cheque', format=wx.LIST_ALIGN_LEFT,width=75)
			self.InsertColumn(8, 'Nº Boleto',format=wx.LIST_ALIGN_LEFT, width=90)
			self.InsertColumn(9, 'Valor',    format=wx.LIST_ALIGN_LEFT, width=90)
			self.InsertColumn(10,'Descrição Correntista-Cliente',  width=400)
			self.InsertColumn(11,'Favorecido - Banco/Fornecedor', width=400)
			self.InsertColumn(12,'Vencimento', width=110)
			self.InsertColumn(13,'Nº DAV', width=160)

		elif _ID == "07": #-: Titulos Liuquidados

			self.InsertColumn(0, 'Filial', width=90)
			self.InsertColumn(1, 'Nº Título-DAV', format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(2, 'Vencimento',    format=wx.LIST_ALIGN_LEFT, width=90)
			self.InsertColumn(3, 'Baixa', width=200)
			self.InsertColumn(4, 'Valor', format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(5, 'Descrição do Cliente', width=590)
			self.InsertColumn(6, 'Forma de Pagamento', width=200)
			self.InsertColumn(7, '1-Liquidação', width=100)
			self.InsertColumn(8, '1-Estornado',  width=100)
			self.InsertColumn(9, '1-Receber 2-Caixa',  width=130)

	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception, _reTornos:	pass
						
	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		_ID = RelatorioDiversos._id
		if self.itemIndexMap != []:
			
			index = self.itemIndexMap[item]
			if item % 2:
				if _ID == "04":	return self.attr2
				else:	return self.attr1
			
	def GetListCtrl(self):	return self			

	def OnGetItemImage(self, item):

		_ID = RelatorioDiversos._id
		if self.itemIndexMap != []:

			index=self.itemIndexMap[item]
			if _ID == "5033":
			
				_sta = self.itemDataMap[index][7]
				if _sta == '2':	return self.e_tra

			return self.w_idx


class EsTornarReceber(wx.Frame):

	Filial = ""
	
	def __init__(self, parent,id):

		self.p = parent
		self.p.Disable()
		
		""" Totalizacao da Conta Corrente Total e Individual """
		self.TcC = self.TcD = Decimal("0.00")
		self.IcC = self.IcD = Decimal("0.00")
		self.hsI = ""
		self.apa = False
		self.ect = False,"",""

		wx.Frame.__init__(self, parent, id, 'Contas Areceber: Estorno de títulos', size=(600,475), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,style = wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)

#------: Relacionar parcelas do titulo selecioando
		self.RelaTiTulos = wx.ListCtrl(self.painel, 420,pos=(0,55), size=(595,130),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.RelaTiTulos.SetBackgroundColour('#B1A0A0')
		self.RelaTiTulos.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Bind(wx.EVT_KEY_UP,self.Teclas)

		self.RelaTiTulos.InsertColumn(0, 'Ordem',      format=wx.LIST_ALIGN_LEFT, width=45)
		self.RelaTiTulos.InsertColumn(1, 'Nº Título',  format=wx.LIST_ALIGN_LEFT, width=110)
		self.RelaTiTulos.InsertColumn(2, 'Parcela',    format=wx.LIST_ALIGN_LEFT, width=50)
		self.RelaTiTulos.InsertColumn(3, 'Lançamento', format=wx.LIST_ALIGN_LEFT, width=130)
		self.RelaTiTulos.InsertColumn(4, 'Vencimento', format=wx.LIST_ALIGN_LEFT, width=110)
		self.RelaTiTulos.InsertColumn(5, 'Valor',      format=wx.LIST_ALIGN_LEFT, width=70)
		self.RelaTiTulos.InsertColumn(6, 'Status',     format=wx.LIST_ALIGN_TOP, width=70)
		self.RelaTiTulos.InsertColumn(7, 'Origem',     format=wx.LIST_ALIGN_TOP, width=70)
		self.RelaTiTulos.InsertColumn(8, 'Estornado',  format=wx.LIST_ALIGN_TOP, width=70)
		self.RelaTiTulos.InsertColumn(9, 'ID-Lançamento',  format=wx.LIST_ALIGN_LEFT, width=110)
		self.RelaTiTulos.InsertColumn(10,'Vinculado',  format=wx.LIST_ALIGN_LEFT, width=110)
		self.RelaTiTulos.InsertColumn(11,'Forma de Pagamento' , width=200)
		self.RelaTiTulos.InsertColumn(12,'Baixa' ,        width=200)
		self.RelaTiTulos.InsertColumn(13,'Cancelamento' , width=200)

		self.RelaTiTulos.InsertColumn(14,'CC Crédito' , format=wx.LIST_ALIGN_LEFT, width=100)
		self.RelaTiTulos.InsertColumn(15,'CC Débito' ,  format=wx.LIST_ALIGN_LEFT, width=100)
		self.RelaTiTulos.InsertColumn(16,'Historico' ,  width=300)

#-------: Relacionar TiTulos Vinculados
		self.VincTiTulos = wx.ListCtrl(self.painel, 420,pos=(0,205), size=(595,122),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.VincTiTulos.SetBackgroundColour('#B1CFEC')
		self.VincTiTulos.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.VincTiTulos.InsertColumn(0, 'Ordem',      format=wx.LIST_ALIGN_LEFT, width=45)
		self.VincTiTulos.InsertColumn(1, 'Nº Título',  format=wx.LIST_ALIGN_LEFT, width=110)
		self.VincTiTulos.InsertColumn(2, 'Parcela',    format=wx.LIST_ALIGN_LEFT, width=50)
		self.VincTiTulos.InsertColumn(3, 'Lançamento', format=wx.LIST_ALIGN_LEFT, width=130)
		self.VincTiTulos.InsertColumn(4, 'Vencimento', format=wx.LIST_ALIGN_LEFT, width=110)
		self.VincTiTulos.InsertColumn(5, 'Valor',      format=wx.LIST_ALIGN_LEFT, width=70)
		self.VincTiTulos.InsertColumn(6, 'Status',     format=wx.LIST_ALIGN_TOP, width=70)
		self.VincTiTulos.InsertColumn(7, 'Origem',     format=wx.LIST_ALIGN_TOP, width=70)
		self.VincTiTulos.InsertColumn(8, 'Estornado',  format=wx.LIST_ALIGN_TOP, width=70)
		self.VincTiTulos.InsertColumn(9, 'ID-Lançamento',  format=wx.LIST_ALIGN_LEFT, width=110)
		self.VincTiTulos.InsertColumn(10,'Vinculado',  format=wx.LIST_ALIGN_LEFT, width=110)
		self.VincTiTulos.InsertColumn(11,'Forma de Pagamento' , width=200)
		self.VincTiTulos.InsertColumn(12,'Baixa' ,        width=200)
		self.VincTiTulos.InsertColumn(13,'Cancelamento' , width=200)
		self.VincTiTulos.InsertColumn(14,'CC Crédito' , format=wx.LIST_ALIGN_LEFT, width=100)
		self.VincTiTulos.InsertColumn(15,'CC Débito' ,  format=wx.LIST_ALIGN_LEFT, width=100)
		self.VincTiTulos.InsertColumn(16,'Historico' ,  width=300)

		Leg = wx.StaticText(self.painel,-1,"1-Baixado\n2-Liquidação\n3-Estornado\n4-Cancelado p/Desmenbramento\n5-Cancelado", pos=(400, 335))
		Leg.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		Leg.SetForegroundColour("#7F7F7F")

		self.TiR = wx.StaticText(self.painel,-1,"Títulos p/Cancelamento { Principal }", pos=(3, 40))
		self.TiR.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TiR.SetForegroundColour("#A52A2A")

		self.TiE = wx.StaticText(self.painel,-1,"Títulos p/Recuperar { Vinculados }", pos=(3, 190))
		self.TiE.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TiE.SetForegroundColour("#1273D2")

		wx.StaticText(self.painel,-1,"NºLançamento/Título", pos=(3, 0)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"NºParcela",           pos=(120, 0)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nome do Cliente",     pos=(190, 0)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Selecionar Título Baixado,Liquidado p/Estornar",     pos=(3,330)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Conta Corrente Crédito { Transferência }", pos=(3,365)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Conta Corrente Débito  { PgTo-Crédito  }", pos=(3,383)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.nRG = wx.StaticText(self.painel,-1,label="ID", pos=(290, 0))
		self.nRG.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.nRG.SetForegroundColour('#195792')

		self.nTL = wx.TextCtrl(self.painel,-1,value="", pos=(0,  13), size=(110,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.nPC = wx.TextCtrl(self.painel,-1,value="", pos=(122,13), size=(50, 20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.nCL = wx.TextCtrl(self.painel,-1,value="", pos=(187,13), size=(409,20),style=wx.TE_READONLY)

		self.vCc = wx.TextCtrl(self.painel,-1,value="0.00", pos=(180,359), size=(80,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.vCd = wx.TextCtrl(self.painel,-1,value="0.00", pos=(180,378), size=(80,20),style=wx.TE_READONLY|wx.TE_RIGHT)

		self.nTL.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nPC.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nCL.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vCc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vCd.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nTL.SetBackgroundColour('#E5E5E5')
		self.nPC.SetBackgroundColour('#E5E5E5')
		self.nCL.SetBackgroundColour('#E5E5E5')
		self.vCc.SetBackgroundColour('#BFBFBF')
		self.vCd.SetBackgroundColour('#BFBFBF')

		self.Tpr = wx.CheckBox(self.painel, -1, "Marcar o Título p/Estornar"+(" "*30), pos=(0,340))
		self.Tpr.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.mTv = wx.TextCtrl(self.painel,-1,value="", pos=(0,400), size=(597,68),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.mTv.SetBackgroundColour('#4D4D4D')
		self.mTv.SetForegroundColour('#90EE90')
		self.mTv.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL))

		self.nCa = wx.StaticText(self.painel,-1,label="", pos=(545,400))
		self.nCa.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nCa.SetForegroundColour('#EAEA98')

		self.indivi = GenBitmapTextButton(self.painel,-1,label=' Estornar\n Título', pos=(325,336), size=(70,24), bitmap=wx.Bitmap("imagens/estornop.png",  wx.BITMAP_TYPE_ANY))
		self.agrupa = GenBitmapTextButton(self.painel,-1,label=' Estornar\n Grupo ', pos=(325,372), size=(70,24), bitmap=wx.Bitmap("imagens/agrupar16.png", wx.BITMAP_TYPE_ANY))
		voltar = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/volta.png",  wx.BITMAP_TYPE_ANY), pos=(270,357), size=(50,40))				

		self.indivi.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL, False,"Arial"))
		self.agrupa.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL, False,"Arial"))
		self.indivi.SetBackgroundColour('#7F7F7F')
		self.agrupa.SetBackgroundColour('#7F7F7F')

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		self.Tpr.Bind( wx.EVT_CHECKBOX, self.chkBox )

		self.agrupa.Bind( wx.EVT_BUTTON, self.esTornarVinculados )
		self.indivi.Bind( wx.EVT_BUTTON, self.esTornarIndividual )

		self.lisTarTiTulos()
		self.indivi.Enable(False) 
		if self.VincTiTulos.GetItemCount() == 0:	self.agrupa.Enable(False) 
		if self.VincTiTulos.GetItemCount() != 0:	self.agrupa.SetBackgroundColour('#E5E5A6') 

	def sair(self,event):
		
		self.p.Enable()
		self.Destroy()

	def lisTarTiTulos(self):
	
		if self.p.ListaReceber.GetItemCount() !=0:
		
			indice = self.p.ListaReceber.GetFocusedItem()
			nLanca = self.p.ListaReceber.GetItem(indice, 0).GetText().split('/')
			nClien = self.p.ListaReceber.GetItem(indice, 4).GetText()
			nRegis = self.p.ListaReceber.GetItem(indice,49).GetText()
			
			self.nTL.SetValue(nLanca[0])
			self.nPC.SetValue(nLanca[1])
			self.nCL.SetValue(nClien)
			self.nRG.SetLabel( "{ ID-"+str( nRegis )+" }" )

			""" Limpar Lista """
			self.RelaTiTulos.DeleteAllItems()
			self.VincTiTulos.DeleteAllItems()
			self.RelaTiTulos.Refresh()
			self.VincTiTulos.Refresh()

			conn = sqldb()
			sql  = conn.dbc("Contas Areceber: Estorno", fil = self.Filial, janela = self.painel )

			if sql[0]:

				xxx = nLanca[0]
				sTiTulos = "SELECT * FROM receber WHERE rc_ndocum='"+ str( nLanca[0] ) +"' and rc_status!='4' and rc_status!='5' ORDER BY rc_ndocum,rc_nparce"
				bTiTulos = sql[2].execute( sTiTulos )
				rTiTulos = sql[2].fetchall()
				
				if bTiTulos !=0:
					
					ordem = 0
					orRec = 0
					
					rVi = rTiTulos[0][52]
					rTd = rTiTulos[0][7]

					""" Apura o numero de dias passados p/Permissão de Estorno """
					if rTd !=None	and rTd !='':

						dD = format( rTd, "%d/%m/%Y" )
						ld = datetime.datetime.strptime(dD, "%d/%m/%Y").date()
						hj = datetime.datetime.now().date()
						
						""" Apura o dias passado p/Bloquear estorno atraves da ressalva """
						rs = ( hj - ld ).days

						if login.filialLT[ self.Filial ][34] !="" and login.filialLT[ self.Filial ][34] !=None:	rd = int( login.filialLT[ self.Filial ][34] )
						else:	rd = 0

						if rd >0 and rs > rd:
							
							self.Tpr.Enable(False)
							self.indivi.Enable(False)
							self.agrupa.Enable(False)

							self.TiR.SetLabel(str( rs )+" { "+str( rd )+" DD }, Limite de tempo ultrapassado para estorno...")
							self.TiE.SetLabel(str( rs )+" { "+str( rd )+" DD }, Limite de tempo ultrapassado para estorno...")
							self.TiR.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
							self.TiE.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
							self.TiR.SetForegroundColour("#DA3939")
							self.TiE.SetForegroundColour("#DA3939")
							
					for i in rTiTulos:

						if i[2] and [2] == "A":	self.apa = True
						if i[55] and i[55] == "APAGAR":	self.apa = True
						__f = i[24] if i[24] else login.identifi
						
						if len( login.filialLT[__f][35].split(";") ) >= 80 and int(login.filialLT[__f][35].split(";")[79]):	self.ect = self.diasPassados( format( i[7], "%d/%m/%Y"), login.filialLT[__f][35].split(";")[79] )
						
						dL = dV = dB = dC = ""
						pC = Decimal("0.00") 
						if i[7] !=None	and i[7] !='':	dL = format( i[7], "%d/%m/%Y" )+" "+str( i[8] )
						if i[26] !=None	and i[26] !='':	dV = format( i[26],"%d/%m/%Y" )
						if i[19] !=None	and i[19] !='':	dB = format( i[19],"%d/%m/%Y" )+" "+str( i[20] )+" "+str( i[17])
						if i[44] !=None	and i[44] !='':	dC = format( i[44],"%d/%m/%Y" )+" "+str( i[45] )+" "+str( i[47])

						""" Pagamento com Credito """
						if i[6][:2] == "10":	pC = i[5]

						self.TcC += i[42]
						self.TcD += pC

						self.RelaTiTulos.InsertStringItem(ordem, str( ordem + 1 ).zfill(3) )
						self.RelaTiTulos.SetStringItem(ordem, 1, str( i[1] ) )
						self.RelaTiTulos.SetStringItem(ordem, 2, str( i[3] ) )
						self.RelaTiTulos.SetStringItem(ordem, 3, str( dL   ) )
						self.RelaTiTulos.SetStringItem(ordem, 4, str( dV   ) )
						self.RelaTiTulos.SetStringItem(ordem, 5, format( i[5],',' ) )
						self.RelaTiTulos.SetStringItem(ordem, 6, str( i[35] ) )
						self.RelaTiTulos.SetStringItem(ordem, 7, str( i[2]  ) )
						self.RelaTiTulos.SetStringItem(ordem, 8, str( i[54] ) )
						self.RelaTiTulos.SetStringItem(ordem, 9, str( i[0]  ) )
						self.RelaTiTulos.SetStringItem(ordem,10, str( i[51] ) )
						self.RelaTiTulos.SetStringItem(ordem,11, str( i[6]  ) )
						self.RelaTiTulos.SetStringItem(ordem,12, str( dB    ) )
						self.RelaTiTulos.SetStringItem(ordem,13, str( dC    ) )
						self.RelaTiTulos.SetStringItem(ordem,14, format( i[42],',' ) )
						self.RelaTiTulos.SetStringItem(ordem,15, format( pC, ','   ) )

						if i[63] !=None:	self.RelaTiTulos.SetStringItem(ordem,16, str( i[63] ) )
						else:	self.RelaTiTulos.SetStringItem(ordem,16, "" )

						if ordem % 2:	self.RelaTiTulos.SetItemBackgroundColour(ordem, "#BF9B9B")
						if str( i[35] ) == "2":

							self.RelaTiTulos.SetItemBackgroundColour(ordem, "#215C94")
							self.RelaTiTulos.SetItemTextColour(ordem, '#FFFFFF')

						if str( i[35] ) == "1":
							
							self.RelaTiTulos.SetItemBackgroundColour(ordem, "#C01616")
							self.RelaTiTulos.SetItemTextColour(ordem, '#FFFFFF')

						ordem +=1

					self.vCc.SetValue( format( self.TcC, ',' ) )
					self.vCd.SetValue( format( self.TcD, ',' ) )

					""" TiTulos vinculados """
					if rVi !="" and rVi !=None:
		
						Tv =  ( len( rVi.split('|') ) -2 )
						bT = 1

						for v in range( Tv ):

							if rVi.split('|') !='' and rVi.split('|')[bT] !='':
									
								nT = rVi.split('|')[bT].split('/')[0]
								pT = rVi.split('|')[bT].split('/')[1]

								slv = "SELECT * FROM receber WHERE rc_ndocum='"+str( nT )+"' and rc_nparce='"+str( pT )+"' ORDER BY rc_ndocum,rc_nparce"
								blv = sql[2].execute(slv)
								rlv = sql[2].fetchall()

								if blv !=0:

									for r in rlv:
											
										bL = bV = bB = bC = ""
										if i[7] !=None	and i[7] !='':	bL = format( i[7], "%d/%m/%Y" )+" "+str( i[8] )
										if i[26] !=None	and i[26] !='':	bV = format( i[26],"%d/%m/%Y" )
										if i[19] !=None	and i[19] !='':	bB = format( i[19],"%d/%m/%Y" )+" "+str( i[20] )+" "+str( i[17])
										if i[44] !=None	and i[44] !='':	bC = format( i[44],"%d/%m/%Y" )+" "+str( i[45] )+" "+str( i[47])

										self.VincTiTulos.InsertStringItem(orRec, str( orRec + 1 ).zfill(3) )
										self.VincTiTulos.SetStringItem(orRec, 1, str( r[1] ) )
										self.VincTiTulos.SetStringItem(orRec, 2, str( r[3] ) )
										self.VincTiTulos.SetStringItem(orRec, 3, str( bL   ) )
										self.VincTiTulos.SetStringItem(orRec, 4, str( bV   ) )
										self.VincTiTulos.SetStringItem(orRec, 5, format( r[5],',' ) )
										self.VincTiTulos.SetStringItem(orRec, 6, str( r[35] ) )
										self.VincTiTulos.SetStringItem(orRec, 7, str( r[2]  ) )
										self.VincTiTulos.SetStringItem(orRec, 8, str( r[54] ) )
										self.VincTiTulos.SetStringItem(orRec, 9, str( r[0]  ) )
										self.VincTiTulos.SetStringItem(orRec,10, str( r[51] ) )
										self.VincTiTulos.SetStringItem(orRec,11, str( r[6] ) )
										self.VincTiTulos.SetStringItem(orRec,12, str( bB   ) )
										self.VincTiTulos.SetStringItem(orRec,13, str( bC   ) )
										self.VincTiTulos.SetStringItem(ordem,14, format( i[42],',' ) )

										if i[63] !=None:	self.VincTiTulos.SetStringItem(ordem,16, str( i[63]) )
										else:	self.VincTiTulos.SetStringItem(ordem,16, "" )
										
										if orRec % 2:	self.VincTiTulos.SetItemBackgroundColour(orRec, "#C9DAEA")

										orRec +=1
							bT +=1

				conn.cls(sql[1])
				if self.apa or self.ect[0]:

					self.Tpr.Enable( False )
					self.TiR.SetLabel("Titulo vinculado, utilize o contas apagar p/estorno")
					if self.ect:	self.TiR.SetLabel("Data de lançamento acima da ressalva")

	def diasPassados(self, data, ressalva ):
		
		baixa = datetime.datetime.strptime( str( data ).split(' ')[0], '%d/%m/%Y').date()
		dhoje = datetime.datetime.now().date()
		ndias = ( dhoje - baixa ).days
		
		if ndias > int( ressalva ):	return True, str( ndias ), str( ressalva )
		else:	return False, str( ndias ), str( ressalva )

	def esTornarVinculados(self,event):

		if len( self.mTv.GetValue() ) < 15:
			
			alertas.dia(self.painel,"Motivo do estorno com menos de 15 letras...\n"+(" "*100),"Contas Areceber: Estorno de Títulos")
			return

		mensa = u"Estorno em Grupo do Título Nº "+ self.nTL.GetValue() +" ID-"+str( self.nRG.GetLabel() )+"\nNome do Cliente: "+ self.nCL.GetValue() +"\n\nConfirme p/Estornar !!\n"+(" "*130)
		esTor = wx.MessageDialog(self.painel,mensa,"Contas Areceber: Estorno em grupo",wx.YES_NO|wx.NO_DEFAULT)
		if esTor.ShowModal() ==  wx.ID_YES:
			
			DTA = datetime.datetime.now().strftime("%Y-%m-%d")
			HRS = datetime.datetime.now().strftime("%T")
			CDL = str( login.uscodigo )
			USL = str( login.usalogin )
			
			nRTiTu = self.RelaTiTulos.GetItemCount()
			nRVinc = self.VincTiTulos.GetItemCount()
			
			conn = sqldb()
			sql  = conn.dbc("Contas AReceber: Estorno de Títulos Desmenbrados", fil = self.Filial, janela = self.painel )
			grv  = True

			if sql[0] == True:

				_mensagem = mens.showmsg("Contas AReceber: Estorno de Titulos Desmenbrados...\n\nAguarde...")

				try:
					
					""" Titulos Vinculados """
					for i in range( nRVinc ):
						
						idL = str( self.VincTiTulos.GetItem(i, 9).GetText() )

						his = ""
						if self.VincTiTulos.GetItem(i, 16).GetText() !="":	his = "\n\n"+ self.VincTiTulos.GetItem(i, 16).GetText()
						hisTo = "Contas Areceber: Estorno em Grupo de Titulos { "+str( USL )+"  "+str( DTA )+" "+str( HRS )+" }\n[ Motivo ]\n"+str( self.mTv.GetValue() )+his

						estor = "UPDATE receber SET rc_status='',rc_canest='Aberto por estorno',rc_recebi='',\
						rc_dtcanc='00-00-0000',rc_hrcanc='00:00:00',rc_cancod='',\
						rc_canlog='',rc_desvin='',rc_baixat='',rc_estorn='1',\
						rc_obsest='"+ hisTo +"' WHERE rc_regist='"+ idL +"'"

						sql[2].execute(estor)
					
					""" Titulos Principais """
					for r in range( nRTiTu ):
						
						idT = str( self.RelaTiTulos.GetItem(r, 9).GetText() )
						his = ""
						if self.VincTiTulos.GetItem(i, 16).GetText() !="":	his = "\n\n"+ self.VincTiTulos.GetItem(i, 16).GetText()
						hisTo = "Contas Areceber: Estorno em Grupo de Titulos { "+str( USL )+"  "+str( DTA )+" "+str( HRS )+" }\n[ Motivo ]\n"+str( self.mTv.GetValue() )+his

						cance = "UPDATE receber SET rc_status='5',rc_canest='Cancelado por estorno',\
						rc_dtcanc='"+DTA+"',rc_hrcanc='"+HRS+"',rc_cancod='"+CDL+"',\
						rc_canlog='"+USL+"',rc_desvin='',rc_baixat='2',\
						rc_obsest='"+ hisTo +"' WHERE rc_regist='"+ idT +"'"

						sql[2].execute(cance)

					sql[1].commit()
					del _mensagem

				except Exception, _reTornos:

					sql[1].rollback()
					del _mensagem
					grv = False

				conn.cls(sql[1])

				if grv == False:	alertas.dia(self.painel,u"[ Erro, Processo Interrompido ] Estorno de Titulos Desmenbrados!!\n"+(" "*140)+"\nRetorno:"+str(_reTornos),"Contas AReceber: Estorno de Titulos Desmenbrados")			
				if grv == True:

					""" Ajusta Valores no Conta Corrente """
					DB = Decimal( self.vCc.GetValue().replace( ',' , '' ) )
					CR = Decimal( self.vCd.GetValue().replace( ',' , '' ) )
					ic = self.p.ListaReceber.GetFocusedItem()

					aC = "" #-------------------------: Atualizacao da conta corrente
					TT = str( self.nTL.GetValue() ) #-: Nº Titulo

					if ( CR + DB ) != 0:
    					
						CD = str( self.p.ListaReceber.GetItem(ic, 11).GetText() )
						FA = str( self.p.ListaReceber.GetItem(ic, 26).GetText() )
						CL = str( self.nCL.GetValue() )
						DC = str( self.p.ListaReceber.GetItem(ic,  6).GetText() )
						FL = str( self.p.ListaReceber.GetItem(ic, 27).GetText() )
						HS = "Estorno em grupo do contas areceber"

						estornar_conta_corrente = False if str( self.p.ListaReceber.GetItem(ic, 7).GetText().split('-')[0] ) in ['02','03'] and len( login.filialLT[self.Filial][35].split(';') ) >= 121 and login.filialLT[self.Filial][35].split(';')[120] == 'T' else True
						""" { Quando houver estorno do titulo principal e esse for cheque }
							Nao debitar no conta corrente do cliente p/q o cheque voltou e estar na posse
							para um novo lancamento com outro cheque no mesmo valor ou pgamento em dinheiro do debito
							mais o credito gerado o cliente nao perde pq o estar retido, o maximo q a filial pode fazer e bloquei do uso do credito
							Monfardini Glaucia: 21-08-2018 15:50
						"""
						if estornar_conta_corrente:

						    forma.crdb(TT,CD,CL,DC,FL,"RE",HS,DB,CR,FA,self.painel, Filial = self.Filial )
						    aC = u"com atualizacao da conta corrente"

					soco.gravadados(TT,"Estorno de Titulos\n"+ self.mTv.GetValue() ,"Contas AReceber")
					
					"""  Estornar no controle de conta corrente  """

					self.p.selecionar(wx.EVT_BUTTON)
					alertas.dia(self.painel,u"Estorno de titulos desmenbrados, finalizado!!\n"+ aC +"\n"+(" "*140),"Contas Areceber: Estorno de titulos desmenbrados")
					
					self.sair(wx.EVT_BUTTON)

	def esTornarIndividual(self,event):

		if len( self.mTv.GetValue() ) < 15:
			
			alertas.dia(self.painel,"Motivo do estorno com menos de 15 letras...\n"+(" "*100),u"Contas Areceber: Estorno de Títulos")
			return

		numTT = self.Tpr.GetLabel().split(":")[1]
		numId = self.Tpr.GetLabel().split(":")[2]
		numero_dav = 'LR-'+numTT.strip()
		cc_documento = 'ER-'+numTT.strip()

		mensa = u"Estorno individual título Nº "+ numTT +" ID-"+ numId +"\nNome do cliente: "+ self.nCL.GetValue() +"\n\nConfirme p/estornar !!\n"+(" "*130)
		esTor = wx.MessageDialog(self.painel,mensa,"Contas Areceber: Estorno individual",wx.YES_NO|wx.NO_DEFAULT)

		if esTor.ShowModal() ==  wx.ID_YES:
			
			DTA = datetime.datetime.now().strftime("%Y-%m-%d")
			HRS = datetime.datetime.now().strftime("%T")
			CDL = str( login.uscodigo )
			USL = str( login.usalogin )

			his = ""
			if self.hsI !="":	his = "\n\n"+self.hsI  
			hisTo = self.hsI+u"Contas Areceber: Estorno de Titulos Individual Nº "+ numTT +" { "+ USL +"  "+ DTA +" "+ HRS +"}\n[ Motivo ]\n"+ self.mTv.GetValue() +his
			
			if type( hisTo ) == str:	hisTo = hisTo.decode("UTF-8") 
			
			conn = sqldb()
			sql  = conn.dbc("Contas Areceber: Estorno de títulos desmenbrados", fil = self.Filial, janela = self.painel )
			grv  = True

			estorno_contacorrente = ""
			if sql[0]:

				_mensagem = mens.showmsg("Contas Areceber: Estorno de titulos desmenbrados...\n\nAguarde...")

				try:

					"""  Pega dados do lancamento de credito no conta corrente para estornar no conta corrente  """
					if sql[2].execute("SELECT * FROM bancoconta WHERE bc_docume='"+ numero_dav+"'"):
						
						result_banco = sql[2].fetchone()

						#--// Numero do documento [ R ContasReceber, 01 Parcela ] { R-0000001/01 }
						numero_dav = cc_documento
						valor_liquido = str( result_banco[7] )
						forma_pagamento = '5-Estorno de contas areceber'
						bandeira = result_banco[11]
						filial = result_banco[12]
						tipo_lancamento = "21" #--// Estorno de contas areceber
						lancamento_longo = "Estorno de lancamento do contas areceber" + "\n\n"+hisTo if hisTo else ""+ "\n\n"+result_banco[10] if result_banco[10] else ""
						id_banco = result_banco[4]
						lancamento_curto = "Estorno contas areceber " + bandeira + "}" if bandeira else forma_pagamento +"}"
						plano_conta = result_banco[5]
						credito_debito = u"Dédito"
						modulo = "5-Estorno contas areceber"
						banco_origem = ""
						banco_destino = result_banco[16]
						numero_compoe = result_banco[17]
						data_ferencia = datetime.datetime.now().strftime("%Y/%m/%d")

						estorno_contacorrente = valor_liquido+'|'+lancamento_curto+'|'+lancamento_longo+'|D|'+numero_dav+'|'+plano_conta+\
						'|'+id_banco+'|'+credito_debito+'|'+modulo+'|'+tipo_lancamento+'|'+banco_origem+'|'+banco_destino+'|'+numero_compoe+'|'+data_ferencia

					estor = "UPDATE receber SET rc_status='',rc_canest='Aberto por estorno',rc_recebi='',\
							rc_dtcanc='00-00-0000',rc_hrcanc='00:00:00',rc_cancod='',\
							rc_canlog='',rc_desvin='',rc_baixat='',rc_estorn='1',\
							rc_obsest='"+ hisTo +"' WHERE rc_regist='"+ numId +"'"

					sql[2].execute(estor)
					sql[1].commit()
					del _mensagem

				except Exception, _reTornos:

					sql[1].rollback()
					del _mensagem
					grv = False

				conn.cls(sql[1])

				if grv == False:	alertas.dia(self.painel,u"[ Erro, Processo interrompido ] Estorno de titulos desmenbrados!!\n"+(" "*140)+"\nRetorno:"+str(_reTornos),"Contas AReceber: Estorno de titulos desmenbrados")			
				if grv == True:

					""" Ajusta Valores no Conta Corrente """
					DB = Decimal( self.vCc.GetValue().replace( ',' , '' ) )
					CR = Decimal( self.vCd.GetValue().replace( ',' , '' ) )
					ic = self.p.ListaReceber.GetFocusedItem()

					aC = "" #-------------------------: Atualizacao da conta corrente
					TT = str( self.nTL.GetValue() ) #-: Nº Titulo

					if ( CR + DB ) != 0:
							
						CD = str( self.p.ListaReceber.GetItem(ic, 11).GetText() )
						FA = str( self.p.ListaReceber.GetItem(ic, 26).GetText() )
						CL = str( self.nCL.GetValue() )
						DC = str( self.p.ListaReceber.GetItem(ic,  6).GetText() )
						FL = str( self.p.ListaReceber.GetItem(ic, 27).GetText() )
						HS = "Estorno em grupo do contas areceber"
							
						estornar_conta_corrente = False if str( self.p.ListaReceber.GetItem(ic, 7).GetText().split('-')[0] ) in ['02','03'] and len( login.filialLT[self.Filial][35].split(';') ) >= 121 and login.filialLT[self.Filial][35].split(';')[120] == 'T' else True
						""" { Quando houver estorno do titulo principal e esse for cheque }
							Nao debitar no conta corrente do cliente p/q o cheque voltou e estar na posse
							para um novo lancamento com outro cheque no mesmo valor ou pgamento em dinheiro do debito
							mais o credito gerado o cliente nao perde pq o estar retido, o maximo q a filial pode fazer e bloquei do uso do credito
							Monfardini Glaucia: 21-08-2018 15:50
						"""
						"""  Estornar no controle de conta corrente  """
						if estornar_conta_corrente:

						    forma.crdb(TT,CD,CL,DC,FL,"RE",HS,DB,CR,FA,self.painel)
						    aC = u"com atualização da conta corrente"

					soco.gravadados(TT, hisTo ,"Contas AReceber")
					
					if estorno_contacorrente:	contaco.gravarLancamentosNovos( dados = estorno_contacorrente, parent = self, mostrar = False, numero_apagar='' )
					
					self.p.selecionar(wx.EVT_BUTTON)
					alertas.dia(self.painel,u"Estorno de titulos desmenbrados, finalizado!!\n"+ aC +"\n"+(" "*140),"Contas Areceber: Estorno de titulos desmenbrados")
					
					self.sair(wx.EVT_BUTTON)

	def chkBox(self,event):

		indice = self.RelaTiTulos.GetFocusedItem()
		nLanca = str( self.RelaTiTulos.GetItem(indice, 1).GetText() + "/" + self.RelaTiTulos.GetItem(indice, 2).GetText() )
		sTaTus = str( self.RelaTiTulos.GetItem(indice, 6).GetText() )
		idLanc = str( self.RelaTiTulos.GetItem(indice, 9).GetText() )

		vlCred = str( self.RelaTiTulos.GetItem(indice, 14).GetText() )
		vlDebi = str( self.RelaTiTulos.GetItem(indice, 15).GetText() )

		if self.Tpr.GetValue() == True and sTaTus in ["2"]:
			
			self.Tpr.SetLabel(u"Estornar Título Nº: "+nLanca+ ":" + idLanc)
			self.vCc.SetValue( vlCred )
			self.vCd.SetValue( vlDebi )

			self.indivi.Enable(True)
			self.agrupa.Enable(False)
			self.agrupa.SetBackgroundColour('#7F7F7F')
			self.indivi.SetBackgroundColour('#E5E5A6')

			self.hsI = str( self.RelaTiTulos.GetItem(indice, 16).GetText() )
		
		elif self.Tpr.GetValue() == True and sTaTus == "":

			self.Tpr.SetLabel(u"Marcar o título p/estornar"+(" "*30))
			self.Tpr.SetValue(False)

			self.indivi.Enable(False)
			self.agrupa.Enable(True)
			self.indivi.SetBackgroundColour('#7F7F7F')
			self.agrupa.SetBackgroundColour('#E5E5A6')

			self.vCc.SetValue( format( self.TcC, ',' ) )
			self.vCd.SetValue( format( self.TcD, ',' ) )
			self.hsI = ""

		elif self.Tpr.GetValue() == True and sTaTus == "1":

			self.Tpr.SetLabel(u"Marcar o título p/estornar"+(" "*20))
			self.Tpr.SetValue(False)

			self.indivi.Enable(False)
			self.agrupa.Enable(True)
			self.indivi.SetBackgroundColour('#7F7F7F')
			self.agrupa.SetBackgroundColour('#E5E5A6')

			self.vCc.SetValue( format( self.TcC, ',' ) )
			self.vCd.SetValue( format( self.TcD, ',' ) )
			self.hsI = ""

		elif self.Tpr.GetValue() == False:

			self.Tpr.SetLabel(u"Marcar o título p/estornar"+(" "*20))
			self.vCc.SetValue( format( self.TcC, ',' ) )
			self.vCd.SetValue( format( self.TcD, ',' ) )

			self.indivi.Enable(False)
			self.agrupa.Enable(True)
			self.indivi.SetBackgroundColour('#7F7F7F')
			self.agrupa.SetBackgroundColour('#E5E5A6')
			self.hsI = ""
			
		if self.VincTiTulos.GetItemCount() == 0:
			
			self.agrupa.Enable(False) 
			self.agrupa.SetBackgroundColour('#7F7F7F')
			self.hsI = ""

	def Teclas(self,event):
		
		""" Retorna Nº de Caracter do Motivo """
		self.nCa.SetLabel("15-"+str( len( self.mTv.GetValue() ) ) )

class TitulosDemembrados(wx.Frame):

	def __init__(self, parent,id):

		self.p = parent

		indice = self.p.ListaReceber.GetFocusedItem()
		self.d = self.p.ListaReceber.GetItem(indice,0).GetText()
		self.r = self.p.ListaReceber.GetItem(indice,24).GetText()

		wx.Frame.__init__(self, parent, id, 'Contas AReceber: { Relação de Títulos Desmembrados }', size=(800,300), style=wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,style = wx.BORDER_SUNKEN)

		self.RelaTiTulos = wx.ListCtrl(self.painel, 420,pos=(30,0), size=(770,280),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.RelaTiTulos.SetBackgroundColour('#B1CFEC')
		self.RelaTiTulos.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.RelaTiTulos.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.impresDav)

		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		self.RelaTiTulos.InsertColumn(0, 'Tipo',      width=80)
		self.RelaTiTulos.InsertColumn(1, 'Nº Dav/Título', width=120)
		self.RelaTiTulos.InsertColumn(2, 'Nº NF',         width=80)
		self.RelaTiTulos.InsertColumn(3, 'Emissão',       width=110)
		self.RelaTiTulos.InsertColumn(4, 'Descrição do Cliente', width=265)
		self.RelaTiTulos.InsertColumn(5, 'Valor', format=wx.LIST_ALIGN_LEFT, width=100)
		self.RelaTiTulos.InsertColumn(6, 'DAV-Original', width=200)

		wx.StaticText(self.painel,-1,"Click duplo p/visualizar DAV...",pos=(32,282)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.oco = wx.StaticText(self.painel,-1,"",pos=(650,282))
		self.oco.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.relacaoTitulos()

	def impresDav(self,event):
		
		indic = self.RelaTiTulos.GetFocusedItem()
		nTipo = self.RelaTiTulos.GetItem(indic,0).GetText()
		nDavs = self.RelaTiTulos.GetItem(indic,1).GetText()
		
		if nTipo.upper() == "DAV":
	
			impress.impressaoDav( nDavs.split('/')[0], self, True, True,  "", "", servidor = self.p.filrc, codigoModulo = "", enviarEmail = "", recibo=False )

		else:	alertas.dia(self,u"Documento selecionado não e um Dav valido...\n"+(" "*100),u"Contas Areceber: Títulos desmembrados")
		
	def relacaoTitulos(self):
		
		ind = 0
		rlT = []
		for i in self.r.split("|"):
			
			if ind !=0 and i !='':	rlT.append( i )
			ind +=1

		self.oco.SetLabel(u"Ocorrências: { "+str( len( rlT ) )+" }")

		conn = sqldb()
		sql  = conn.dbc("Contas Areceber: Relação de títulos desmembrados", fil = self.p.filrc, janela = self.painel )
		indi = 0

		if sql[0] == True:

			for sl in sorted(rlT):

				nT = ""
				em = ""
				nc = ""
				vl = ""
				nf = ""
				nd = sl
				
				nT = "Receber"
				if sl.split("/")[0].isdigit() == False:
					
					if sql[2].execute( "SELECT * FROM receber WHERE rc_ndocum='"+str( sl.split("/")[0] )+"' and rc_nparce='"+str( sl.split("/")[1] )+"'") !=0:

						rc = sql[2].fetchall()[0]
						
						em = str( rc[7].strftime("%d/%m/%Y") )+" "+str( rc[8] )+" "+str( rc[10] )
						nc = str( rc[12] )
						nf = str( rc[59] )
						vl = format( rc[18],',' )
						
				else:
					
					nDav = sl.split("/")[0]
					if sql[2].execute( "SELECT * FROM cdavs WHERE cr_ndav='"+str( sl.split("/")[0] )+"'" ) !=0:

						nT = "DAV"
						rs = sql[2].fetchall()[0]
						
						em = str( rs[11].strftime("%d/%m/%Y") )+" "+str( rs[12] )+" "+str( rs[9] )
						nc = str( rs[4] )
						nf = str( rs[8] )
						vl = format( rs[37],',' )
						
					else:	nT = u"Não Localizado"
						
				self.RelaTiTulos.InsertStringItem( indi, nT )
				self.RelaTiTulos.SetStringItem(indi,1, sl)	
				self.RelaTiTulos.SetStringItem(indi,2, nf)	
				self.RelaTiTulos.SetStringItem(indi,3, em)	
				self.RelaTiTulos.SetStringItem(indi,4, nc)	
				self.RelaTiTulos.SetStringItem(indi,5, vl)
				if indi % 2:	self.RelaTiTulos.SetItemBackgroundColour(indi, "#9CBFE1")
			
				indi +=1

			conn.cls( sql[1] )
			
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#2F6F83") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Contas Areceber "+str(self.d)+"\nRelação de Desmembramentos", 0, 297, 90)

class GerenciadorOcorrencias(wx.Frame):

	numero_dc = ""
	nuparcela = ""
	nmcliente = ""
	id_filial = ""
	moduloacs = ""
	
	def __init__(self, parent,id):

		self.p = parent

		wx.Frame.__init__(self, parent, id, 'Grenciador de ocorrencias de davs-titulos desmenbrados', size=(800,375), style=wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.RelaTiTulos = wx.ListCtrl(self.painel, 420,pos=(0,50), size=(799,180),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.RelaTiTulos.SetBackgroundColour('#9CBAD7')
		self.RelaTiTulos.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.RelaTiTulos.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.consultarTitulo)

		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		self.RelaTiTulos.InsertColumn(0, 'Tipo', width=250)
		self.RelaTiTulos.InsertColumn(1, 'Nº Dav/Título',format=wx.LIST_ALIGN_LEFT, width=120)
		self.RelaTiTulos.InsertColumn(2, 'Data', format=wx.LIST_ALIGN_LEFT, width=80)
		self.RelaTiTulos.InsertColumn(3, 'Valor',format=wx.LIST_ALIGN_LEFT, width=110)
		self.RelaTiTulos.InsertColumn(4, 'Pagamento/Recebimento', width=265)
		self.RelaTiTulos.InsertColumn(5, 'Valor', format=wx.LIST_ALIGN_LEFT, width=100)
		self.RelaTiTulos.InsertColumn(6, 'DAV-Original', width=200)

		wx.StaticText(self.painel,-1,"Numero DAV-Titulo",pos=(3,0)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Origem",pos=(160,0)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Descrição do cliente/fornecedor",pos=(313,0)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Historico do cancelamento/estorno",pos=(53,237)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Historico observação/estorno",pos=(433,237)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.dav_titulo = wx.TextCtrl(self.painel,-1,value=str( self.numero_dc )+'/'+str( self.nuparcela ), pos=(0, 13), size=(140,20),style = wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.dav_titulo.SetBackgroundColour('#E5E5E5')
		self.dav_titulo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.dav_origem = wx.TextCtrl(self.painel,-1,value="", pos=(157, 13), size=(140,20),style = wx.TE_READONLY)
		self.dav_origem.SetBackgroundColour('#E5E5E5')
		self.dav_origem.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.cdescricao = wx.TextCtrl(self.painel,-1,value=str( self.nmcliente ), pos=(310, 13), size=(490,20),style = wx.TE_READONLY)
		self.cdescricao.SetBackgroundColour('#E5E5E5')
		self.cdescricao.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self._canest = wx.TextCtrl(self.painel,-1,value = '', pos=(50, 250), size=(362,117),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self._canest.SetBackgroundColour('#BFBFBF')
		self._canest.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self._bosest = wx.TextCtrl(self.painel,-1,value = '', pos=(430, 250), size=(368,117),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self._bosest.SetBackgroundColour('#BFBFBF')
		self._bosest.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.saida = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/voltap.png", wx.BITMAP_TYPE_ANY), pos=(10,250), size=(36,36))
		self.ocorr = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/ocorrencia.png", wx.BITMAP_TYPE_ANY), pos=(10,293), size=(36,36))
		self.prndv = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/printp.png", wx.BITMAP_TYPE_ANY), pos=(10,333), size=(36,36))
		self.ocorr.SetBackgroundColour("#6F9BC8")
		self.prndv.SetBackgroundColour("#477EB6")

		self.saida.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.prndv.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ocorr.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.RelaTiTulos.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.saida.Bind (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.prndv.Bind (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ocorr.Bind (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.RelaTiTulos.Bind (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.levantarOcorrencias(wx.EVT_BUTTON)
		self.saida.Bind(wx.EVT_BUTTON, self.sair)
		self.prndv.Bind(wx.EVT_BUTTON, self.impressaoDocumento)
		self.ocorr.Bind(wx.EVT_BUTTON, self.ocorrenciasGeral)

	def sair(self,event):	self.Destroy()
	def consultarTitulo(self,event):

		if self.RelaTiTulos.GetItemCount():

			indice = self.RelaTiTulos.GetFocusedItem()
			_tip = self.RelaTiTulos.GetItem( indice, 0 ).GetText().split('-')[0]
			_doc = self.RelaTiTulos.GetItem( indice, 1 ).GetText()
			
			if _tip == "1":	self.p.gerenteOcorrenciaNovo( _doc, self.id_filial, self.nmcliente )
			if _tip == "4":	bordero.resumoBordero( _doc, self.painel, Filial = self.p.filrc )
			
			if _tip == "2":

				formarecebimentos.dav = str( _doc.split('/')[0] )
				formarecebimentos.mod = ""
				formarecebimentos.dev = False
				formarecebimentos.ffl =  self.p.filrc

				frcb_frame=formarecebimentos( parent=self, id=-1 )
				frcb_frame.Centre()
				frcb_frame.Show()

			if _tip == "3":

				contasApagar.numero = _doc
				alt_frame=contasApagar(parent=self,id = event.GetId() )
				alt_frame.Centre()
				alt_frame.Show()

		if _tip == "9":	self.ocorrenciasGeral(wx.EVT_BUTTON)
		
	def ocorrenciasGeral(self,event):

		indice = self.RelaTiTulos.GetFocusedItem()
		_tip = self.RelaTiTulos.GetItem( indice, 0 ).GetText().split('-')[0]
		_doc = self.RelaTiTulos.GetItem( indice, 1 ).GetText()

		if _tip in ["1","2","9"]:
			
			if _doc.split("/")[0][( len( _doc.split("/")[0] )-2 ):].upper() == "DR":	formarecebimentos.mod = "RC"
			else:	formarecebimentos.mod = ""

			formarecebimentos.dav = str( _doc.split('/')[0] )
			formarecebimentos.dev = False
			formarecebimentos.ffl =  self.p.filrc

			frcb_frame=formarecebimentos( parent=self, id=-1 )
			frcb_frame.Centre()
			frcb_frame.Show()

	def impressaoDocumento(self,event):

		if self.RelaTiTulos.GetItemCount():
			
			indic = self.RelaTiTulos.GetFocusedItem()
			nTipo = self.RelaTiTulos.GetItem(indic,0).GetText().split('-')[0]
			nDavs = self.RelaTiTulos.GetItem(indic,1).GetText()

			if nTipo == "2":
		
				impress.impressaoDav( nDavs.split('/')[0], self, True, True,  "", "", servidor = self.p.filrc, codigoModulo = "", enviarEmail = "", recibo=False )

			else:	alertas.dia(self,u"Documento selecionado não e um Dav valido...\n"+(" "*100),"Contas Areceber: Gerenciador de desmembramento")

		else:	alertas.dia(self,"Lista de documentos vazio...\n"+(" "*100),"Contas Areceber: Gerenciador de desmembramento")
		
	def levantarOcorrencias(self,event):

		if    self.moduloacs == "RC" and self.numero_dc[( len( self.numero_dc )-2 ):].upper() == "DR":	self.buscarTitulos( 1 ) #--: Titulo desmenbrado pelo contas areceber
		elif  self.moduloacs == "RC" and not self.numero_dc[( len( self.numero_dc )-2 ):].upper() == "DR":	self.buscarTitulos(  2 ) #--: Titulo original pelo contas areceber

	def buscarTitulos(self, tipo ):

		conn = sqldb()
		sql  = conn.dbc("Contas AReceber: Consulta de Debitos", fil = self.id_filial, janela = self.painel )

		if sql[0] == True:

			indice = 0

			self.RelaTiTulos.InsertStringItem( indice, "9-DAV-Titulo principal" )
			self.RelaTiTulos.SetStringItem( indice, 1, str( self.numero_dc )+"/"+str( self.nuparcela ) )
			self.RelaTiTulos.SetItemBackgroundColour(indice, "#E5E59A")

			indice +=1
			if sql[2].execute("SELECT rc_origem,rc_canest,rc_obsest,rc_compro,rc_histor,rc_borrtt,rc_relapa,rc_border, rc_tipods FROM receber WHERE rc_ndocum='"+str( self.numero_dc )+"' and rc_nparce='"+str( self.nuparcela )+"'"):

				i =sql[2].fetchone()
				origem = ""

				if   i[0] == "V":	origem = "Vendas"
				elif i[0] == "R":	origem = "Contas areceber"
				elif i[0] == "P":	origem = "Contas apagar"
				elif i[0] == "A":	origem = "Descmenbramento"
				self.dav_origem.SetValue( origem )
					
				if i[3]:
					
					for d in i[3].split('|'):

						if d:

							_titulo = "1-Desmenbramento" if d.split("/")[0][( len( d.split("/")[0] )-2 ):].upper() == "DR" else "2-Titulo original de recebimento"
							if i[6]:	_titulo = u"1-Lançamento atraves do contas pagar"
								
							self.RelaTiTulos.InsertStringItem( indice, _titulo )
							self.RelaTiTulos.SetStringItem( indice, 1, d.split(";")[0] )
							self.RelaTiTulos.SetStringItem( indice, 2, d.split(";")[1] )
							self.RelaTiTulos.SetStringItem( indice, 3, d.split(";")[2] )
							self.RelaTiTulos.SetStringItem( indice, 4, d.split(";")[4] )
							if indice % 2:	self.RelaTiTulos.SetItemBackgroundColour(indice, "#B1CFEC")

							indice +=1

				if i[4]:
						
					if i[0].upper() == "P" and "<LCR>"  in i[4].upper():

						apagar = i[4].split('[')[1].replace("</lcr>","").replace("]","").split("|")

						for ap in apagar:

							if ap:
									
								self.RelaTiTulos.InsertStringItem( indice, "3-Lançamento do saldo negativo apagar" )
								self.RelaTiTulos.SetStringItem( indice, 1, ap )
								if indice % 2:	self.RelaTiTulos.SetItemBackgroundColour(indice, "#B1CFEC")

								indice +=1

				if i[5] and i[7]:
						
					bordero_tipo = ""
					if   i[8] == "1":	bordero_tipo = "Deposito"
					elif i[8] == "2":	bordero_tipo = "Desconto"
					elif i[8] == "3":	bordero_tipo = "Pagamentos"
					elif i[8] == "4":	bordero_tipo = u"Liquidação atraves contas apagar"

					self.RelaTiTulos.InsertStringItem( indice, "4-Bordero "+str( bordero_tipo ) )
					self.RelaTiTulos.SetStringItem( indice, 1, i[7] )
					if indice % 2:	self.RelaTiTulos.SetItemBackgroundColour(indice, "#B1CFEC")

					indice +=1
							
				if i[6]:

					for ap in i[6].split('|'):

						if ap:
									
							self.RelaTiTulos.InsertStringItem( indice, "4-Liquidação atraves do contas apagar" )
							self.RelaTiTulos.SetStringItem( indice, 1, ap )
							if indice % 2:	self.RelaTiTulos.SetItemBackgroundColour(indice, "#B1CFEC")

							indice +=1
					
				if i[1]:	self._canest.SetValue( i[1] )
				if i[2]:	self._bosest.SetValue( i[2] )
				
			conn.cls( sql[1] )

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 101:	sb.mstatus("  Sair do grerenciador",0)
		elif event.GetId() == 102:	sb.mstatus("  Visualizar, reimpressão do dav",0)
		elif event.GetId() == 103:	sb.mstatus("  Registro de ocorrencias do dav-desmenbramento",0)
		elif event.GetId() == 420:	sb.mstatus("  Click duplo para consultar titulo { Recebimento, Bordero, Consulta em contas apagar }",0)

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Contas areceber: Gerenciador de ocorrencias de titulos",0)
		event.Skip()
							
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#2F6F83") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Contas Areceber "+str( self.id_filial ), 0, 373, 90)

class ValidacoesReceber:
	
    def validacaoBaixas(self, sql, itens, lista_controle ):

	retorno = False, ""
	for i in range(itens):

	    if lista_controle.GetItem( i, 0 ).GetText().upper() == "BAIXA":
			
		id_registro = str( lista_controle.GetItem( i, 20 ).GetText() )

		if sql[2].execute("SELECT rc_regist, rc_status,rc_bxlogi,rc_dtbaix,rc_hsbaix, rc_dtcanc,rc_hrcanc,rc_canlog FROM receber WHERE rc_regist='"+ id_registro +"'"):
												
		    __rs = sql[2].fetchone()
		    if __rs[1] == "1":	retorno = True, u"Baixado" # Baixado
		    if __rs[1] == "2":	retorno = True, u"Liquidação" # Liquidação
		    if __rs[1] == "3":	retorno = True, u"Conciliação" # Conciliacao bancaria
		    if __rs[1] == "4":	retorno = True, u"Cancelado p/desmenbramento" # Cancelado p/desmembramento
		    if __rs[1] == "5":	retorno = True, u"Cancelado" # Cancelado

	return retorno

    def baixaTitulosConciliacao(self,par=None, lista=None, filial=None):

	conn = sqldb()
	sql  = conn.dbc("Contas AReceber: Conciliação bancaria", fil=filial, janela=par)
	
	baixados=''
	baixas=False
	if sql[0]== True:

	    for i in lista:

		achar="SELECT rc_ndocum,rc_nparce,rc_formap,rc_vencim,rc_apagar,rc_status FROM receber WHERE rc_regist='"+ i +"'"
		if lista[i][3]=='2':	achar="SELECT rc_ndocum,rc_nparce,rc_formap,rc_vencim,rc_apagar,rc_status FROM receber WHERE rc_ndocum='"+ i +"'"
		
		if sql[2].execute(achar):

		    result=sql[2].fetchone()
		    valor_pago=lista[i][1]
		    numero_dav=result[0]
		    numparcela=result[1]
		    fpagamento=result[2]
		    
		    valorapaga=str(result[4])
		
		    jur="0.00"
		    dBa=datetime.datetime.now().strftime("%Y/%m/%d")
		    hBa=datetime.datetime.now().strftime("%T")
		    usa=login.usalogin
		    cus=login.uscodigo
		    ven=result[3].strftime("%d/%m/%Y")

		    gravar = "UPDATE receber SET rc_bxcaix=%s,rc_bxlogi=%s,rc_vlbaix=%s,rc_dtbaix=%s,rc_hsbaix=%s,\
		    rc_formar=%s,rc_status=%s,rc_canest=%s,rc_recebi=%s,rc_baixat=%s,rc_modulo=%s,rc_acresc=%s WHERE rc_regist=%s"
		    
		    if lista[i][3]=='2': #--// Nossa cobranca
			gravar = "UPDATE receber SET rc_bxcaix=%s,rc_bxlogi=%s,rc_vlbaix=%s,rc_dtbaix=%s,rc_hsbaix=%s,\
			rc_formar=%s,rc_status=%s,rc_canest=%s,rc_recebi=%s,rc_baixat=%s,rc_modulo=%s,rc_acresc=%s WHERE rc_ndocum=%s"

		    """ Grava Ocorrencias """
		    _lan  = datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin
		    _tip  = "Contas AReceber"
		    _oco  = "Conciliacao de titulos\n"+\
		    "Lancamento: "+_lan+\
		    "\n\nDAV/Comanda: "+numero_dav+'-'+numparcela+\
		    "\nVencimento: "+ven+\
		    "\nValor: "+valorapaga+\
		    "\nAtraso: "+\
		    "\nJuros: "+jur+\
		    "\nMulta: "+\
		    "\nValor Apagar: "+valorapaga+\
		    "\nForma Pagamento: "+fpagamento+\
		    "\nValor Baixado: "+valor_pago

		    """ Gravando Ocorrencia """
		    valor = "insert into ocorren (oc_docu,oc_usar,oc_corr,oc_tipo,oc_inde)\
		    values (%s,%s,%s,%s,%s)"			

		    _gST = "2"
		    _gHS = 'Baixa por conciliacao'
		    _gBX = '1'

		    __bx='{Marca de baixa} ' if result[5] else ''
		    if not result[5]:

			baixa=sql[2].execute(gravar, (cus,usa,valor_pago,dBa,hBa,fpagamento,_gST,_gHS,'1',_gBX,login.rcmodulo,jur,i) )
			sql[2].execute(valor, (numero_dav, _lan, _oco, _tip, filial))

			if baixa:
			    baixados+='Baixado....: '+i+'-'+lista[i][2]+'\n'
			    baixas=True
			    
			else:	baixados+=__bx+'Nao baixado: '+i+'-'+lista[i][2]+'\n'
		    else:	baixados+=__bx+'Nao baixado: '+i+'-'+lista[i][2]+'\n'
	    
	    if baixas:	sql[1].commit()
	    conn.cls(sql[1])
	
	return baixados

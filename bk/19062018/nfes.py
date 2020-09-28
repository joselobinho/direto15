#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import datetime
import os,glob
import zipfile
import shutil
#import wx.lib.mixins.listctrl as listmix
import commands

from conectar import sqldb,gerenciador,listaemails,dialogos,cores,login,menssagem,sbarra
from decimal import Decimal
from ConfigParser import SafeConfigParser

alertas = dialogos()
mens    = menssagem()
sb      = sbarra()

parser = SafeConfigParser()
parser.read('srv/config.ini')

class GerenciarNFe(wx.Frame):

	relNfes  = {}
	registro = 0
	
	def __init__(self, parent,id):
		
		self.p = parent
		self.r = 0
		self.n = int(parser.get('nfe','ambiente')[:1])

		nfamb = "Produção"
		if self.n == 2:	nfamb = "Homologação" 

		wx.Frame.__init__(self, parent, id, 'Gerênciador de NFes', size=(900,500), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)

		self.cadNFes = NFListCtrl(self.painel, 300 ,pos=(10,2), size=(885,390),
							style=wx.LC_REPORT
							|wx.LC_VIRTUAL
							|wx.BORDER_SUNKEN
							|wx.LC_HRULES
							|wx.LC_VRULES
							|wx.LC_SINGLE_SEL
							)

		self.cadNFes.SetBackgroundColour('#7DA2B1')
		self.cadNFes.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		#self.Bind(wx.EVT_KEY_UP, self.Teclas)
		self.cadNFes.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passar)

		wx.StaticText(self.painel,-1,'Periódo', pos=(18,422)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.hompd = wx.TextCtrl(self.painel,-1,nfamb, pos=(15,400) ,size=(115,18),style = wx.TE_READONLY)
		self.hompd.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.hompd.SetBackgroundColour('#E5E5E5')
		self.hompd.SetForegroundColour('#1C5F9F')

		procura = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/procurap.png", wx.BITMAP_TYPE_ANY), pos=(260,455), size=(36,34))				
		voltar  = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltam.png",   wx.BITMAP_TYPE_ANY), pos=(320,455), size=(36,34))
		enviar  = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/email.png",    wx.BITMAP_TYPE_ANY), pos=(364,455), size=(36,34))
		enviar.SetBackgroundColour('#BFBFBF')

		conta = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/contador.png", wx.BITMAP_TYPE_ANY), pos=(408,455), size=(36,34))				

		self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(15,435), size=(110,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(15,465), size=(110,25))

		self.TDNFs = wx.RadioButton(self.painel,-1,"Todos            ", pos=(145,400),style=wx.RB_GROUP)
		self.EMNFs = wx.RadioButton(self.painel,-1,"Emitidos         ", pos=(145,425))
		self.NENFs = wx.RadioButton(self.painel,-1,"Não emitidas     ", pos=(145,445))
		self.CANFs = wx.RadioButton(self.painel,-1,"Cancelados       ", pos=(145,470))

		self.TDNFs.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.EMNFs.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.NENFs.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.CANFs.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		Tipo = ['1-NFes de Vendas','2-NFes de devolução de vendas','3-NFes de devolução de compras','4-NFes de transferência']
		self.TNFes = wx.ComboBox(self.painel, -1, Tipo[0],  pos=(260,400),  size=(250,24), choices = Tipo,style=wx.CB_SORT)
	
		procura.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		voltar .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		enviar .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		conta  .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
	
		procura.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		voltar .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		enviar .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		conta  .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		voltar. Bind(wx.EVT_BUTTON, self.sair)
		procura.Bind(wx.EVT_BUTTON, self.selecionar)
		conta.  Bind(wx.EVT_BUTTON, self.pararaFilesZip)

		self.TDNFs.Bind(wx.EVT_RADIOBUTTON, self.selecionar)
		self.EMNFs.Bind(wx.EVT_RADIOBUTTON, self.selecionar)
		self.NENFs.Bind(wx.EVT_RADIOBUTTON, self.selecionar)
		self.CANFs.Bind(wx.EVT_RADIOBUTTON, self.selecionar)
		
		self.TNFes.Bind(wx.EVT_COMBOBOX, self.EventoCombo)

		self.selecionar(wx.EVT_BUTTON)

	def sair(self,event):	self.Destroy()
	def pararaFilesZip(self,event):
		
		nRg = self.cadNFes.GetItemCount()
		val = False

		Rela = "vendas"
		if self.TNFes.GetValue()[:1] == '2':	Rela = "devolucao_vendas"
		if self.TNFes.GetValue()[:1] == '3':	Rela = "devolucao_compras"
		if self.TNFes.GetValue()[:1] == '4':	Rela = "estoque_transferencia"

		Tipo = "geral"
		if self.EMNFs.GetValue() == True:	Tipo = "vendas"
		if self.CANFs.GetValue() == True:	Tipo = "canceladas"

		ind = 0
		for x in range(nRg):

			if self.cadNFes.GetItem(ind,11).GetText() !='':	val = True
			ind +=1
			
		if val == True:

			try:
				
				pasTa = "nfe/"+str(datetime.datetime.now().strftime("%m-%Y"))
				if os.path.exists("nfe/contabilidade") == False:	os.makedirs("nfe/contabilidade")
				if os.path.exists(pasTa) == False:	os.makedirs(pasTa)
				if os.path.exists(pasTa) == True:

					selarq = pasTa+"/*.xml"
					lisarq = glob.glob(selarq)
					for ar in lisarq:	os.remove(ar)
				
			except Exception, _reTornos:	pass

			try:

				
				""" Copia para a pasta """
				ind = 0
				for p in range(nRg):

					if self.cadNFes.GetItem(ind,11).GetText() !='':

						xmls = self.cadNFes.GetItem(ind,11).GetText()
						shutil.copy2(xmls, pasTa)

					ind +=1
					
				hoje = datetime.datetime.now().strftime("%d%m%Y")
				arq  = 'nfe/contabilidade/xmls'+hoje+login.emfantas.lower().replace(' ','')+'_'+Tipo+'_'+Rela+'.zip'
				zf   = zipfile.ZipFile(arq, mode='w')

				for dirname, subdirs, files in os.walk(pasTa):
					zf.write(dirname)
					for filename in files:
						zf.write(os.path.join(dirname, filename))
				
		
#				zf = zipfile.ZipFile("myzipfile.zip", "w")
#				for dirname, subdirs, files in os.walk("mydirectory"):
#					zf.write(dirname)
#					for filename in files:
#						zf.write(os.path.join(dirname, filename))
#				zf.close()		
				
				
				
				
				
				
				
				
				#zf.write(pasTa+"/*.xml")
				#zf.close()
				
				#zf = zipfile.ZipFile(arq, mode='a')
				#ind = 0
				#for i in range(nRg):

					#ArquivoPasta = self.cadNFes.GetItem(ind,12).GetText()
					#if ArquivoPasta !='':	zf.write(ArquivoPasta)
					
				#	ind +=1
					
				zf.close()

				infoXml.arquivo = arq	
				inf_frame=infoXml(parent=self,id=-1)
				inf_frame.Centre()
				inf_frame.Show()

			except Exception, _reTornos:

				alertas.dia(self.painel,u"Erro na geração dos dados !!\n \nRetorno: "+str(_reTornos),"Retorno")	
				zf.close()
			
			
		else:	alertas.dia(self.painel,u"NFes não localizada na pasta de Nfes...\n"+(" "*100),u"Gerênciador de NFes")
		
	def EventoCombo(self,event):
		
		if self.TNFes.GetValue()[:1] == '1':

			self.cadNFes.SetBackgroundColour('#7DA2B1')
			self.cadNFes.attr1.SetBackgroundColour("#80A9BA")
			
		if self.TNFes.GetValue()[:1] == '2':

			self.cadNFes.SetBackgroundColour('#CEDCCE')
			self.cadNFes.attr1.SetBackgroundColour("#CBECCB")

		self.selecionar(wx.EVT_BUTTON)

	def passar(self,event):
		
		indice = self.cadNFes.GetFocusedItem()
		if self.cadNFes.GetItem(indice,10).GetText() !='':	self.cadNFes.SetItemTextColour(indice, '#FF0000')

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	sb.mstatus(u"Sair - Voltar",0)
		elif event.GetId() == 101:	sb.mstatus(u"Procurar NFes e Relacionar",0)
		elif event.GetId() == 102:	sb.mstatus(u"Enviar XML,PDF Selecionados por email",0)
		elif event.GetId() == 103:	sb.mstatus(u"Relacionar XMLs, Compactar para enviar para contabilidade",0)
				
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("Gerênciador de NFes: Enviar XML para a contabilidade",0)
		event.Skip()

	def selecionar(self,event):

		conn = sqldb()
		sql  = conn.dbc("Caixa: Gerênciador de NFes",1,login.identifi)

		if sql[0] == True:

			pasta = 'nfe/danfe/producao/'
			if self.n == 2:	pasta = 'nfe/danfe/homologacao/'
		
			daTaI = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			daTaF = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

			if   self.TDNFs.GetValue() == True:
#				if self.TNFes.GetValue()[:1] == '1':	vd = "SELECT * FROM cdavs WHERE cr_edav >=%s and cr_edav <=%s"
#				if self.TNFes.GetValue()[:1] == '2':	vd = "SELECT * FROM dcdavs WHERE cr_edav >=%s and cr_edav <=%s"

				if self.TNFes.GetValue()[:1] == '1':	vd = "SELECT * FROM cdavs WHERE cr_edav>='"+str(daTaI)+"' and cr_edav<='"+str(daTaF)+"'"
				if self.TNFes.GetValue()[:1] == '2':	vd = "SELECT * FROM dcdavs WHERE cr_edav>='"+str(daTaI)+"' and cr_edav<='"+str(daTaF)+"'"
				#vd = "SELECT * FROM cdavs WHERE cr_edav >=%s and cr_edav <=%s"
				venda  = sql[2].execute(vd)

			elif self.EMNFs.GetValue() == True:
#				if self.TNFes.GetValue()[:1] == '1':	vd = "SELECT * FROM cdavs WHERE cr_edav >=%s and cr_edav <=%s and cr_nfem!=%s and cr_chnf!=%s and cr_nfca=%s"
#				if self.TNFes.GetValue()[:1] == '2':	vd = "SELECT * FROM dcdavs WHERE cr_edav >=%s and cr_edav <=%s and cr_nfem!=%s and cr_chnf!=%s and cr_nfca=%s"

				if self.TNFes.GetValue()[:1] == '1':	vd = "SELECT * FROM cdavs WHERE cr_edav>='"+str(daTaI)+"' and cr_edav<='"+str(daTaF)+"' and cr_nfem!='' and cr_chnf!='' and cr_nfca=''"
				if self.TNFes.GetValue()[:1] == '2':	vd = "SELECT * FROM dcdavs WHERE cr_edav>='"+str(daTaI)+"' and cr_edav<='"+str(daTaF)+"' and cr_nfem!='' and cr_chnf!='' and cr_nfca=''"
				venda  = sql[2].execute(vd)

			elif self.NENFs.GetValue() == True:
#				if self.TNFes.GetValue()[:1] == '1':	vd = "SELECT * FROM cdavs WHERE cr_edav >=%s and cr_edav <=%s and cr_nfem=%s and cr_chnf=%s"
#				if self.TNFes.GetValue()[:1] == '2':	vd = "SELECT * FROM dcdavs WHERE cr_edav >=%s and cr_edav <=%s and cr_nfem=%s and cr_chnf=%s"

				if self.TNFes.GetValue()[:1] == '1':	vd = "SELECT * FROM cdavs WHERE cr_edav>='"+str(daTaI)+"' and cr_edav<='"+str(daTaF)+"' and cr_nfem='' and cr_chnf=''"
				if self.TNFes.GetValue()[:1] == '2':	vd = "SELECT * FROM dcdavs WHERE cr_edav>='"+str(daTaI)+"' and cr_edav<='"+str(daTaF)+"' and cr_nfem='' and cr_chnf=''"
				venda  = sql[2].execute(vd)

			elif self.CANFs.GetValue() == True:
#				if self.TNFes.GetValue()[:1] == '1':	vd = "SELECT * FROM cdavs WHERE cr_edav >=%s and cr_edav <=%s and cr_nfca!=%s"
#				if self.TNFes.GetValue()[:1] == '2':	vd = "SELECT * FROM dcdavs WHERE cr_edav >=%s and cr_edav <=%s and cr_nfca!=%s"

				if self.TNFes.GetValue()[:1] == '1':	vd = "SELECT * FROM cdavs WHERE cr_edav>='"+str(daTaI)+"' and cr_edav<='"+str(daTaF)+"' and cr_nfca!=''"
				if self.TNFes.GetValue()[:1] == '2':	vd = "SELECT * FROM dcdavs WHERE cr_edav>='"+str(daTaI)+"' and cr_edav<='"+str(daTaF)+"' and cr_nfca!=''"
				venda  = sql[2].execute(vd)

			vendas = sql[2].fetchall()

			_registros = 0
			relacao    = {}
			pLista     = venda
			QuanTidade = 1

			self.cadNFes.DeleteAllItems()
			self.cadNFes.Refresh()
			
			for i in vendas:
				
				if i[8] !='': #-: Numero da NFe
					 
					emDav = format(i[11],"%d/%m/%Y")+" "+str(i[12])
					NfLsT = i[15].split(' ')
					NfCan = i[16].split(' ')
					DRn = emNFe = NfPro = caNFe = DNF = ''

					if NfLsT[0] !='':
						
						emNFe = format( datetime.datetime.strptime(NfLsT[0], "%Y-%m-%d"),"%d/%m/%Y")+' '+NfLsT[1]
						NfPro = NfLsT[2]

						DRp = pasta+NfLsT[0].split("-")[0]+"-"+NfLsT[0].split("-")[1].zfill(2)+"/"+parser.get('nfe','serie').zfill(3)+"-"+i[8].zfill(9)+"/"
						DNF = i[73]+"-nfe.xml"
						DRn = DRp+DNF

						if os.path.exists(DRn) == False:	DRn = ""
						
					if NfCan[0] !='':
						caNFe = format( datetime.datetime.strptime(NfCan[0],"%Y-%m-%d"),"%d/%m/%Y" )+' '+NfCan[1]+' '+NfCan[2]+NfCan[3]+' '+NfCan[4]
												
					relacao[_registros] = str(QuanTidade).zfill(5),"",emDav,i[8],emNFe,i[5],i[4],NfPro,i[73],i[74],caNFe,DRn,DNF

					_registros +=1
					QuanTidade +=1

			self.cadNFes.SetItemCount( ( QuanTidade - 1 ) )
			NFListCtrl.itemDataMap  = relacao
			NFListCtrl.itemIndexMap = relacao.keys()
				
			conn.cls(sql[1])
	
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#123B63") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Gerênciador de Notas Fiscais Eletrônica", 0, 495, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		dc.DrawRoundedRectangle(12,395,500,100,   3) #-->[ Lykos ]
	
#class NFListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
class NFListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):

		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

		self.il = wx.ImageList(16, 16)
		a={"sm_up":"UNDO","sm_dn":"REDO","w_idx":"TICK_MARK","e_idx":"WARNING","i_idx":"ERROR","i_orc":"GO_FORWARD","e_est":"CROSS_MARK"}

		for k,v in a.items():
			s="self.%s= self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_%s,wx.ART_TOOLBAR,(16,16)))" % (k,v)
			exec(s)

		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr2 = wx.ListItemAttr()
		self.attr3 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour("#80A9BA")
		self.attr2.SetBackgroundColour('#D67C7C')
		self.attr3.SetBackgroundColour('#4B79A5')

		self.InsertColumn(0, 'QTDE',   width=70)
		self.InsertColumn(1, 'Marcar', width=50)
		
		self.InsertColumn(2, 'Emissão DAV',         width=130)
		self.InsertColumn(3, 'Nº NFe',              format=wx.LIST_ALIGN_LEFT,width=80)
		self.InsertColumn(4, 'NFe Emissão',         width=150)
		self.InsertColumn(5, 'Fantasia' ,           width=200)
		self.InsertColumn(6, 'Fornecedor-Cliente' , width=400)
		self.InsertColumn(7, 'Nº Protocolo',        format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(8, 'Chave NFe',           format=wx.LIST_ALIGN_LEFT,width=380)
		self.InsertColumn(9, 'Recebimento',         width=100)
		self.InsertColumn(10,'Cancelamento',        width=300)
		self.InsertColumn(11,'Pasta da NFe',        width=900)
		self.InsertColumn(12,'Arquivo XMS',         width=900)
		
		#listmix.ColumnSorterMixin.__init__(self, 4)
			
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
			
			index = self.itemIndexMap[item]
			nfCan = self.itemDataMap[index][10]
			proto = self.itemDataMap[index][7]
			chave = self.itemDataMap[index][8]

			if nfCan != '':	return self.attr2
			if proto == '':	return self.attr3
			if chave == '':	return self.attr3
			if item % 2:	return self.attr1
			
	def GetListCtrl(self):	return self			

	def OnGetItemImage(self, item):

		if self.itemIndexMap != []:

			index=self.itemIndexMap[item]
			if self.itemDataMap[index][11] !='':	return self.w_idx
			else:	return ''

		else:	return ''

class infoXml(wx.Frame):

	arquivo = ''
	def __init__(self, parent,id):

		wx.Frame.__init__(self, parent, id, 'Gerênciador de NFes', size=(800,300), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		informacao = ''
		qTdArquivo = 0
		archive_name = self.arquivo

		zf = zipfile.ZipFile(archive_name)
		for info in zf.infolist():

			informacao += info.filename
			informacao += '\n\tComment:\t ' + str( info.comment )
			informacao += '\n\tModified:\t ' + str( datetime.datetime(*info.date_time) )
			informacao += '\n\tSystem:\t ' + str(info.create_system) #, '(0 = Windows, 3 = Unix)'
			informacao += '\n\tZIP version:\t ' + str( info.create_version )
			informacao += '\n\tCompressed:\t ' + str( info.compress_size) #, 'bytes'
			informacao += '\n\tUncompressed:\t ' + str( info.file_size ) #, 'bytes'
			informacao += '\n\n'
			qTdArquivo +=1

		wx.StaticText(self.painel,-1,'NFe Selecionadas', pos=(703,262)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Nome do Arquivo',  pos=(203,262)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		historico = wx.TextCtrl(self.painel,-1,value=informacao, pos=(15,0), size=(783,260),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		historico.SetBackgroundColour('#4D4D4D')
		historico.SetForegroundColour('#90EE90')
		historico.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.nomarq = wx.TextCtrl(self.painel,-1,value=str(archive_name), pos=(200,275), size=(400,18),style = wx.TE_READONLY)		
		self.nomarq.SetBackgroundColour('#E5E5E5')
		self.nomarq.SetForegroundColour('#4D4D4D')
		self.nomarq.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		nfesel = wx.TextCtrl(self.painel,-1,value=str(qTdArquivo), pos=(700,275), size=(92,18),style = wx.ALIGN_RIGHT|wx.TE_READONLY)		
		nfesel.SetBackgroundColour('#E5E5E5')
		nfesel.SetForegroundColour('#4D4D4D')
		nfesel.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		voltar  = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltap.png",   wx.BITMAP_TYPE_ANY), pos=(15,263), size=(32,32))
		enviar  = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/emailp.png",   wx.BITMAP_TYPE_ANY), pos=(60,263), size=(32,32))
		enviar.SetBackgroundColour('#BFBFBF')

		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		enviar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
	
		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		enviar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		enviar.Bind(wx.EVT_BUTTON, self.enviarArquivo)

	def sair(self,event):	self.Destroy()

	def enviarArquivo(self,event):
		
		emails = []
		emails.append(login.filialLT[login.identifi][25])
		gerenciador.emails = emails
		gerenciador.Anexar = self.nomarq.GetValue()
		ger_frame=gerenciador(parent=self,id=-1)
		ger_frame.Centre()
		ger_frame.Show()

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	sb.mstatus(u"Sair - Voltar",0)
		elif event.GetId() == 101:	sb.mstatus(u"Enviar Relação NFes {XML} pata contabilidade",0)
				
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("Gerênciador de NFes: Enviar XML para a contabilidade",0)
		event.Skip()

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#A52A2A") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Relação de NFes { Enviar para Contabilidade }", 0, 295, 90)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# RJ 28-11-2015
# Jose de Almeida Lobinho
# Emissao da NFE,NFCe Via ACBrMonitorPlus

import re
import os
import wx
import time
import unicodedata
import datetime
import socket
import ConfigParser
import StringIO

from xml.dom  import minidom
from decimal  import *
from conectar import menssagem,login,diretorios,numeracao,dialogos,sqldb
#from nfe310   import nfe31c,TraTaRetorno
from produtom import rTabelas

mens    = menssagem()
alertas = dialogos()
#nfe31RT = TraTaRetorno()

TTabelas= rTabelas()

nfclogs = diretorios.logsPsT+"nfce_excessao.txt"
emilogs = diretorios.logsPsT+"nfce_emissao.txt"

class acbrNFCe:
	
	def acbrNFCeStatus(self,parent):

		self.p = parent
		self.p.reTsD.SetValue("")
		
		rTn = acbRetornos()
		con = acbrTCP()

		cn = con.acbrAbrir( cnT=1, par = parent, fls = self.p.Filial )
		if cn[0] == False:	return
		
		self.s = cn[1]

#-----: Veririca se estar ATivo
		try:
			_menssag = mens.showmsg( "{ ACBrPlus } A T I V o"+self.p.TM )
			cmd1 = "NFE.Ativo"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
			self.s.send(cmd1)
			rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False  )

			err = False

#---------: Ok-Ativo
			rTNFCe = rTn.acbrAbrirRetornos( parent, op = 0, rT = rTo, nF = '' )
			if rTo.upper() == "OK: ATIVO":

					_menssag = mens.showmsg( "{ ACBrPlus } Status do WebServer-SEFAZ"+self.p.TM )
					cmd1 = "NFE.StatusServico"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
					self.s.send(cmd1)
					rTo, End, qrc,chv = rTn.acbrLimpa(op=1,s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False  )
					rTNFCe = rTn.acbrAbrirRetornos( parent, op = 0, rT = rTo, nF = '' )
					
					self.p.reTsD.SetForegroundColour("#EDED93")

					if rTNFCe[0] !=[]:
						
						rS = "[STATUS]\n"+\
							 "Ambiente.........: "+str( rTNFCe[0][0] )+"\n"+\
							 u"Código de Retorno: "+str( rTNFCe[0][1] )+"\n"+\
							 "Motivo...........: "+str( rTNFCe[0][2] )+"\n"+\
							 "U F..............: "+str( rTNFCe[0][3] )+"\n"+\
							 "DT-Recebimento...: "+str( rTNFCe[0][4] )+"\n"+\
							 "DT-Retorno.......: "+str( rTNFCe[0][5] )+"\n"+\
							 "Observação.......: "+str( rTNFCe[0][6] )+"\n"
					else:	rS = str( rTNFCe[4] )

					try:	rS = rS.decode('utf-8')
					except Exception, rsTry:
						
						de = str( datetime.datetime.now().strftime("%d-%m-%Y %T") )+" "+login.usalogin
						open(nfclogs,"a").write(de+" STATUS-Conversao do Retorno\n"+str( rTry )+"\n")
						rS = str( unicodedata.normalize('NFKD', rS.decode('CP1252')).encode('UTF-8', 'ignore') )

					self.p.reTsD.SetValue( rS )
						 
		except Exception, rTry:
			
			err = True
			de = str( datetime.datetime.now().strftime("%d-%m-%Y %T") )+" "+login.usalogin
			open(nfclogs,"a").write(de+" STATUS\n"+str( rTry )+"\n")
			
		del _menssag
		con.acbrFechar( cnf = self.s )
	
		if err == True:	alertas.dia(self.p,"Solitacões duplicadas, Não utilize clicks duplos...\n\nRetorno: "+str( rTry )+"\n"+(" "*140),"Clicks Duplos")

	def configuraNFCe(self,parent, fls ):
		

		d = login.filialLT[ fls ][30].split(";")
		r = login.filialLT[ fls ][38].split("|")[0].split(";")

		nfceidcsc = str( r[0] ).strip() #-: ID-CSC
		nfceiccsc = str( r[1] ).strip() #-: CSC
		nfcecerti = str( r[3] ).strip() #-: nome do certificado
		nfcesenha = str( r[4] ).strip() #-: senha do certificado
		nfceversa = str( r[6] ).strip() #-: Versao
		nfceambie = str( r[7] ).strip() #-: ambiente
		
		rTn = acbRetornos()
		con = acbrTCP()

		cn = con.acbrAbrir( cnT=1, par = parent, TipoNF = 1, fls = fls )
		if cn[0] == False:	return False
		
		self.s = cn[1]

#-----: Veririca se estar ATivo
		informar = ""
		error    = False
		err      = False
		cerwin   = True
		
		try:

			_menssag = mens.showmsg( "{ Configurando Ambiente-Plus }\nA T I V o"+parent.TM )
			cmd1 = "NFE.Ativo"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
			self.s.send(cmd1)
			rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False  )
			informar += "\nAmbiente-Plus Ativo "+str( rTo.decode('iso-8859-7').encode('utf8') )
			if "ERRO:" in rTo:	error = True

	#-------Ok-Ativo
			rTNFCe = rTn.acbrAbrirRetornos( parent, op = 1, rT = rTo, nF = '' )
			if rTo.upper() == "OK: ATIVO":

				pasta_certificado = "c:\\ACBrMonitorPlus\\"+str( nfcecerti )
				"""
					Verifica a existencia do XML na pasta c:\ACBrMonitorPlus\Logs
				"""	
				cmd1 = "NFE.FileExists("+str( pasta_certificado )+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
				self.s.send(cmd1)
				rTo, End, qrc, chv = rTn.acbrLimpa( op=1, s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False  )

				if "ERRO:" in rTo.upper():	cerwin = False
				if "OK:" in rTo.upper():

		#---------: Certificado { r[8] == 'T'>---> Configurar pasta e senha do certificado }
					if r[8] == "T":
						
						pasTaPFX = "c:\\ACBrMonitorPLUS\\"+nfcecerti #-: Pasta onde estar o certificado no windows
						_menssag = mens.showmsg( "{ Configurando Ambiente-Plus }\nPasta e Sennha do Certificado"+parent.TM )
						cmd1 = "NFE.SetCertificado("+pasTaPFX+","+nfcesenha+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
						self.s.send(cmd1)
						rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False  )
						rTNFCe = rTn.acbrAbrirRetornos( parent, op = 1, rT = rTo, nF = '' )

						informar += "\nPasta e Sennha do Certificado "+str( rTo.decode('iso-8859-7').encode('utf8') )
						if "ERRO:" in rTo:	error = True

		#---------: Versao da NFCe
					if r[9] == "T":

						_menssag = mens.showmsg( "{ Configurando Ambiente-Plus }\nVersão da NFCe"+parent.TM )
						cmd1 = "NFE.SetVersaoDF("+nfceversa+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
						self.s.send(cmd1)
						rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False  )
						rTNFCe = rTn.acbrAbrirRetornos( parent, op = 1, rT = rTo, nF = '' )

						informar += "\nVersão da NFCe "+str( rTo.decode('iso-8859-7').encode('utf8') )
						if "ERRO:" in rTo:	error = True

		#---------: Modelo da 55-65
					if r[10] == "T":

						_menssag = mens.showmsg( "{ Configurando Ambiente-Plus }\nModelo da NF 55-NFe, 65=NFCe"+parent.TM )
						cmd1 = "NFE.SetModeloDF(65)"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
						self.s.send(cmd1)
						rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False  )
						rTNFCe = rTn.acbrAbrirRetornos( parent, op = 1, rT = rTo, nF = '' )

						informar += "\nModelo da NF 55-NFe, 65=NFCe "+str( rTo.decode('iso-8859-7').encode('utf8') )
						if "ERRO:" in rTo:	error = True

		#---------: Ambiente Homologacao-Producao
					if r[11] == "T":

						_menssag = mens.showmsg( "{ Configurando Ambiente-Plus }\nAmbiente 1-Produção, 2-Homologação"+parent.TM )
						cmd1 = "NFE.SetAmbiente("+nfceambie+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
						self.s.send(cmd1)
						rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False  )
						rTNFCe = rTn.acbrAbrirRetornos( parent, op = 1, rT = rTo, nF = '' )

						informar += "\nAmbiente 1-Produção, 2-Homologação "+str( rTo.decode('iso-8859-7').encode('utf8') )
						if "ERRO:" in rTo:	error = True

		#---------: Token e Numero CSC Numero
					if r[12] == "T":

						_menssag = mens.showmsg( "{ Configurando Ambiente-Plus }\nCSC-Numero"+parent.TM )
						cmd1 = "NFE.SetCSC("+nfceiccsc+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
						self.s.send(cmd1)
						rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False  )
						rTNFCe = rTn.acbrAbrirRetornos( parent, op = 1, rT = rTo, nF = '' )

						informar += "\nCSC-Numero "+str( rTo.decode('iso-8859-7').encode('utf8') )
						if "ERRO:" in rTo:	error = True

		#-------------: Token e Numero CSC-ID
						_menssag = mens.showmsg( "{ Configurando Ambiente-Plus }\nCSC-ID"+parent.TM )
						cmd1 = "NFE.SetIdCSC("+nfceidcsc+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
						self.s.send(cmd1)
						rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False  )
						rTNFCe = rTn.acbrAbrirRetornos( parent, op = 1, rT = rTo, nF = '' )

						informar += "\nCSC-ID "+str( rTo.decode('iso-8859-7').encode('utf8') )
						if "ERRO:" in rTo:	error = True

		except Exception as rTry:
		
			err = True
			de = str( datetime.datetime.now().strftime("%d-%m-%Y %T") )+" "+login.usalogin
			open(nfclogs,"a").write(de+" CONFIGURA NFCE\n"+str( rTry )+"\n")
				
		del _menssag
		rTorna = False
		
		con.acbrFechar( cnf = self.s )

		if err == True:	
			
			parent.ecfof.SetLabel('Ambiente Plus-Erro, Configuração do Ambiente')
			parent.ecfof.SetForegroundColour('#D31818')
			alertas.dia(parent,"1-Retorno do Erro\n\n"+str( rTry )+"\n"+(" "*140),"Configuração do Ambiente")
			
		if err != True and error == True:	
			
			parent.ecfof.SetLabel('Ambiente Plus-Erro, Configuração do Ambiente')
			parent.ecfof.SetForegroundColour('#D31818')
			alertas.dia(parent,"2-Retorno do Erro\n\n"+str( informar )+"\n"+(" "*140),"Configuração do Ambiente")

		if err != True and error == False:
			
			parent.ecfof.SetLabel('Ambiente Plus-Configurado')
			parent.ecfof.SetForegroundColour('#2284A5')
			rTorna = True

		if not cerwin:

			alertas.dia(parent,"Certificado não localizado no lado da estação windows\n"+(" "*140),"Configuração do Ambiente")
			rTorna = False
			
		return rTorna

	def acbrRePrinTer(self,parent, Filial,lsT):
		

		self.p = parent
		rTn = acbRetornos()
		dTa = lsT[0].split(" ")[0].split("-")
		inf = ""
		
		d = login.filialLT[ Filial ][30].split(";")
		r = login.filialLT[ Filial ][38].split("|")[0].split(";")

		"""   Auditoria de Emissao   """
		if len( r ) >=13:	audiToria = r[13]
		else:	audiToria = "F"

		"""   Cria o diretorio da NFCe   """
		pasTa,Tmpas, pCan = rTn.acbrCriaPasTa( Filial, True, str( lsT[0] ) )
		arqLoca = pasTa+str( lsT[1] )+'-nfe.xml'
		exisTen = os.path.exists(arqLoca)
		
		"""   Verifica na pasta de Emissao da NFCe, se Existir verifica na pasta de emissao do pela data do DAV   """
		if exisTen !=True:

			pasTa,Tmpas, pCan = rTn.acbrCriaPasTa( Filial, True, str( lsT[2] ) )

		AnoMes  = dTa[0]+dTa[1]
		psTaXML = "c:\\ACBrMonitorPlus\\Logs\\"+str( lsT[1] )+'-nfe.xml'
		arqLoca = pasTa+str( lsT[1] )+'-nfe.xml'
		exisTen = os.path.exists( arqLoca )

		"""  Conexao com acbr  """
		con = acbrTCP()

		cn = con.acbrAbrir( cnT=1, par = parent, TipoNF = 1, fls = Filial )
		if cn[0] == False:	return
		self.sn = cn[1]

		if exisTen != True:
			

			dS = "{ XML Não locaziado }\n"+\
				 "\nNumero Chave: "+lsT[1]+\
                 "\nNF Emissão..: "+lsT[0]+\
                 "\nDAV Emissão.: "+lsT[2]+\
                 "\n\nPasta Local.: "+arqLoca
			
			self.p.reTsD.SetValue( dS )
			
		if exisTen == True:

			"""
				Faz a leitura do xml p/enviar para a estacao windows
			"""
			cArq = open(arqLoca).read()
			xArq ='"'+cArq+'"'
			
			"""	Faz o Envio do XML p/a estacao windows p/pasta c:\ACBrMonitorPlus\Logs """
			cmd1 = "NFE.SaveToFile("+psTaXML+","+xArq+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
			self.sn.send(cmd1)
			rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.sn, nF = '', aINI = '', chave = '', recupera = False, rCancela = False  )
			inf += "1-Verificando a existencia do XML\n"+str( rTo.decode('iso-8859-7').encode('utf8') )
									
			"""	Verifica a existencia do XML na pasta c:\ACBrMonitorPlus\Logs """	
			cmd1 = "NFE.FileExists("+str( psTaXML )+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
			self.sn.send(cmd1)
			rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.sn, nF = '', aINI = '', chave = '', recupera = False, rCancela = False  )
			inf += "1-Verificando a existencia do XML\n"+str( rTo.decode('iso-8859-7').encode('utf8') )

			self.p.reTsD.SetValue( inf )

			if "OK:" in rTo.upper():

				rlsT  = psTaXML, lsT[1], self.sn
				self.acbrNFCeReimpressao( self.p, Filial, rlsT, 1 )
				
		con.acbrFechar( cnf = self.sn )
		
	def acbrNFCeReimpressao(self, parent, filial, lisTa, op ):
		
		rTn = acbRetornos()

		self.s  = lisTa[2]
		informe = parent.reTsD.GetValue()
		
		if op == 1:	psTaXML = lisTa[0]
		else:
			
			daTaEmi = lisTa[0].split(" ")[0].split("-")
			AnoMes  = str( daTaEmi[0] )+str( daTaEmi[1] )
			psTaXML = "c:\\ACBrMonitorPlus\\Logs\\"+str( lisTa[1] )+'-nfe.xml'
		
		_menssag = mens.showmsg( "{ Impressão da NFCe }\nChave: "+str( lisTa[1] )+"\n"+parent.TM )
		
		"""	Impressao em modo de contigencia """
		if self.p.cnTgn.GetValue() == True:
			
			cmd2 = "NFE.ImprimirDanfe("+psTaXML+",,1,,,,1,)"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
			cmd1 = "NFE.ImprimirDanfe("+psTaXML+",,1,,,,0,)"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)

			_menssag = mens.showmsg( "{ Impressão em Contigência { Via Consumidor }\nChave: "+str( lisTa[1] )+"\n"+parent.TM )

			self.s.send(cmd2)
			_menssag = mens.showmsg( "{ Impressão em Contigência { Via Estabelecimento }\nChave: "+str( lisTa[1] )+"\n"+parent.TM )

		else:

			""" Impressao em modo normal """
			_menssag = mens.showmsg("{ Impressão em Modo Normal { Via Consumidor }\nChave: "+str( lisTa[1] )+"\n"+parent.TM )
			cmd1 = "NFE.ImprimirDanfe("+psTaXML+",,,1,,,,1,)"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
		
		self.s.send(cmd1)
		rTo, End, qrc, chv = rTn.acbrLimpa( op=1, s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False  )
		rTNFCe = rTn.acbrAbrirRetornos( parent, op = 1, rT = rTo, nF = '' )
		
		informe +='\n\n'+str( unicodedata.normalize('NFKD', rTo.decode('CP1252')).encode('UTF-8', 'ignore') )

		if op == 1:	parent.reTsD.SetForegroundColour("#EDED93")
		if "ERRO:" in rTo:	parent.reTsD.SetForegroundColour("#FF5858")
		
		parent.reTsD.SetValue( str( informe ) )

		del _menssag
		
	def acbrNFCeConsulta(self, parent, Filial, lsT , mensa, chaveATual, rtn105 = False, localizado = False ):
		
		self.p = parent
		rTn = acbRetornos()
		dTa = lsT[0].split(" ")[0].split("/")
		dTa = dTa[2]+'-'+dTa[1]+"-"+dTa[0]
		inf = ""
		chA = lsT[1]

		if chaveATual !="":	chA = str( chaveATual.strip() )
		
		d = login.filialLT[ Filial ][30].split(";")
		r = login.filialLT[ Filial ][38].split("|")[0].split(";")

		"""   Auditoria de Emissao   """
		if len( r ) >=13:	audiToria = r[13]
		else:	audiToria = "F"

		"""   Cria o diretorio da NFCe   """
		pasTa,Tmpas, pCan = rTn.acbrCriaPasTa( Filial, True, str( dTa ) )
		inNF = lsT[2], "65", lsT[3], Tmpas, pasTa

		AnoMes  = dTa[0]+dTa[1]
		psTaXML = "c:\\ACBrMonitorPlus\\Logs\\"+str( chA )+'-nfe.xml'
		psTcXML = "c:\\ACBrMonitorPlus\\Logs\\"+str( chA )+'-sit-soap.xml'
		psTaCan = pCan+str( chA )+"-can.xml"
		
		"""  Recuperacao do XML de Cancelamento  """
		cancelamenTo = False
		
		"""
			Verifica a existencia na pasta local
			
			Se o xml for 204 o nome do arquivo nao muda
			Mais se o xml for 539 muda o numero da chave
			por isso q mantenho a chave antiga para pegar o arquivo anterior e depois grava no window com a chave nova
		"""
		
		arqLoca = pasTa+str( chA )+'-nfe.xml'
		exisTen = os.path.exists( arqLoca )

		reTGrva, grava = False,['',"Motivo vazio/Não localizado..."]
		
		if exisTen == True:
			
			"""  Conexao com acbr  """
			con = acbrTCP()

			cn = con.acbrAbrir( cnT=1, par = parent, TipoNF = 1, fls = Filial )
			if cn[0] == False:	return
			self.sn = cn[1]

			doc = login.filialLT[ Filial ][9].decode('UTF-8')

			""" Faz a leitura do xml p/enviar para a estacao windows """
			cArq = open(arqLoca).read()
			xArq ='"'+cArq+'"'
			
			""" Faz o Envio do XML p/a estacao windows p/pasta c:\ACBrMonitorPlus\Logs """
			_menssag = mens.showmsg( "{ Salvando XML na estacao [ Recuperção do XML ] }\n\nChave: "+str( chA )+"\n\n"+str( mensa )+"\n\nAguarde..." )

			"""	Faz a leitura do xml p/enviar para a estacao windows """
			cArq = open(arqLoca).read()
			xArq ='"'+cArq+'"'

			cmd1 = "NFE.SaveToFile("+psTaXML+","+xArq+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
			self.sn.send(cmd1)
			rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.sn, nF = '', aINI = '', chave = '', recupera = False, rCancela = False )
			inf += "1-Verificando a existencia do XML\n"+str( rTo.decode('iso-8859-7').encode('utf8') )
									
			""" Verifica a existencia do XML na pasta c:\ACBrMonitorPlus\Logs """	
			_menssag = mens.showmsg( "{ Verificando a existencia do XML na estacao [ Recuperção do XML ] }\nChave: "+str( chA )+"\n"+str( mensa ) )
			cmd1 = "NFE.FileExists("+str( psTaXML )+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
			self.sn.send(cmd1)
			rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.sn, nF = '', aINI = '', chave = '', recupera = False, rCancela = False )

			if "OK:" in rTo.upper():
				
				_menssag = mens.showmsg( "{ Consultando NFCe [ Recuperção do XML ] }\n\nChave: "+str( chA )+"\n"+str( mensa )+"\n\nAguarde..." )
				cmd1 = "NFE.ConsultarNFe("'"'+str( chA )+'"'")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
				
				self.sn.send(cmd1)
				rTo, End, qrc, chv = rTn.acbrLimpa( op=1, s=self.sn, nF = '', aINI = '', chave = '', recupera = False, rCancela = False )
				
				sT,nP = False,False
				if rTo[:3] != "OK:":	 reTGrva, grava = False,['',"Sem retorno do SEFAZ"]
				if rTo[:5] == "ERRO:":	 reTGrva, grava = False,['',rTo]
			
				if rTo[:3] == "OK:":
					
					ET = datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin
					
					hAnT = ""
					if lsT[5] !="":	hAnT = "\n"+str( lsT[5] )
					
					hisTorico = "Recuperacao de XML { "+str(ET)+" }\n"+str( rTo )+hAnT
					
					csTat = proTo = dTre = moTivo = ndanfe = csTaTs = rTsTaT = ""
					reTon = ["100","101","105","135","150","110","301","302"]

					for i in rTo.split("\n"):

						if i.strip() !="" and i.upper()[:5] == "CSTAT"		and i.split("=")[1].split("\r")[0] in reTon:	sT,csTat = True, i.split("=")[1].split("\r")[0]
						if i.strip() !="" and i.upper()[:5] == "NPROT"		and i.split("=")[1].split("\r")[0] != "":	nP,proTo = True, i.split("=")[1].split("\r")[0]

						if i.strip() !="" and i.upper()[:5] == "CSTAT"		and i.split("=")[1].split("\r")[0] != "":	csTaTs = i.split("=")[1].split("\r")[0]
						if i.strip() !="" and i.upper()[:7] == "XMOTIVO"	and i.split("=")[1].split("\r")[0] != "":	moTivo = i.split("=")[1].split("\r")[0]
						if i.strip() !="" and i.upper()[:5] == "CHNFE"		and i.split("=")[1].split("\r")[0] != "":	ndanfe = i.split("=")[1].split("\r")[0]

					if csTat  !="":	rTsTaT +="csTaT-Consulta: "+str( csTat )+"\n"
					if proTo  !="":	rTsTaT +="Protocolo: "+str( proTo )+"\n"
					if csTaTs !="":	rTsTaT +="csTaT Retorno: "+str( csTaTs )+"\n"
					if moTivo !="":	rTsTaT +="Motivo: "+str( moTivo )+"\n"
					if ndanfe !="":	rTsTaT +="Numero Danfe: "+str( ndanfe )+"\n"

					if sT and nP:

						"""  Recupercao do Protocolo de Cancelamento   """
						if csTat == "135" or csTat == "101":	psTaXML = psTcXML


						cmd1 = "NFE.FileExists("+str( psTaXML )+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
						self.sn.send(cmd1)
						rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.sn, nF = '', aINI = '', chave = '', recupera = False, rCancela = False  )

						if rTo[:3] != "OK:":	 reTGrva, grava = False,['',"Sem retorno do SEFAZ"]
						if rTo[:5] == "ERRO:":	 reTGrva, grava = False,['',str( rTsTaT.decode('iso-8859-7').encode('utf8') )+"\n"+str( rTo.decode('iso-8859-7').encode('utf8') )]

						if "OK:" in rTo.upper():

							"""   Recuperacao do Protocolo de cancelamento   """
							__op = 4
							if csTat == "135" or csTat == "101":	__op, cancelamenTo = 7,True
							
							cmd1 = "NFE.LoadfromFile("+str( psTaXML )+",15)"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
							self.sn.send(cmd1)

							rTo, End, qrc, chv = rTn.acbrLimpa( op = __op, s=self.sn, nF = inNF, aINI = '', chave = str( chA ), recupera = True, rCancela = cancelamenTo  )
							if rTo[:3] != "OK:":	 reTGrva, grava = False,['',"Sem retorno do SEFAZ"]
							if rTo[:5] == "ERRO:":	 reTGrva, grava = False,['',str( rTsTaT.decode('iso-8859-7').encode('utf8') )+"\n"+str( rTo.decode('iso-8859-7').encode('utf8') )]

							"""  Resgata o QR-Code  do XML  """
							if rTo[:3] != "ERRO:": # and csTat !="135":

								if cancelamenTo == True:

									proTCan = rTn.acbrCanInuRetorno(1, self.p, rTo, Filial, chA, rCancela = True, pasCan = psTaCan )
									lsT = chA,proTCan,psTaCan

									grava = con.acbrGravarNF( self.p, lsT, passo=6, TNF = 2, ORI = 1, his = hisTorico, conTigencia = False, csTaTr = csTat, rsConTigencia = "", vNF = '' )
									reTGrva = grava[0]
									
								else:	

									docume = minidom.parseString(rTo)
									qrCode,sT = nfe31RT.AbrirXML(docume,"infNFeSupl","qrCode")
									sT,nChave = nfe31RT.AbrirXML(docume,"infNFe","Id")

									amb,aT4 = nfe31RT.AbrirXML(docume,"infProt","tpAmb") #-------: Nº da DANFE
									dan,aT5 = nfe31RT.AbrirXML(docume,"infProt","chNFe") #-------: Nº da DANFE
									dTr,aT6 = nfe31RT.AbrirXML(docume,"infProt","dhRecbto") #----: Data de Recebimento
									Pro,aT7 = nfe31RT.AbrirXML(docume,"infProt","nProt") #-------: Numero do Protocolo
									cst,aT8 = nfe31RT.AbrirXML(docume,"infProt","cStat") #-------: CST de Retorno 
									mot,aT9 = nfe31RT.AbrirXML(docume,"infProt","xMotivo") #-----: Motivo

									ser,aT10 = nfe31RT.AbrirXML(docume,"ide","serie") #-----: Motivo
									nnf,aT10 = nfe31RT.AbrirXML(docume,"ide","nNF") #-----: Motivo
									
									dTr = format(datetime.datetime.strptime(dTr[0].split("T")[0], "%Y-%m-%d"),"%d/%m/%Y")+" "+str( dTr[0].split("T")[1] )

									if cst[0] in reTon and Pro[0] !="":
										
										"""
											** Grava Retorno de Nota **
											Dav,NF,Chave,Protocolo,DTEmissao
										"""

										"""   A recuperacao do XML via download de sistemas de recuperacao da internet nao vem com o qrcode    """
										if qrCode == "" or qrCode == []:	qrCode = [""]
										
										lsTax = lsT[4],nnf[0],dan[0],Pro[0],dTr,pasTa,qrCode[0],ser[0]
										if rtn105 and lsT[6] == "539" and cst[0] == "100" and dan[0] != lsT[1]:	lsTax = lsT[4],nnf[0],lsT[1],Pro[0],dTr,pasTa,qrCode[0],ser[0]

										grava = con.acbrGravarNF( self.p, lsTax, passo=2, TNF = 2, ORI = 1, his = hisTorico, conTigencia = False, csTaTr = cst[0], rsConTigencia = "", vNF = '' )
							
										"""  Atuliza ou Inclui o XML  """
										if grava[0] == True:

											grava = con.acbrGravarNF( self.p, lsTax, passo=4, TNF = 2, ORI = 1, his = hisTorico, conTigencia = False, csTaTr = cst[0], rsConTigencia = "", vNF = '' )

										reTGrva = grava[0]
		
									else:	reTGrva, grava = False,['',"Sem retorno de protocolo\n\nDANFE: "+str( dan[0] )+"\nCST: "+str( dan[0] )+"\nMotivo: "+str( mot )+"\n\nVoçe pode fazer o download do xml na sefaz e copiar para a pasta local\n"]

					else:	reTGrva, grava = False,['',"Sem retorno de protocolo\n\nDANFE: "+str( ndanfe )+"\nCST: "+str( csTaTs )+"\nMotivo: "+str( moTivo )]

			del _menssag
			con.acbrFechar( cnf = self.sn )

		if rtn105 and reTGrva:

			"""  Se a recupercao vier de uma contigencia q o sefaz ja processou vai dar erro pq o dav ja estava recebido  """
			try:
				self.p.p.fechamento("229",'nfce', filial = Filial )
			except Exception as retorno_excessa:	pass
				
			alertas.dia(self.p,"{ Recuperação do XML com csTat 105/204/539 NFCe em processamento }\n\n [ XML recuperado com sucesso ]\nChave: "+str( chA )+"\n"+(" "*140),"Recuperacao de XML")
				
		else:
			
			if reTGrva == True and cancelamenTo == False:	alertas.dia(self.p,"XML de NFCe ACBr-Plus recuperado com sucesso...\n"+(" "*130),"Recuperacao de XML")
			if reTGrva == True and cancelamenTo == True:	alertas.dia(self.p,"XML de NFCe ACBr-Plus { csTat 135, Cancelameno }, recuperado com sucesso...\n"+(" "*130),"Recuperacao de XML")
			if reTGrva == False:	alertas.dia(self.p,"{ Erro na recuperacao do XML-NFCe ACBr-Plus }\n\n"+str( grava[1] )+"\n"+(" "*170),"Recuperacao de XML")

		return reTGrva
		
	def acbrNFCeCancelamento(self, parent, lisTa, mensa ):

		"""   lisTa-> NºChave, Motivo   """
		rTn = acbRetornos()
		con = acbrTCP()

		cn = con.acbrAbrir( cnT=1, par = parent, TipoNF = 1, fls = lisTa[2] )
		if cn[0] == False:	return False, ""
		
		self.s = cn[1]
		falha  = False
		
		_menssag = mens.showmsg( "{ Cancelamento de NFCe }\nChave: "+str( lisTa[0] )+"\n"+str( mensa ) )
		cmd1 = "NFE.CancelarNFe("+lisTa[0]+","+str( lisTa[1] ).replace(',','')+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
		self.s.send( cmd1 )
		rTo, End, qrc, chv = rTn.acbrLimpa( op=5, s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False )

		if "ERRO:" not in rTo:	rTNFCe = rTn. acbrCanInuRetorno( 1, parent, rTo, lisTa[2], lisTa[0], rCancela = False, pasCan = "" )
		if "ERRO:" in rTo:	falha, rTNFCe = True, rTo
		
		con.acbrFechar( cnf = self.s )
		del _menssag
		
		return falha,rTNFCe
		
	def acbrNFCeInutulizacao(self, parent, lisTa, mensa ):
		
		"""   lisTa-> NºChave, Motivo   """
		rTn = acbRetornos()
		con = acbrTCP()

		cn = con.acbrAbrir( cnT=1, par = parent, TipoNF = 1, fls = lisTa[7] )
		if cn[0] == False:	return False,''
		
		self.s = cn[1]
		falha  = False
		
		_menssag = mens.showmsg( "{ Inutilização de NFCe }\nCNPJ: "+str( lisTa[0] )+"\n"+str( mensa ) )
		cmd1 = "NFE.InutilizarNFe("+str(lisTa[0])+","+str(lisTa[1]).replace(',','')+","+str(lisTa[2])+","+str(lisTa[3])+","+str(lisTa[4])+","+str(lisTa[5])+","+str(lisTa[5])+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
		self.s.send(cmd1)
		rTo, End, qrc, chv = rTn.acbrLimpa( op=1, s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False )
	
		if "ERRO:" not in rTo:	rTNFCe = rTn. acbrCanInuRetorno( 2, parent, rTo, lisTa[2], lisTa[0], rCancela = False, pasCan = "" )
		if "ERRO:" in rTo:	falha, rTNFCe = True, rTo
		
		con.acbrFechar( cnf = self.s )
		del _menssag
		
		return falha,rTNFCe
				
	def acbrNFCeEmissao(self,parent):

		"""
			100|Autorizado o uso da NF-e
			103|Lote recebido com sucesso
			104|Lote processado
			105|Lote em processamento
			110|Uso Denegado
			301|Uso Denegado: Irregularidade fiscal do emitente
			303|Uso Denegado: Destinatário não habilitado a operar na UF
			128|Lote de Evento Processado
			135|Evento registrado e vinculado a NF-e
			136|Evento registrado, mas não vinculado a NF-e
			150|Autorizado o uso da NF-e, autorização fora de prazo
			
			107|Serviço em Operação

			erro de conexao sem internet contigencia off-line

			Contigencias on-line
			108|Serviço Paralisado Momentaneamente (curto prazo) ->Contigencia
			109|Serviço Paralisado sem Previsão -> Contigencia
		"""

		self.p = parent
		self.f = parent.p

		rTn = acbRetornos()
		
		d = self.p.dcia if self.p.dcia else login.filialLT[ self.p.Filial ][30].split(";")
		r = self.p.acbr if self.p.acbr else login.filialLT[ self.p.Filial ][38].split("|")[0].split(";")

		"""   Auditoria de Emissao   """
		if len( r ) >=13:	audiToria = r[13]
		else:	audiToria = "F"

		"""   Cria o diretorio da NFCe   """
		if parent.emis.GetValue():	__data, __avanca = parent.emis.GetValue(), True
		else:	__data, __avanca = '', False
		pasTa,Tmpas, pCan = rTn.acbrCriaPasTa( self.p.Filial, __avanca, __data )

		m = nfe31c()
		
		carquivo = diretorios.esCerti+d[6]
		csenha   = d[5]
		nDavs    = str( self.p.nuDavs ) #----: Numero do DAV
		nSerie   = str( r[5] ) #-------------: Numero da Serie
		
		"""  Conexao com acbr  """
		con = acbrTCP()

		cn = con.acbrAbrir( cnT=1, par = parent, TipoNF = 1, fls = self.p.Filial )
		if cn[0] == False:	return
		
		self.s = cn[1]

		numerar = numeracao()
		rT, nfis, lsT = numerar.verificaNFCe( nDav=nDavs, nFil=self.p.Filial, nSer=nSerie )
		
		if rT == False:	nfis = numerar.numero("15","Numero da NFCe",self.p,self.p.Filial)

		if nfis == '':
						
			alertas.dia(self.p,"Numero de NFCe não foi gerado, Tente novamente!!\n"+(" "*110),"Emissão de NFes")
			return

		envioNFCe = ""
		dEmi= datetime.datetime.now().strftime("%d/%m/%Y %T")
		dhC = ""
		juC = ""

		"""   Dados do Destinatario   """
		_cod = _doc = _nom = _fan = _lgr = _nro = _bai = _cmu = _mun = _ufd = _cep = ""
		if self.p.consu.GetValue():	_nom = "Consumidor"
		else:
			
			_cod = str( self.p.d[3].strip()  )
			_doc = str( self.p.d[39].strip() )
			_fan = str( self.p.d[5].strip()  )
			_nom = str( self.p.d[4].strip()  )

			if self.p.c !="":

				if self.p.c[14].strip() !='':	comp = " "+str( self.p.c[14].strip() )
				else:	comp = ""
					

				_fan = str( self.p.c[2].strip() )
				_nom = str( self.p.c[1].strip() )
				_doc = str( self.p.c[3].strip() )

				_lgr = str( self.p.c[8].strip() )
				_bai = str( self.p.c[9].strip() )
				_mun = str( self.p.c[10].strip() )
				_ufd = str( self.p.c[15].strip() )
				_nro = str( self.p.c[13].strip() )+comp
				_cod = str( self.p.c[46].strip() )

				_cmu = str( self.p.c[11].strip() )
				_cep = str( self.p.c[12].strip() )

			logradouro, __rl = self.p.vallogradouro( self.p.c )
			if logradouro == False:	_lgr = _nro = _bai = _cmu = _mun = _ufd = _cep = ""


#-----: Grava passo_1
		lsT = nfis,nSerie,nDavs,_cod,_doc,_fan,_nom
		con.acbrGravarNF( parent, lsT, passo=1, TNF = 2, TEM = 1, TLA = 2, ORI = 1, conTigencia = False, csTaTr = "", rsConTigencia = "", vNF = str( self.p.d[37] ).replace(",","") )

		"""   Configura o tipo de emissao - Normal,Contigencia  """
		TpEmissao = 1
		if self.p.cnTgn.GetValue() == True:	TpEmissao = 9
	
		_menssag = mens.showmsg( "{ Configurando Tipo de Emissão da NFCe"+parent.TM )
		if self.p.cnTgn.GetValue() == True:
			
			cmd1 = "NFE.SetFormaEmissao(9)"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
			dhC  = dEmi
			juC  = "Sem conexao para emissão on-line da nfce "
			
		else:	cmd1 = "NFE.SetFormaEmissao(1)"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
		
		self.s.send(cmd1)
		rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False )
		rTNFCe = rTn.acbrAbrirRetornos( parent, op = 1, rT = rTo, nF = '' )

		"""    Informacoes do Adicionais da NFCe do Estado     """
		nota_rodape = login.rdpnfes
		if nota_rodape:

			if "<"+self.p.Filial.upper()+">" in nota_rodape.upper() and "</"+self.p.Filial.upper()+">" in nota_rodape.upper():	nota_rodape = nota_rodape.split( "<"+self.p.Filial.upper()+">" )[1].split( "</"+self.p.Filial.upper()+">" )[0]

		infoAdicionais = nota_rodape.replace("\n"," ") if nota_rodape else ''
		#infoAdicionais = login.rdpnfes.replace("\n"," ") if login.rdpnfes !=None and login.rdpnfes !='' else ''
		#print infoAdicionais
		
		envioNFCe +="[infNFe]\n"
		envioNFCe +="versao="+str( d[2] )+"\n"
		envioNFCe +="[Identificacao]\n"
		envioNFCe +="cNF="+m.NFecNF(str(nfis)).zfill(8)+"\n" #-: Codigo Numerico que compoe a chave
		envioNFCe +="natOp=VENDA\n" #--------------------------: Natureza da operacao
		envioNFCe +="indPag=0\n" #-----------------------------: Forma de Pagamentos 0 - pagamento à vista, 1 - pagamento à prazo, 2 - outros.
		envioNFCe +="mod=65\n" #-------------------------------: Informar o código do Modelo do Documento Fiscal, código 55 para a NF-e ou código 65 para NFC-
		envioNFCe +="serie="+nSerie+"\n" #---------------------: Numero de Serie da NFCe do Usuario
		envioNFCe +="nNF="+str( nfis ).zfill(9)+"\n" #---------: Numero da Nota Fiscal
		envioNFCe +="dhEmi="+str(dEmi)+"\n" #------------------: Data e Hora de Emissao
		# Parece q Precisa envioNFCe +="dhSaiEnt=
		envioNFCe +="tpNF=1\n" #-------------------------------: 0-entrada, 1-saída.
		envioNFCe +="idDest=1\n" #-----------------------------: 1-Operação interna, 2-Operação interestadual, 3-Operação com exterior
		envioNFCe +="tpImp=4\n" #------------------------------: 0-Sem geração de DANFE, 1-DANFE normal, Retrato, 2-DANFE normal, Paisagem, 3-DANFE Simplificadom, 4-DANFE NFC-e, 5-DANFE NFC-e em mensagem eletrônica
		envioNFCe +="tpEmis="+str( TpEmissao )+"\n" #---------: 1-Emissão normal (não em contingência), 5-Contingência FS-DA, com impressão do DANFE em formulário de segurança, 9-Contingência off-line da NFC-e (as demais opções de contingência são válidas também para a NFC-e)
		envioNFCe +="finNFe=1\n" #-----------------------------: 1-NF-e normal, 2-NF-e complementar, 3-NF-e de ajuste, 4-Devolução
		envioNFCe +="indFinal=1\n" #---------------------------: 0-Não, 1-Consumidor final
		envioNFCe +="indPres=1\n" #----------------------------: 0-Não se aplica (por exemplo, Nota Fiscal complementar ou de ajuste), 1-Operação presencial, 2-Operação não presencial, pela Internet, 3-Operação não presencial, Teleatendimento, 4-NFC-e em operação com entrega a domicílio, 9-Operação não presencial, outros
		envioNFCe +="procEmi=0\n" #----------------------------: 0-emissão de NF-e com aplicativo do contribuinte, 1-emissão de NF-e avulsa pelo Fisco, 2-emissão de NF-e avulsa, pelo contribuinte com seu certificado digital, através do site do Fisco, 3-emissão NF-e pelo contribuinte com aplicativo fornecido pelo Fisco
		envioNFCe +="verProc="+str( d[8] )+"\n" #--------------: informar a versão do processo de emissão da NF-e utilizada (aplicativo emissor de NF-e)
		envioNFCe +="dhCont="+str( dhC )+"\n" #----------------: informar a data e hora de entrada em contingência no padrão UTC - Universal Coordinated Time, onde TZD pode ser -02:00 (Fernando de Noronha), -03:00 (Brasília) ou -04:00(Manaus), no horário de verão serão - 01:00, -02:00 e -03:00. Ex.: 2010-08-19T13:00:15-03:00.
		envioNFCe +="xJust="+str( juC )+"\n" #-----------------: informar a justificativa de entrada em contingência, deve ser informado sempre que tpEmis for diferente de 1 Importante: dhCont e xJust devem ser ambos informados ou omitidos.

		eTelfones = login.filialLT[ self.p.Filial ][10].split('|')[0].replace(' ','').replace('-','').replace('(','').replace(')','').replace('.','')
		
		envioNFCe +="[Emitente]\n"
		envioNFCe +="CNPJCPF="+str( login.filialLT[ self.p.Filial ][9] )+"\n"
		envioNFCe +="xNome="+str( login.filialLT[ self.p.Filial ][1].decode('UTF-8') )+"\n"
		envioNFCe +="xFant="+str( login.filialLT[ self.p.Filial ][14].decode('UTF-8') )+"\n"
		envioNFCe +="IE="+str( login.filialLT[ self.p.Filial ][11].decode('UTF-8').decode('UTF-8') )+"\n"
		envioNFCe +="CRT="+str( d[11] )+"\n"
		envioNFCe +="xLgr="+str( login.filialLT[ self.p.Filial ][2].decode('UTF-8') )+"\n"
		envioNFCe +="nro="+str( login.filialLT[ self.p.Filial ][7].decode('UTF-8') )+"\n"
		envioNFCe +="xCpl="+str( login.filialLT[ self.p.Filial ][8].decode('UTF-8') )+"\n"
		envioNFCe +="xBairro="+str( login.filialLT[ self.p.Filial ][3].decode('UTF-8') )+"\n"
		envioNFCe +="cMun="+str( login.filialLT[ self.p.Filial ][13].decode('UTF-8') )+"\n"
		envioNFCe +="xMun="+str( login.filialLT[ self.p.Filial ][4].decode('UTF-8') )+"\n"
		envioNFCe +="UF="+str( login.filialLT[ self.p.Filial ][6].decode('UTF-8') )+"\n"
		envioNFCe +="CEP="+str( login.filialLT[ self.p.Filial ][5].decode('UTF-8') )+"\n"
		envioNFCe +="cPais=1058\n"
		envioNFCe +="xPais=BRASIL\n"
		envioNFCe +="Fone="+str( eTelfones )+"\n"
		envioNFCe +="cUF="+str( login.filialLT[ self.p.Filial ][13].decode('UTF-8') )[:2]+"\n" #-: informar o código da UF do emitente do Documento Fiscal, utilizar a codificação do IBGE (Ex. SP->35, RS->43, etc.)
		envioNFCe +="cMunFG="+str( login.filialLT[ self.p.Filial ][13].decode('UTF-8') )+"\n" #--: informar o código do Município de Ocorrência do Fato Gerador do ICMS, que é o local onde ocorre a entrada ou saída da mercadoria, utilizar a Tabela do IBG

		envioNFCe +="[Destinatario]\n"
		envioNFCe +="idEstrangeiro=\n"
		envioNFCe +="CNPJCPF="+str( _doc )+"\n"
		envioNFCe +="xNome="+str( _nom )+"\n"
		envioNFCe +="indIEDest=9\n" #------------: Indicador da IE do Destinatário, Nota 1: No caso de NFC-e informar indIEDest=9 e não informar a tag IE do destinatário;
		envioNFCe +="xLgr="+str( _lgr )+"\n"
		envioNFCe +="nro="+str( _nro )+"\n"
		envioNFCe +="xBairro="+str( _bai )+"\n"
		envioNFCe +="cMun="+str( _cmu )+"\n"
		envioNFCe +="xMun="+str( _mun )+"\n"
		envioNFCe +="UF="+str( _ufd )+"\n"
		envioNFCe +="CEP="+str( _cep )+"\n"
		
		"""   Abertura do Banco   """
		conn = sqldb()
		sql  = conn.dbc("Caixa: Consulta de Items do DAVs", fil =  self.p.Filial, janela = self.p )
		vTT  = Decimal('0.00')
		if sql[0] == True:
			
			iTems = 1
			for i in self.p.i:

				ncm = str( i[56] )
				cfo = str( i[57] )
				csT = str( i[58] )
				ces = ""
				csTPIS = "06"
				csTCOF = "06"

				"""  Troca os codigos fiscais  se for regime normal, passa a utilizar o codigo fiscal da nfce no cadastro de produtos   """
				if sql[2].execute("SELECT pd_cfir,pd_cest,pd_para FROM produtos WHERE pd_codi='"+str( i[5] )+"'") !=0:

					cfs = sql[2].fetchall()
					cfi = cfs[0][0]
					ces = cfs[0][1]

					if cfi !="" and len( cfi.split(".") ) >= 2:

						ncm = str( cfi.split(".")[0].strip() ) #-: NCM
						cfo = str( cfi.split(".")[1].strip() ) #-: CFOP
						csT = str( cfi.split(".")[2].strip() ) #-: CST

					"""  PIS-COFINS  """
					if cfs[0][2] !=None and cfs[0][2] !="":

						T = TTabelas.parameTrosProduTos( cfs[0][2] )[0]
						csTPIS = T[0] #-: CST-PIS
						csTCOF = T[2] #-: CST-COFINS

				
				"""   Tributos Federais e Estauais   """
				vTribuTos = ""
				if i[94] !=None and i[94] !="":
					
					vTribF = Decimal( i[94].split("|")[0] ) #-: Tributos Federais
					vTribE = Decimal( i[94].split("|")[2] ) #-: Tributos Estaduais
					vTribM = Decimal( i[94].split("|")[3] ) #-: Tributos Municipal
					vTribuTos = ( vTribF + vTribE + vTribM )
					
					"""  Totaliza Impostos Aproximandos  """
					vTT +=vTribuTos

				ciTF = ""
				if i[95] !=None and i[95] and len( i[95].split("|")[0] ) >=1:	ciTF +=" CI:"+i[95].split("|")[0]	

				xProduTo = i[7].replace(',','.').replace('"'," ").replace("'"," ")
				envioNFCe +="[Produto"+str( iTems ).zfill(3)+"]\n"
				envioNFCe +="cProd="+str( i[5] ).replace(",","")+"\n"
				envioNFCe +="cEAN="+str( i[6] )+"\n"
				envioNFCe +="xProd="+str( xProduTo.strip()+str(ciTF) )+"\n"
				envioNFCe +="NCM="+ncm+"\n"
				envioNFCe +="CEST="+ces+"\n"
				envioNFCe +="CFOP="+cfo+"\n"
				envioNFCe +="uCom="+str( i[8] )+"\n"
				envioNFCe +="qCom="+str( i[12] )+"\n"
				envioNFCe +="vUnCom="+str( i[11] )+"\n"
				envioNFCe +="vProd="+str( i[13] )+"\n"
				envioNFCe +="uTrib="+str( i[8] )+"\n"
				envioNFCe +="qTrib="+str( i[12] )+"\n"
				envioNFCe +="vUnTrib="+str( i[11] )+"\n"
				envioNFCe +="vFrete=\n"
				envioNFCe +="vSeg=\n"
				envioNFCe +="vDesc="+str( i[28] )+"\n"
				envioNFCe +="vOutro="+str( i[27] )+"\n"
				envioNFCe +="indTot=1\n" #------------------: 0-o valor do item (vProd) não compõe o valor total da NF-e (vProd) 1-o valor do item (vProd) compõe o valor total da NF-e.
				envioNFCe +="vTotTrib="+str( vTribuTos )+"\n" #-: Valor aproximado do produto IBPT
				envioNFCe +="infAdProd=\n"

				
				if csT.strip() !='' and str( int( csT ) ) == "101":	csT = "0102"
					
				envioNFCe +="[ICMS"+str( iTems ).zfill(3)+"]\n"
				envioNFCe +="orig="+str( csT[:1] )+"\n"
				if str( d[11] ) == "3" and csT.strip() !="":	envioNFCe +="CST="+str( int( csT ) )+"\n"
				if str( d[11] ) != "3" and csT.strip() !="":	envioNFCe +="CSOSN="+str( int( csT ) )+"\n"
				envioNFCe +="modBC=3\n" #---: informar a modalidade de determinação da BC do ICMS ST: 0-Preço tabelado ou máximo sugerido; 1-Lista Negativa (valor); 2-Lista Positiva (valor); 3-Lista Neutra (valor); 4-Margem Valor Agregado (%); 5-Pauta (valor).
				envioNFCe +="vBC="+str( i[34] )+"\n"
				envioNFCe +="pICMS="+str( i[29] )+"\n"
				envioNFCe +="vICMS="+str( i[39] )+"\n"
				envioNFCe +="modBCST=4\n"
				envioNFCe +="pMVAST=\n"
				envioNFCe +="pRedBCST=\n"
				envioNFCe +="vBCST=\n"
				envioNFCe +="pICMSST=\n"
				envioNFCe +="vICMSST=\n"
				envioNFCe +="UFST=\n"
				envioNFCe +="pBCOp=\n"
				envioNFCe +="vBCSTRet=\n"
				envioNFCe +="vICMSSTRet=\n"
				envioNFCe +="motDesICMS=\n"
				envioNFCe +="pCredSN=\n"
				envioNFCe +="vCredICMSSN=\n"
				envioNFCe +="vBCSTDest=\n"
				envioNFCe +="vICMSSTDest=\n"
				envioNFCe +="vICMSDeson=\n"
				envioNFCe +="vICMSOp=\n"
				envioNFCe +="pDif=\n"
				envioNFCe +="vICMSDif=\n"

				envioNFCe +="[PIS"+str( iTems ).zfill(3)+"]\n"
				envioNFCe +="CST="+str( csTPIS )+"\n"
				envioNFCe +="vBC="+str( i[52] )+"\n"
				envioNFCe +="pPIS="+str( i[50] )+"\n"
				envioNFCe +="qBCProd=0\n"
				envioNFCe +="vAliqProd=0\n"
				envioNFCe +="vPIS="+str( i[54] )+"\n"

				envioNFCe +="[COFINS"+str( iTems ).zfill(3)+"]\n"
				envioNFCe +="CST="+str( csTCOF )+"\n"
				envioNFCe +="vBC="+str( i[53] )+"\n"
				envioNFCe +="pCOFINS="+str( i[51] )+"\n"
				envioNFCe +="qBCProd=0\n"
				envioNFCe +="vAliqProd=0\n"
				envioNFCe +="vCOFINS="+str( i[55] )+"\n"
		
				iTems +=1
				
			conn.cls( sql[1] )	
			vDesconto = self.p.d[25]
			
			"""  Totalizacao da NFCe - Trobutos   """
			envioNFCe +="[Total]\n"
			envioNFCe +="vBC="+str( self.p.d[31] )+"\n"
			envioNFCe +="vICMS="+str( self.p.d[26] )+"\n"
			envioNFCe +="vICMSDeson=\n"
			envioNFCe +="vBCST=\n"
			envioNFCe +="vST=\n"
			envioNFCe +="vProd="+str( self.p.d[ 36] )+"\n"
			envioNFCe +="vFrete=\n"
			envioNFCe +="vSeg=\n"
			envioNFCe +="vDesc="+str( vDesconto )+"\n"
			envioNFCe +="vII=\n"
			envioNFCe +="vIPI=\n"
			envioNFCe +="vPIS="+str( self.p.d[70] )+"\n"
			envioNFCe +="vCOFINS="+str( self.p.d[71] )+"\n"
			envioNFCe +="vOutro="+str( self.p.d[24] )+"\n"
			envioNFCe +="vNF="+str( self.p.d[37] )+"\n"
			envioNFCe +="vTotTrib="+str( vTT )+"\n" #-----------: Total Geral do Imposto Aproximado

			envioNFCe +="[Transportador]\n"
			envioNFCe +="modFrete=9\n" #------------------------: 0-por conta do emitente; 1-por conta do destinatário; 2-por conta de terceiros; 9-sem frete
			envioNFCe +="CNPJCPF=\n"
			envioNFCe +="xNome=\n"
			envioNFCe +="IE=\n"
			envioNFCe +="xEnder=\n"
			envioNFCe +="xMun=\n"
			envioNFCe +="UF=\n"
			envioNFCe +="vServ=\n"
			envioNFCe +="vBCRet=\n"
			envioNFCe +="pICMSRet=\n"
			envioNFCe +="vICMSRet=\n"
			envioNFCe +="CFOP=\n"
			envioNFCe +="cMunFG=\n"
			envioNFCe +="Placa=\n"
			envioNFCe +="UFPlaca=\n"
			envioNFCe +="RNTC=\n"
			envioNFCe +="vagao=\n"
			envioNFCe +="balsa=\n"
			envioNFCe +="[Volume001]\n"
			envioNFCe +="qVol=\n"
			envioNFCe +="esp=\n"
			envioNFCe +="Marca=\n"
			envioNFCe +="nVol=\n"
			envioNFCe +="pesoL=\n"
			envioNFCe +="pesoB=\n"

			"""    Formas de Pagamentos    """
			if self.p.TPEmis != 2:

				fPaga = [str(self.p.d[56]),str(self.p.d[57]),str(self.p.d[58]),str(self.p.d[59]),str(self.p.d[60]),str(self.p.d[61]),str(self.p.d[62]),str(self.p.d[63]),str(self.p.d[64]),str(self.p.d[65]),str(self.p.d[66]),str(self.p.d[84])]
				if self.p.meian.GetValue():	fPaga = self.p.forma_pagamentos #----// Meia nf //

				fSele = 1
				fSequ = 1

				for pgT in fPaga:

					vlp = "0.00"
					if fSele == 1  and Decimal( pgT ) !=0:	opg, vlp = "01", str( pgT ) #--: 56-Dinheiro	 
					if fSele == 2  and Decimal( pgT ) !=0:	opg, vlp = "02", str( pgT ) #--: 57-Ch.Avista    
					if fSele == 3  and Decimal( pgT ) !=0:	opg, vlp = "02", str( pgT ) #--: 58-Ch.Predatado 
					if fSele == 4  and Decimal( pgT ) !=0:	opg, vlp = "03", str( pgT ) #--: 59-CT Credito   
					if fSele == 5  and Decimal( pgT ) !=0:	opg, vlp = "04", str( pgT ) #--: 60-CT Debito    
					if fSele == 6  and Decimal( pgT ) !=0:	opg, vlp = "99", str( pgT ) #--: 61-FAT Boleto   
					if fSele == 7  and Decimal( pgT ) !=0:	opg, vlp = "99", str( pgT ) #--: 62-FAT Carteira 
					if fSele == 8  and Decimal( pgT ) !=0:	opg, vlp = "99", str( pgT ) #--: 63-Finaceira    
					if fSele == 9  and Decimal( pgT ) !=0:	opg, vlp = "10", str( pgT ) #--: 64-Tickete      
					if fSele == 10 and Decimal( pgT ) !=0:	opg, vlp = "05", str( pgT ) #--: 65-PGTO Credito 
					if fSele == 11 and Decimal( pgT ) !=0:	opg, vlp = "99", str( pgT ) #--: 66-DEP. Conta   
					if fSele == 12 and Decimal( pgT ) !=0:	opg, vlp = "99", str( pgT ) #--: 85-Receber Local   

					
					if Decimal( vlp ) !=0:
												
						envioNFCe +="[PAG"+str( fSequ ).zfill(3)+"]\n"
						envioNFCe +="tpag="+str( opg )+"\n" #---: 01=Dinheiro, 02=Cheque, 03=Cartão de Crédito, 04=Cartão de Débito, 05=Crédito Loja, 10=Vale Alimentação, 11=Vale Refeição, 12=Vale Presente, 13=Vale Combustível, 99=Outros.
						envioNFCe +="vPag="+vlp+"\n"
						envioNFCe +="CNPJ=\n"
						envioNFCe +="tBand=\n"
						envioNFCe +="cAut=\n"
						
						"""  Pagamentos em Cartao   """
						if opg == "03" or opg == "04":	envioNFCe +=" tpIntegra=2\n" #-: 1=Pagamento integrado com o sistema de automação da empresa (Ex.: equipamento TEF, Comércio Eletrônico), 2= Pagamento não integrado com o sistema de automação da empresa (Ex.: equipamento POS)
						fSequ +=1

					fSele +=1

			if self.p.TPEmis == 2:

				nRegis = self.p.r.GetItemCount() 
				fSequ  = 1
				
				#-------------// Meia NF
				if self.p.meian.GetValue():	nRegis = len( self.p.forma_pagamentos )

				for pg in range( nRegis ):

					vlp = "0.00"
					fpg = self.p.r.GetItem(pg,2).GetText()[:2]
					vlr = Decimal( self.p.r.GetItem(pg,3).GetText().replace(",","") )
					vpc = str( Decimal( self.p.r.GetItem(pg,4).GetText().replace(",","") ) )
					
					#--------------// Meia NF
					if self.p.meian.GetValue():
						
						fpg = self.p.forma_pagamentos[ pg ].split(";")[0].split("-")[0]
						vlr = vpc = self.p.forma_pagamentos[ pg ].split(";")[1]
								
					if vlr !=0 and fpg == "01":	opg, vlp = "01", str( vlr ) #--: 56-Dinheiro	 
					if vlr !=0 and fpg == "02":	opg, vlp = "02", str( vlr ) #--: 57-Ch.Avista    
					if vlr !=0 and fpg == "03":	opg, vlp = "02", str( vlr ) #--: 58-Ch.Predatado 
					if vlr !=0 and fpg == "04":	opg, vlp = "03", str( vlr ) #--: 59-CT Credito   
					if vlr !=0 and fpg == "05":	opg, vlp = "04", str( vlr ) #--: 60-CT Debito    
					if vlr !=0 and fpg == "10":	opg, vlp = "05", str( vlr ) #--: 65-PGTO Credito
					if vlr !=0 and fpg == "06":	opg, vlp = "99", str( vlr ) #--: 61-FAT Boleto
					if vlr !=0 and fpg == "07":	opg, vlp = "99", str( vlr ) #--: 62-FAT Carteira 
					if vlr !=0 and fpg == "08":	opg, vlp = "99", str( vlr ) #--: 63-Finaceira 
					if vlr !=0 and fpg == "09":	opg, vlp = "10", str( vlr ) #--: 64-Tickete                        
					if vlr !=0 and fpg == "11":	opg, vlp = "99", str( vlr ) #--: 66-DEP. Conta 
					if vlr !=0 and fpg == "12":	opg, vlp = "99", str( vlr ) #--: 85-Receber Local 

					if Decimal( vlp ) !=0:
							
						"""  Como nao tem tag para troco o sistema guarda o valor da parcela e verifica se tem diferenca com o valor da parcela recebida e ajusta p/nao dar rejeicao  """
						if vlp != vpc:	vlp = vpc
						
						envioNFCe +="[PAG"+str( fSequ ).zfill(3)+"]\n"
						envioNFCe +="tpag="+str( opg )+"\n" #---: 01=Dinheiro, 02=Cheque, 03=Cartão de Crédito, 04=Cartão de Débito, 05=Crédito Loja, 10=Vale Alimentação, 11=Vale Refeição, 12=Vale Presente, 13=Vale Combustível, 99=Outros.
						envioNFCe +="vPag="+vlp+"\n"
						envioNFCe +="CNPJ=\n"
						envioNFCe +="tBand=\n"
						envioNFCe +="cAut=\n"
							
						"""  Pagamentos em Cartao   """
						if opg == "03" or opg == "04":	envioNFCe +=" tpIntegra=2\n" #-: 1=Pagamento integrado com o sistema de automação da empresa (Ex.: equipamento TEF, Comércio Eletrônico), 2= Pagamento não integrado com o sistema de automação da empresa (Ex.: equipamento POS)
						fSequ +=1

			"""  Conitnua  """
			envioNFCe +="[DadosAdicionais]\n"
			envioNFCe +="infAdFisco=\n"
			envioNFCe +="infCpl="+str( infoAdicionais )+"\n"
			envioNFCe +="[InfAdic001]\n"
			envioNFCe +="xCampo=\n"
			envioNFCe +="xTexto=\n"
			envioNFCe +="[ObsFisco001]\n"
			envioNFCe +="xCampo=\n"
			envioNFCe +="xTexto="
			
			rTT = ""
			
			NFechave = ""
			#NumChave = ""
			EndeWind = ""
		
			passos = []
			falhas = False
			retorno_rejeicao = ""

			"""
			
				Envio do XML p/SEFAZ			
				
			"""
			try:

				"""  Cria o XML  """
				lisTas = str( nfis ), nDavs #-: p/Gravar as rejeicoes
				em_pro = False
				
				inNF = nfis, "65", nSerie, Tmpas, pasTa
				_menssag = mens.showmsg( "{ ACBrPlus } Criando XML"+self.p.TM )
				cmd1 = "NFE.CriarNFe("+str( envioNFCe )+",1)"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
				self.s.send(cmd1)

				rTo, Endereco, qrCode, NFechave = rTn.acbrLimpa( op=10, s=self.s, nF = inNF, aINI = envioNFCe, chave = '', recupera = False, rCancela = False )
				saida_cria = rTo if "ERRO:" in rTo else "" #-: Guarda os dados quando houver erro

				"""   Expressoes regulares p/extrair o numero da chave do retorno do endereco  """
				if Endereco and len( re.search ("\d{44}" , Endereco ).group() ) == 44:	NFechave = re.search ("\d{44}" , Endereco ).group()
				existir = "c:\\ACBrMonitorPlus\\Logs\\"+str( NFechave )+'-nfe.xml'

				"""  Vefifica se o xml criado existe na estacao windows  """
				_menssag = mens.showmsg( "{ ACBrPlus } Vefificando existencia do XML ACBr-Plus"+self.p.TM )
				cmd1 = "NFE.FileExists("+ str( existir ) +")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
				time.sleep(0.2)
				self.s.send(cmd1)
				rTo, End, qrc, chv = rTn.acbrLimpa( op=11, s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False )
				
				if "ERRO:" not in rTo:	rTNFCe = rTn.acbrAbrirRetornos( parent, op = 0, rT = rTo, nF = '' )

				rTT +="1 - Criando XML\n"+str( rTo )
				if saida_cria:	rTT += "\n"+saida_cria
				if "ERRO:" in rTo:

					falhas = True
					self.rejeicaodoSefaz( lisTas, rTT, em_processamento = False )
				"""  Assina  """
				if Endereco and "OK:" in rTo.upper() and NFechave:
				#if End !="": #-: and csTaTAv == "107":


					"""  Faz a leitura do XML """
					endAn = "c:\\ACBrMonitorPlus\\Logs\\"+str( NFechave )+'-nfe.xml'
					cmd1 = "NFE.LoadfromFile("+ str( endAn ) +",15)"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
					self.s.send(cmd1)
					rTo, End, qrCode, NFechave = rTn.acbrLimpa( op=2, s=self.s, nF = inNF, aINI = envioNFCe, chave = '', recupera = False, rCancela = False )
					
					passos.append('1')

					_menssag = mens.showmsg( "{ ACBrPlus } Assinando XML"+self.p.TM )
					
					cmd1 = "NFE.AssinarNFe("+str( endAn )+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
					self.s.send(cmd1)
					rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False )
					rTNFCe = rTn.acbrAbrirRetornos( parent, op = 0, rT = rTT, nF = '' )

					rTT +="\n\n3 - Assinando XML\n"+str( rTo )

					if "ERRO:" in rTo:
						
						falhas = True
						self.rejeicaodoSefaz( lisTas, rTT, em_processamento = False )

					""" Endereco do XML Na maquina windows """
					if len( rTo.split("OK:") ) >=2:	EndeWind = rTo.split("OK:")[1].strip()
					if self.p.cnTgn.GetValue() == True and len( rTo.split("OK:") ) >= 2:	endXML = rTo.split("OK:")[1].strip()
					else:	endXML = ""

					"""  Valida """
					if "OK:" in rTo:
					
						passos.append('2')

						_menssag = mens.showmsg( "{ ACBrPlus } Validando XML"+self.p.TM )
						cmd1 = "NFE.ValidarNFe("+str( endAn )+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
						self.s.send(cmd1)
						rTo, End, qrc, chv = rTn.acbrLimpa( op=1, s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False )
						rTNFCe = rTn.acbrAbrirRetornos( parent, op = 0, rT = rTo, nF = '' )
						rTT +="\n\n2 - Validacao do XML\n"+str( rTo )
						
						if "ERRO:" in rTo:
							
							falhas = True
							self.rejeicaodoSefaz( lisTas, rTT, em_processamento = False )
				

						"""
							Enviando ao SEFAZ
						"""	
						
						if "OK:" in rTo:

							"""   Inicio para emissao da nfce em modo de contigencia	"""

							if self.p.cnTgn.GetValue() == True and endXML !="":


								"""
									** Grava Retorno de Nota **
									Dav,NF,Chave,Protocolo,DTEmissao
								"""
								nchav = NFechave[3:] # endXML.split("\\")[3][:44]
								nDaTa = datetime.datetime.now().strftime("%d/%m/%Y %T")  
								vDaTa = datetime.datetime.now().strftime("%Y-%m-%d %T")  
								
								hisTorico = "1-Emissao em contigencia off-line\nRetorno: "+str( rTo )

								lsT = nDavs,nfis,nchav,'',nDaTa,pasTa,qrCode,nSerie
								con.acbrGravarNF( self.p, lsT, passo=2, TNF = 2, ORI = 1, his = hisTorico, conTigencia = True, csTaTr="", rsConTigencia = "", vNF = '' ) #, TEM = 1, TLA = 1, ORI = 1 )

								"""   Finaliza o Recebimento no Caixa   """	
								if self.p.TPEmis == 2:	self.f.fechamento("229",'nfce', filial = self.p.Filial )
								self.p.Finalizacao = True
								self.p.envio.Enable( False )
										

								"""  Ler o XML   """
								passos.append('4')
								AnoMes   = datetime.datetime.now().strftime("%Y%m")
								psTaXML  = "c:\\ACBrMonitorPlus\\Logs\\"+str( nchav )+'-nfe.xml'
								_menssag = mens.showmsg( "{ ACBrPlus } Lendo arquivo"+self.p.TM )
										
								cmd1 = "NFE.LoadfromFile("+str( psTaXML )+",15)"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
								self.s.send(cmd1)
								rTo, End, qrc, chv = rTn.acbrLimpa( op=6, s=self.s, nF = inNF, aINI = '', chave = nchav, recupera = False, rCancela = False )
								
								rTT ="\n5-Fazendo leitura do xml\nRetorno: "+str( rTo )
								rTNFCe = rTn.acbrAbrirRetornos( parent, op = 1, rT = rTT, nF = nfis )
								hisTorico +=rTT


								"""    Impressao na Finalizacao    """

								if len( r ) >= 16 and r[15] == "T" and endXML !="":

									rlsT  = vDaTa,str( nchav ), self.s
									self.acbrNFCeReimpressao( self.p, self.p.Filial, rlsT, 2 )	
								
								
								self.p.reTsD.SetValue( hisTorico )
								self.p.reTsD.SetBackgroundColour('#D3B9B9')
								self.p.reTsD.SetForegroundColour('#118AB2')
																
								
							else:

								"""	Emissao em modo normal	"""
									
								passos.append('3')

								_menssag = mens.showmsg( "{ ACBrPlus } Enviando XML-SEFAZ"+self.p.TM )
								reinicio = True
								numVezes = 0   
								
								while reinicio:
									
								
									cmd1 = "NFE.EnviarNFe("+str( endAn )+",1)"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
									self.s.send(cmd1)
									rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False )

									rTT +="\n\n4 - Enviando ao SEFAZ\n"+str( rTo )
									rTNFCe = rTn.acbrAbrirRetornos( parent, op = 3, rT = rTT, nF = nfis )

									"""    02-05-2016-Ajuste Se Ficar com retorno de 204 Eelimnar o loop   """
									if "ERRO:" in rTo.upper().strip() and "Erro Interno" in rTNFCe[4] and "HTTP" in rTNFCe[4].upper().strip():

										self.rejeicaodoSefaz( lisTas, "Reenviando...\n\n"+rTT, em_processamento = False )
										self.p.reTsD.SetValue( "Reenviando..." )
										_menssag = mens.showmsg( "{ ACBrPlus "+str( numVezes )+" } Reenviando XML-SEFAZ"+self.p.TM+"\n\nO servidor da SEFAZ não responde, reenviando o XML!!" )
											
									else:	reinicio = False
									numVezes +=1
									if numVezes == 2:	reinicio = False
									
								if rTNFCe[1] !=[] and rTNFCe[2] !=[] and rTNFCe[3] !=[]: 

									rS = "[ENVIO] Ambiente...........: "+str( rTNFCe[1][0] )+\
										 "\nCódigo de Retorno..........: "+str( rTNFCe[1][1] )+\
										 "\nMotivo.....................: "+str( rTNFCe[1][2] )+\
										 "\nUF.........................: "+str( rTNFCe[1][3] )+\
										 "\nNº Recebimento.............: "+str( rTNFCe[1][4] )+\
										 "\nDT-Recebimento.............: "+str( rTNFCe[1][5] )+\
										 "\n\n[RETORNO] Código de Retorno: "+str( rTNFCe[2][2] )+\
										 "\nMotivo.....................: "+str( rTNFCe[2][3] )+\
										 "\n\n[NFE-"+str(nfis).zfill(7)+"] Numero Chave.: "+str( rTNFCe[3][4] )+\
										 "\nNº Protolcolo..............: "+str( rTNFCe[3][6] )+\
										 "\nDigestValues...............: "+str( rTNFCe[3][7] )
										 
									sDaTa = str( rTNFCe[1][5] ).split(' ')
									nDaTa = str( datetime.datetime.strptime( sDaTa[0], '%d/%m/%Y').date() )+" "+sDaTa[1]
								
									self.p.nnfc.SetValue( str( nfis ) )
									self.p.seri.SetValue( nSerie )
									self.p.npro.SetValue( str( rTNFCe[3][6] ) )
									self.p.ndta.SetValue( str( nDaTa ) )
									self.p.chav.SetValue( str( rTNFCe[3][4] ) )
									self.p.dfvl.SetValue( str( rTNFCe[3][7] ) )
									
									"""
										105	Ok, Beleza-Vai Demorar um pouco"
										150	Ok, Beleza-Atrasado"
										110	Ok, Beleza-Mais nao pode usar o numero da nfce-vc ta ferrado"
										301	Ok, Beleza-Mais nao pode usar o numero da nfce-vc ta ferrado nao pode emitir nota"
										302	Ok, Beleza-Mais nao pode usar o numero da nfce-seu cliente ta ferrado vc nao pode emitir a nota pra ele"
									"""

									if   str( rTNFCe[2][2] ) == "100":	self.p.reTsD.SetForegroundColour("#8BDBF6")
									else:	self.p.reTsD.SetForegroundColour("#FF5858")

									self.p.reTsD.SetValue( rS )

									if audiToria == "T" and str( rTNFCe[2][2] ) != "100":	open( emilogs, "a" ).write("\nDAV: "+str( nDavs )+" Abertura: "+str(datetime.datetime.now().strftime("%d/%m/%Y %T"))+"\n"+str( rS )+"\n")

									cSTAT = ["100","105","150","110","301","302"]
									emprc = ["105","204","539"] #-: Notas fiscais ja processadas no sefaz

									emlst = str( nfis ), nDavs, str( rTNFCe[3][4] ), str( rTNFCe[2][2] ) 

									retorno_rejeicao = rTNFCe[2][2]
									"""
										A duplicidade de nota fiscal, normalmente fica registra no sefaz, duas notas com o mesmo numero mais com codificacao diferentes
										p/q quando o acbr reenvia a nota troca a codificacao
									"""  
									if str( rTNFCe[2][2] ) == "539" and len( str( rTNFCe[2][3] ).split("[chNFe:") ) >=2 and str( rTNFCe[2][3] ).split("[chNFe:")[1][:44].isdigit():

										nova_chave = str( rTNFCe[2][3] ).split("[chNFe:")[1][:44]
										if len( nova_chave.strip() ) == 44 and nova_chave!= str( rTNFCe[3][4] ):	emlst = str( nfis ), nDavs, nova_chave, str( rTNFCe[2][2] )
	

									if str( rTNFCe[2][2] ) in emprc:	em_pro = self.rejeicaodoSefaz( emlst, "", em_processamento = True )

										
									if str( rTNFCe[2][2] ) in cSTAT:
				
										"""
											** Grava Retorno de Nota **
											Dav,NF,Chave,Protocolo,DTEmissao
										"""
										hisTorico = str( rTo )
										if self.p.n !="" and self.p.n[8] !=None:	hisTorico = self.p.n[8]+"\n\n"+str( rTo )

										lsT = nDavs,nfis,rTNFCe[3][4],rTNFCe[3][6],rTNFCe[1][5],pasTa,qrCode,nSerie
										con.acbrGravarNF( self.p, lsT, passo=2, TNF = 2, ORI = 1, his = hisTorico, conTigencia = False, csTaTr = str( rTNFCe[2][2] ), rsConTigencia = "", vNF = '' ) #, TEM = 1, TLA = 1, ORI = 1 )


										"""   Finaliza o Recebimento no Caixa   """	
										if self.p.TPEmis == 2:	self.f.fechamento("229",'nfce', filial = self.p.Filial )
										self.p.Finalizacao = True
										self.p.envio.Enable( False )
										

										"""  Ler o XML   """
										passos.append('4')
										AnoMes   = datetime.datetime.now().strftime("%Y%m")
										psTaXML  = "c:\\ACBrMonitorPlus\\Arqs\\"+str( login.filialLT[ self.p.Filial ][9] ).strip()+"\\NFCe\\"+str( AnoMes )+"\\NFCe\\"+str( rTNFCe[3][4] )+'-nfe.xml'
										_menssag = mens.showmsg( "{ 2-ACBrPlus } Lendo arquivo"+self.p.TM )
										
										cmd1 = "NFE.LoadfromFile("+str( psTaXML )+",10)"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
										self.s.send(cmd1)
										rTo, End, qrc, chv = rTn.acbrLimpa( op=4, s=self.s, nF = inNF, aINI = '', chave = rTNFCe[3][4], recupera = False, rCancela = False )
										rTT +="\n\n5 - Lendo Arquivo\n"+str( rTo )
										rTNFCe = rTn.acbrAbrirRetornos( parent, op = 1, rT = rTT, nF = nfis )
										
										
										"""   Grava o xml no banco   """
										lsT = nDavs,nfis,rTNFCe[3][4],rTNFCe[3][6],rTNFCe[1][5],pasTa,qrCode
										con.acbrGravarNF( self.p, lsT, passo=3, TNF = 2, ORI = 1, his = hisTorico, conTigencia = False, csTaTr = "", rsConTigencia = "", vNF = '' ) #, TEM = 1, TLA = 1, ORI = 1 )

									
										"""    Impressao na Finalizacao    """
										if len( r ) >= 16 and r[15] == "T":

											rlsT = nDaTa,str( rTNFCe[3][4] ), self.s
											self.acbrNFCeReimpressao( self.p, self.p.Filial, rlsT, 2 )	

								else:
									
									rS = rTNFCe[4]
									self.rejeicaodoSefaz( lisTas, rS, em_processamento = False )
								
								self.p.reTsD.SetValue( rS )
				

				del _menssag
					
				
			except Exception, _reTornos:
				
				del _menssag
				falhas = True
				rTT +="\n"+str( _reTornos )
				de = str( datetime.datetime.now().strftime("%d-%m-%Y %T") )+" "+login.usalogin
				open(nfclogs,"a").write(de+" ENVIO EMISSAO NFCE:\n"+str( _reTornos )+"\n"+str( rTT.decode('iso-8859-7').encode('utf8') )+"\n")
				
			con.acbrFechar( cnf = self.s )

			if falhas == True:
				
				try:	self.p.reTsD.SetValue( rTT )
				except Exception, _er:
					
					rTT = str( unicodedata.normalize('NFKD', rTT.decode('CP1252')).encode('UTF-8', 'ignore') )
					self.p.reTsD.SetValue( rTT )
					
					de = str( datetime.datetime.now().strftime("%d-%m-%Y %T") )+" "+login.usalogin
					open(nfclogs,"a").write(de+" ENVIO EMISSAO NFCE-Falhas:\n"+str( _er )+"\n"+str( rTT )+"\n")

			if em_pro:
				
				__ms = ("="*200)+"\nNota fiscal localizada na sefaz \nRefaça o processo de recebimento p/o sistema tentar a recuperação do xml\n"+("="*200)
				self.p.reTsD.SetValue( __ms + "\n\n"+rTT)


			if retorno_rejeicao:

				menssagem_retorno = ""
				if retorno_rejeicao == "105":	menssagem_retorno = "105 - Este retorno será apresentado quando for realizado uma consulta pelo número de recibo do lote "\
																	"e o webservice ainda não terminou de processar o XML enviado\n\n1 - Aguarde um tempo e reenvio o dav p/ajuste e download do xml\n"+(" "*150)

				if retorno_rejeicao == "204":	menssagem_retorno = "204 - Isso acontece quando uma nota já autorizada é reenviada para a SEFAZ\n\n1 - Aguarde um tempo e reenvio o dav p/ajuste e download do xml\n"\
																	"2 - Se persistir o problema, Comunique ao suporte p/resolução da rejeição\n"+(" "*140)
				
				if retorno_rejeicao == "539":	menssagem_retorno = "539 - Quando for emitida uma NF-e e na Sefaz já existir outra NF-e, já autorizada, com o mesmo CNPJ Emitente, Modelo, Série e Número "\
																	"mas com, Data de Emissão, Tipo de Emissão\nou Código Numérico ou outras posições da Chave de Acesso diferentes, será retornado\n"\
																	"a rejeição Duplicidade de NF-e, com diferença na Chave de Acesso\n\n1 - Comunique ao suporte p/resolução da rejeição\n"+(" "*150)

				if menssagem_retorno:	alertas.dia( self.p,menssagem_retorno,"Retorno SEFAZ [ Rejeição ]" )


	def enviaConTigencia(self, parent, lsT, pasTas ):

		self.p = parent
		self.f = parent.p

		rTn = acbRetornos()
		
		d = login.filialLT[ self.p.Filial ][30].split(";")
		r = login.filialLT[ self.p.Filial ][38].split("|")[0].split(";")

		"""   Auditoria de Emissao   """
		if len( r ) >=13:	audiToria = r[13]
		else:	audiToria = "F"

		"""   Cria o diretorio da NFCe   """
		pasTa,Tmpas, pCan = rTn.acbrCriaPasTa( self.p.Filial, True, str( lsT[5] ) )
		inNF = lsT[1], "65", lsT[2], Tmpas, pasTa
		
		m = nfe31c()
		
		carquivo = diretorios.esCerti+d[6]
		csenha   = d[5]
		nDavs    = str( self.p.nuDavs ) #----: Numero do DAV
		nSerie   = str( r[5] ) #-------------: Numero da Serie
		dTemis   = str( lsT[5] )
		dTNFCe   = dTemis.split(" ")[0].split("-")
		informar = rTT = ""
		infDupli = ""
		
		"""  Conexao com acbr  """
		con = acbrTCP()

		cn = con.acbrAbrir( cnT=1, par = parent, TipoNF = 1, fls = self.p.Filial )
		if cn[0] == False:	return
		
		self.s = cn[1]
		
		_menssag = mens.showmsg( "{ ACBrPlus } Vendo existencia do XML Local"+self.p.TM )
		AnoMes  = dTNFCe[0]+dTNFCe[1]
		
		if pasTas[0] == "2" or pasTas[0] == "3":	exisTen = os.path.exists( pasTas[1] )
		else:	exisTen = True
		
		
		if exisTen == True:

			if pasTas[0] != "1":
				
				"""
					Faz a leitura do xml p/enviar para a estacao windows
				"""

				_menssag = mens.showmsg( "{ ACBrPlus } Abrindo XML Local"+self.p.TM )
				cArq = open( pasTas[1] ).read()
				xArq ='"'+cArq+'"'
			
			
				"""
					Faz o Envio do XML p/a estacao windows p/pasta c:\ACBrMonitorPlus\Logs
				"""
				
				_menssag = mens.showmsg( "{ ACBrPlus } Enviando XML p/ACBr-Plus"+self.p.TM )
				cmd1 = "NFE.SaveToFile("+pasTas[2]+","+xArq+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
				self.s.send(cmd1)
				rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False )
				informar += "1-Verificando a existencia do XML\n"+str( rTo.decode('iso-8859-7').encode('utf8') )
									
									
			"""
				Verifica a existencia do XML na pasta c:\ACBrMonitorPlus\Logs
			"""	
			_menssag = mens.showmsg( "{ ACBrPlus } Vefificando existencia do XML ACBr-Plus"+self.p.TM )
			cmd1 = "NFE.FileExists("+pasTas[2]+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)

			self.s.send(cmd1)
			rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False )
			informar += "1-Verificando a existencia do XML\n"+str( rTo.decode('iso-8859-7').encode('utf8') )

			self.p.reTsD.SetValue( informar )
			

			if "OK:" in rTo.upper():


				"""
					Faz o envio do xml p/SEFAZ
				"""	
				_menssag = mens.showmsg( "{ ACBrPlus } Reemviando XML ao SEFAZ"+self.p.TM )
				reinicio = True
				numVezes = 0   
								
				while reinicio:
				
					cmd1 = "NFE.EnviarNFe("+pasTas[2]+",1)"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
					self.s.send(cmd1)
					rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.s, nF = '', aINI = '', chave = '', recupera = False, rCancela = False )

					rTT +="\n\n4 - Enviando ao SEFAZ\n"+str( rTo )
					rTNFCe = rTn.acbrAbrirRetornos( parent, op = 3, rT = rTT, nF = lsT[1] )


					if "ERRO:" in rTo and "Erro Interno" in rTNFCe[4] and "HTTP" in rTNFCe[4]:
										
						_menssag = mens.showmsg( "{ ACBrPlus "+str( numVezes )+" } Reenviando XML-SEFAZ"+self.p.TM+"\n\nO servidor da SEFAZ não responde, reenviando o XML!!\nAguarde..." )
											
					else:	reinicio = False
					numVezes +=1

					if numVezes == 2:	reinicio = False


				informar += "\n2-Enviando XML ao SEFAZ\n"+str( rTo.decode('iso-8859-7').encode('utf8') )
				if rTNFCe[1] !=[] and rTNFCe[2] !=[] and rTNFCe[3] !=[]: 

					self.p.reTsD.SetBackgroundColour("#000000")
					self.p.reTsD.SetForegroundColour("#68C5E3")
					
					informar = "[ENVIO] Ambiente...........: "+str( rTNFCe[1][0] )+\
					 "\nCódigo de Retorno..........: "+str( rTNFCe[1][1] )+\
					 "\nMotivo.....................: "+str( rTNFCe[1][2] )+\
					 "\nUF.........................: "+str( rTNFCe[1][3] )+\
					 "\nNº Recebimento.............: "+str( rTNFCe[1][4] )+\
					 "\nDT-Recebimento.............: "+str( rTNFCe[1][5] )+\
					 "\n\n[RETORNO] Código de Retorno: "+str( rTNFCe[2][2] )+\
					 "\nMotivo.....................: "+str( rTNFCe[2][3] )+\
					 "\n\n[NFE-"+str(lsT[1]).zfill(7)+"] Numero Chave.: "+str( rTNFCe[3][4] )+\
					 "\nNº Protolcolo..............: "+str( rTNFCe[3][6] )+\
					 "\nDigestValues...............: "+str( rTNFCe[3][7] )

					if audiToria == "T" and str( rTNFCe[2][2] ) != "100":	open( emilogs, "a" ).write("\nDAV: "+str( nDavs )+" ContiGencia-Abertura: "+str(datetime.datetime.now().strftime("%d/%m/%Y %T"))+"\n"+str( informar )+"\n")

					rDpl = ["204","539"]
					notf = str( lsT[1] )

					if str( rTNFCe[2][2] ) in rDpl and len( str( rTNFCe[2][3] ).split("[") ) == 3:
					
						novaChave = str( rTNFCe[2][3] ).split("[")[1].replace("]","").replace("chNFe:","")
						if len( novaChave ) == 44 and novaChave.isdigit() == True:

							lsT = str( rTNFCe[3][4] ),novaChave,str( rTNFCe[2][2] )
							con.acbrGravarNF( self.p, lsT, passo=5, TNF = 2, ORI = 1, his = "", conTigencia = False, csTaTr = str( rTNFCe[2][2] ), rsConTigencia = "", vNF = '' ) #, TEM = 1, TLA = 1, ORI = 1 )
							infDupli = "{ Retorno 204/539 }\n\nNota em duplicidade utilize o gerenciador de NFs p/Recuperação do XML"

							emlst = notf, str( nDavs ), str( novaChave ), str( rTNFCe[2][2] )
							if str( rTNFCe[2][2] ) in rDpl:	em_pro = self.rejeicaodoSefaz( emlst, "", em_processamento = True )

					cSTAT = ["100","105","150","110","301","302"]
					if str( rTNFCe[2][2] ) in cSTAT:

				 
						"""
							** Grava Retorno de Nota **
							Dav,NF,Chave,Protocolo,DTEmissao
						"""
						hisTorico = str( rTo )


						lsT = lsT[0],lsT[1],rTNFCe[3][4],rTNFCe[3][6],rTNFCe[1][5],pasTa,lsT[4],lsT[2]
						con.acbrGravarNF( self.p, lsT, passo=2, TNF = 2, ORI = 1, his = hisTorico, conTigencia = False, csTaTr = str( rTNFCe[2][2] ), rsConTigencia = self.p.TpcT, vNF = '' ) #, TEM = 1, TLA = 1, ORI = 1 )

						"""  Ler o XML   """
						_menssag = mens.showmsg( "{ 3-ACBrPlus } Lendo arquivo"+self.p.TM )
						
						"""  Atuliza no cadastro de pedidos, e no gerenciador de Notas  """
						cmd1 = "NFE.LoadfromFile("+pasTas[2]+",10)"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
						self.s.send(cmd1)
						rTo, End, qrc, chv = rTn.acbrLimpa( op=4, s=self.s, nF = inNF, aINI = '', chave = rTNFCe[3][4], recupera = False, rCancela = False )
						rTT +="\n\n5 - Lendo Arquivo\n"+str( rTo )
						rTNFCe = rTn.acbrAbrirRetornos( parent, op = 1, rT = rTT, nF = lsT[1] )
						
						
						"""   Grava o xml no banco   """
						lsT = lsT[0],lsT[1],rTNFCe[3][4],rTNFCe[3][6],rTNFCe[1][5],pasTa,lsT[4]
						con.acbrGravarNF( self.p, lsT, passo=3, TNF = 2, ORI = 1, his = hisTorico, conTigencia = False, csTaTr = "", rsConTigencia = "", vNF = '' ) #, TEM = 1, TLA = 1, ORI = 1 )

						self.p.envio.Enable( False )

			self.p.reTsD.SetValue( informar )

		else:

			dS = "{ XML Não locaziado }\n"+\
				 "\nNumero DAV..: "+nDavs +\
				 "\nNumero Chave: "+lsT[3]+\
                 "\nNumero Serie: "+nSerie+\
                 "\nData Emissão: "+dTemis+\
                 "\n\nPasta Local.: "+pasTas[1]
                 
			self.p.reTsD.SetValue( dS )

		del _menssag
		con.acbrFechar( cnf = self.s )

		if infDupli !="":	alertas.dia(self.p,infDupli+"\n"+(" "*130),"Recuperação do XML")


	def rejeicaodoSefaz(self, lisT, hisTorico, em_processamento = False ):

		NuNoTa = lisT[0]
		numDav = lisT[1]
		if not em_processamento:	rSefaz = str( unicodedata.normalize('NFKD', hisTorico.decode('CP1252')).encode('UTF-8', 'ignore') )
		if not em_processamento:	daTEmi = datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin	

		conn = sqldb()
		sql  = conn.dbc("Rejeicao NFe, Retorno SEFAZ", fil = self.p.Filial , janela = self.p )
		grva = True
		
		if sql[0] == True:
			
			try:
				
				if sql[2].execute("SELECT nf_rsefaz FROM nfes WHERE nf_numdav='"+str( numDav )+"' and nf_nnotaf='"+str( NuNoTa )+"'"):
					
					rS = sql[2].fetchone()[0]
					if not em_processamento and rS != None:	rS += "\n\n"+daTEmi+"\n"+str( rSefaz )
					if not em_processamento and rS == None:	rS  = daTEmi+"\n"+str( rSefaz )
					
					if not em_processamento:	sql[2].execute("UPDATE nfes SET nf_rsefaz='"+str( rS )+"' WHERE nf_numdav='"+str( numDav )+"' and nf_nnotaf='"+str( NuNoTa )+"'")
					if em_processamento:	sql[2].execute("UPDATE nfes SET nf_nchave='"+str( lisT[2] )+"', nf_ncstat='"+str( lisT[3] )+"' WHERE nf_numdav='"+str( numDav )+"' and nf_nnotaf='"+str( NuNoTa )+"'")
					sql[1].commit()

			
			except Exception, rjc:
				
				de = str( datetime.datetime.now().strftime("%d-%m-%Y %T") )+" "+login.usalogin
				open( nfclogs, "a" ).write(de+" Erro na Rejeicao:\n"+str( rjc )+"\n")
				grva = False
			
				
			conn.cls( sql[1] )

			if em_processamento:	return grva


class acbRetornos:

	def acbrAbrirRetornos(self, par, op = 0, rT = "", nF = '', msT = True ):


		self.p = par
		cINI   = ""
		
		if op !=1 and msT == True:	par.reTsD.SetValue( "" )
			
		for i in rT.split('\n'):
			
			if i.split('\r') !="":	cINI +=i.split('\r')[0]+"\n"
			
			"""   Limpa o Retorno p/forma arquivo INI   """
			fINI = ""
			for s in cINI.split('\n'):
			
				
				if "[STATUS]" in s or "[ENVIO]" in s or "[RETORNO]" in s or "[NFE"+str(nF)+"]" in s:	fINI+=s+'\n'
				if len( s.split("=") ) == 2:	fINI+=s+'\n'
				if "DigVal" in s:	fINI+=s+'\n' #-: Estar entrando separa p/q ele tem o caracter '='


		"""  Cria Arquivo INI com o retorno  """
		Config = ConfigParser.ConfigParser()
		string = StringIO.StringIO(fINI)
		Config.readfp(string)
		secTio = Config.sections()

		""" Tratamento dos Retornos do Arquivo INI
			slsT=Statis, elsT=Envio, rlsT=Retorno, nlsT=NotaFiscal
		"""
		slsT = elsT = rlsT = nlsT = []
		sTa = ["TpAmb","CStat","XMotivo","CUF","DhRecbto","DhRetorno","XObs"]
		enV = ["TpAmb","CStat","XMotivo","CUF","NRec","DhRecbto"]
		rrT = ["TpAmb","NRec","CStat","XMotivo","CUF"]
		nFs = ["TpAmb","CStat","XMotivo","CUF","ChNFe","DhRecbto","NProt","DigVal"]


		for sc in secTio:
			
			if sc == "STATUS":	slsT = self.reTornosINI( sc, sTa, Config )
			if sc == "ENVIO":	elsT = self.reTornosINI( sc, enV, Config )
			if sc == "RETORNO":	rlsT = self.reTornosINI( sc, rrT, Config )
			if sc == "NFE"+str( nF ):	nlsT = self.reTornosINI( sc, nFs, Config )

		
		"""   Tratamento do Retorno de ERRO   """
		if "ERRO:" in rT:
			
			sair = ""
			mens = ""
			
			for er in rT.split("\n"):
			
				if sair == "ERRO":	mens +=er+"\n"
				if "ERRO:" in er:	sair = "ERRO"
			
			if mens !="":	rT = mens	
		
		return slsT,elsT,rlsT,nlsT,rT


	def acbrCriaPasTa(self, Filial, conT, emis ):


		ddm = datetime.datetime.now().strftime("%m%Y")
		ddf = datetime.datetime.now().strftime("%d%m%Y")
		"""
		
			Envio da contigencia
			
		"""
		if conT == True:

			dTE = emis.split(" ")[0].split("-")
			ddm = dTE[1]+dTE[0]
			ddf = dTE[2]+dTE[1]+dTE[0]
				
		if os.path.exists( diretorios.nfceacb+Filial.lower() ) == False:	os.makedirs(diretorios.nfceacb+Filial.lower())
		if os.path.exists( diretorios.nfceacb+Filial.lower()+"/"+ddm ) == False:	os.makedirs(diretorios.nfceacb+Filial.lower()+"/"+ddm)

		if os.path.exists( diretorios.nfceacb+Filial.lower()+"/"+ddm+"/danfe") == False:	os.makedirs(diretorios.nfceacb+Filial.lower()+"/"+ddm+"/danfe")
		if os.path.exists( diretorios.nfceacb+Filial.lower()+"/"+ddm+"/cance") == False:	os.makedirs(diretorios.nfceacb+Filial.lower()+"/"+ddm+"/cance")

		if os.path.exists( diretorios.nfceacb+Filial.lower()+"/"+ddm+"/danfe/"+ddf ) == False:	os.makedirs(diretorios.nfceacb+Filial.lower()+"/"+ddm+"/danfe/"+ddf)
		if os.path.exists( diretorios.nfceacb+Filial.lower()+"/"+ddm+"/cance/"+ddf ) == False:	os.makedirs(diretorios.nfceacb+Filial.lower()+"/"+ddm+"/cance/"+ddf)

		if os.path.exists( diretorios.nfceacb+Filial.lower()+"/"+ddm+"/tmp") == False:	os.makedirs(diretorios.nfceacb+Filial.lower()+"/"+ddm+"/tmp")
		if os.path.exists( diretorios.nfceacb+Filial.lower()+"/"+ddm+"/tmp/"+ddf ) == False:	os.makedirs(diretorios.nfceacb+Filial.lower()+"/"+ddm+"/tmp/"+ddf)

		pasTa = diretorios.nfceacb+Filial.lower()+"/"+ddm+"/danfe/"+ddf+"/"
		cance = diretorios.nfceacb+Filial.lower()+"/"+ddm+"/cance/"+ddf+"/"
		Tmpas = diretorios.nfceacb+Filial.lower()+"/"+ddm+"/tmp/"+ddf+"/"

		return pasTa,Tmpas, cance

		
	def acbrCanInuRetorno(self, op, par, rT, fl, ch, rCancela = False, pasCan = "" ):

		psT, Tmp, pCan = self.acbrCriaPasTa( fl, False, '' )
		pasTa =  pCan+str( ch )+"-can.xml"

		arqxml = arqini = ""
		linhas = 0

		"""  Separa ini do xml  """
		for i in rT.split("\n"):

			if op == 1:

				if linhas !=0 and not "<procEventoNFe" in i:	arqini +=str(i)+"\n"
				if "<procEventoNFe" in i:	arqxml = i[4:]	
		
			elif op == 2 and linhas !=0:	arqini +=str(i)+"\n"
			linhas +=1

		"""  Cria Arquivo INI com o retorno  """
		Config = ConfigParser.ConfigParser()
		string = StringIO.StringIO(arqini)
		Config.readfp(string)
		secTio = Config.sections()

		slsT = []
		nFs = ["TpAmb","CStat","XMotivo","CUF","ChNFe","DhRecbto","NProt"]
		inu = ["TpAmb","CStat","XMotivo","CUF","DhRecbto","NProt"]
		
		
		if secTio !=[] and op == 1:	slsT = self.reTornosINI( secTio[0], nFs, Config )
		if secTio !=[] and op == 2:	slsT = self.reTornosINI( secTio[0], inu, Config )


		if rCancela == False and op == 1 and len( slsT ) >= 2 and slsT[1] == "135":
			
			iarquivo = open( pasTa, "w" )
			iarquivo.write( arqxml )
			iarquivo.close()
			
			slsT.append(arqxml)

		else:	slsT.append('')
		
		"""  Grava na recuperacao do XML protocolo de cancelamento  """
		if rCancela == True:

			iarquivo = open( pasCan, "w" )
			iarquivo.write( arqxml )
			iarquivo.close()
			
			slsT = arqxml

		return slsT

		
	def acbrLimpa( self, op=0, s = "", nF = '', aINI = '', chave = '', recupera = False, rCancela = False ):

		request  = ''
		endereco = ''
		qrCode   = ''
		nChave   = ''
		reTorn   = ""
		looping = True
		avanca  = True
		"""   Recebe os dados em 8192 { antes era 1024 mais parece q recebendo uma quantidade 8 vezes fica mais rapido } do ACBR, e acumala em request """


		try:
			
			data = s.recv(8192)
			request = request+data

		except Exception, rTorn:

			de = str( datetime.datetime.now().strftime("%d-%m-%Y %T") )+" "+login.usalogin
			open(nfclogs,"a").write(de+" LIMPA RETORNO:\n"+str( rTorn )+"\n")
			avanca = False
		
		if avanca == True:


			while looping:

				try:
					
					if looping !=False:
						
						data = s.recv(8192)
						request += data
						
					if op == 2 and "</NFe>" in request:	looping = False #-------------: NFe Criada
					if op == 4 and "</nfeProc>" in request:	looping = False #---------: NFCe Finalizado
					if op == 5 and "</procEventoNFe" in request:	looping = False #-: Processo p/Evento { Cancelamento }
					if op == 6 and "</NFe>" in request:	looping = False #-------------: Envio em contigencia
					if op == 7 and "</soap:Envelope" in request:	looping = False #-: Processo p/Evento { Recuperacao de Cancelamento }
					
					if op == 1 and "OK:" in request.upper():	looping = False #---------------------------------: Retorno confirmado
					if op != 2 and ( len( data ) -1 ) == 0:	looping = False #-----------------------------: Retorno Vazio { o menos -1  pq o windows manda uma sujeirinha !! }
					if op != 2 and "ESPERANDO POR COMANDOS" in request.upper():	looping = False #---------: Retorno confirmado

					if op == 10 and "OK:" in request.upper():	looping = False #---------------------------------: Retorno confirmado
					if op == 11 and "OK:" in request.upper():
						looping = False #---------------------------------: Retorno confirmado
						request = "OK: "
					if "ERRO:" in request.upper():	looping = False 
					if "Element" in data:	looping = False

					
				except Exception, rTry:

					looping = False
					de = str( datetime.datetime.now().strftime("%d-%m-%Y %T") )+" "+login.usalogin
					open(nfclogs,"a").write(de+" LIMPA RETORNO:\n"+str( rTry )+"\n")
					
	
					
		"""   Limpa o Final do arquivo  """
		request = request[:( len(request) - 1 )]
		reTorno = request
		
		if "ERRO:" in request:	return request,'','',''

		"""  nF = nfis, "65", nSerie, pasTa, PasTaDanfe """
		if op == 2 or op == 4:

			if aINI !="":	inarquivo = nF[3]+"nfce_"+str( nF[0] )+'-'+str( nF[1] )+'-'+str( nF[2] )+"_"+login.usalogin.lower()+".ini"


		if op == 2 or op == 4:	nmarquivo = nF[3]+"nfce_"+str( nF[0] )+'-'+str( nF[1] )+'-'+str( nF[2] )+".xml"
		if op == 2 or op == 4 or op == 6:	fnarquivo = nF[4]+chave+"-nfe.xml"

		if op == 10: #-: Retorna endereco da pasta onde o xml foi criado
			
			linhas  = 0
			reTorno = ""

			"""  Limpa o XML  Retirando a primeira linha do endereco  """
			for i in request.split('\n'):
				
				"""  Grava apartir da segunda linha do XML  """
				#if linhas != 0 and i !="":	reTorno +=i
				
				""" 
					Pega o endereco do aquivo na maquina windows q estar rodando o acbr
					Limpa o endereco do arquivo na maquina windows  { Fica uma sujeirinha no final a o acbr nao localiza o arquivo }
				""" 
				if linhas == 0:

					rOk = i.split("\r")[0].split("OK:")
					if len( rOk ) == 2:
						
						endereco = rOk[1].strip()
						qrCode = nChave = ""

				linhas +=1	

		
		if op == 2:
			
			"""  Resgata o QR-Code  do XML  """
			reTorno = ""
			qrCode  = ""
			nChave  = ""
			if len( request.split("OK:") ) == 2:	reTorno = request.split("OK:")[1].split('\r')[0].strip()

			if reTorno:
				
				docume = minidom.parseString( reTorno )
				qrCode,sT  = nfe31RT.AbrirXML(docume,"infNFeSupl","qrCode")
				sT,nChave = nfe31RT.AbrirXML(docume,"infNFe","Id")

			
			if rCancela == False:
				
				xarquivo = open( nmarquivo, "w" )
				xarquivo.write(reTorno)
				xarquivo.close()

			if aINI !="" and rCancela == False:

				iarquivo = open( inarquivo, "w" )
				iarquivo.write( aINI )
				iarquivo.close()

		
		if op == 4 or op == 6:
			
				arqXML = request.split("OK:")[1].strip()

				farquivo = open( fnarquivo, "w" )
				farquivo.write( arqXML )
				farquivo.close()

				reTorno = "- Criar XML -{ Endereco }\n"+endereco
				if recupera == True:	reTorno = arqXML

		return reTorno,endereco,qrCode,nChave


	def reTornosINI( self, secao, opcoes, config ):
	
		retorno = []
		for i in opcoes:

			try:	retorno.append( config.get( secao, i ) )
			except Exception, pasIn:

				de = str( datetime.datetime.now().strftime("%d-%m-%Y %T") )+" "+login.usalogin
				open(nfclogs,"a").write(de+" LEITURA INI:\n"+str( pasIn )+"\n")
				retorno.append(None)
				
		return retorno
		
			
				
	def acbrMostarRetornos(self):	pass
	
	def acbrLocalizarWindows(self, parent, Filial, pasTaXML ):
		
		reT = False
		rTn = acbRetornos()
		con = acbrTCP()
		

		cn = con.acbrAbrir( cnT=1, par = parent, TipoNF = 1, fls = Filial )
		if cn[0] == False:	return False
		self.sn = cn[1]

		cmd1 = "NFE.FileExists("+str( pasTaXML )+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
		self.sn.send(cmd1)
		rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=self.sn, nF = '', aINI = '', chave = '', recupera = False , rCancela = False )

		if "OK:" in rTo.upper():	reT = True

		
		con.acbrFechar( cnf = self.sn )
		
		return reT
	
	
	

class acbrTCP:
	
	
	def acbrAbrir(self,cnT = 1, par = "", TipoNF = 1, fls = '' ):

		

		r = login.filialLT[ fls ][38].split("|")[0].split(";") #-: NFCe
		n = login.filialLT[ fls ][38].split("|")[1].split(";") #-: NFe

		nPorT = 3434 #-----------: Porta Padrao
		TmOuT = int( r[14] ) #---: Time Out
		
		iGnor = False
		if len( r ) >= 17 and r[16] == "T":	iGnor = True
		
		esTac = login.acbrEsta #-: IP e Porta da Estacao ACBR
		if esTac == "":	esTac = r[2]

		if TipoNF == 1:
			
			nHosT = str( esTac.split(":")[0] ) #---------------------------------: Dominio/IP
			if len( esTac.split(":") ) >=2:	nPorT = int( esTac.split(":")[1] ) #-: PorTa se for especificada
		
		rTn = acbRetornos()
		rTr = True
		cnn = ""

		if cnT == 1: #-: Abrir Conexao

			cnn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if iGnor == False:	cnn.settimeout( TmOuT )
		
			"""   Conexao  """
			if iGnor == False:	_menssag = mens.showmsg( "{ ACBrPlus - Conexão }\nHosT-PorT: { "+str( nHosT )+":"+str( nPorT )+ " }\n\nO Sistema Aguardara p/"+str( TmOuT )+" Segundos" )
			if iGnor == True:	_menssag = mens.showmsg( "{ ACBrPlus - Conexão }\nHosT-PorT: { "+str( nHosT )+":"+str( nPorT )+ " }\n\nAguardando Retorno da SEFAZ no Tempo do ACBr-PLUS\n\nAguarde..." )

			try:
				

				cnn.connect((nHosT, nPorT))
				rTo, End, qrc, chv = rTn.acbrLimpa(op=1,s=cnn, nF = '', aINI = '', chave = '', recupera = False, rCancela = False  )

				rTNFCe = rTn.acbrAbrirRetornos( par, op = 1, rT = rTo )

			except Exception, _reTornos:

				de = str( datetime.datetime.now().strftime("%d-%m-%Y %T") )+" "+login.usalogin
				open(nfclogs,"a").write(de+" ABERTURA DA CONEXAO SOCKET:\n"+str( _reTornos )+"\n")

				del _menssag
				rTr = False
				alertas.dia( par,"{ Não consigo conexão }\n\nHosT: "+str( nHosT )+"\nPorT: "+str( nPorT )+"\n"+(" "*130)+"\nRetorno: "+str( _reTornos )+"\n","Falha na Conexão")


		if int( r[14] ) == 1:

			alertas.dia( par,"{ Time-Out muito baixo ajuste as configurações }\n"+(" "*130),"Falha na Conexão { Time Out }")
			rTr = False


		return rTr,cnn

		
	def	acbrFechar(self, cnf = "" ):	cnf.close()
	def acbrGravarNF( self, parent, lisTa, passo=1, TNF = 1, TEM = 1, TLA = 1, ORI = 1, his = '', conTigencia = False, csTaTr = "", rsConTigencia = "", vNF = '' ):


		agora = datetime.datetime.now().strftime("%d/%m/%Y %T ")+str( login.usalogin )
		"""
			TNF-Tipo NF 1-NFe, 2-NFCe
			TEM-Tipo de Emissao...: 1-Venda, 2-Devolucao de Vendas, 3-Comras{Entrada de Mercadorias}, 4-Devolucao Compras-RMA, 5-Transferencia, 6-Simples Faturamento
			TLA-Tipo de Lancamento: 1-Emissao 2-Inutilizar 3-Cancelamento 4-Inutilizadas
			ORI-Origem do DAV.....: 1-Vendas, 2-Compras
		"""


		"""
			passo 1-Gravar dados Iniciai da NF, Numero,Serie,Data,Tipo{1-NFe 2-NFCe}
		"""
		
		
		self.p = parent
		r = login.filialLT[ self.p.Filial ][38].split("|")[0].split(";")

		"""   Emissao em Contigencia   """
		if conTigencia == True:	infcTgn, cTgn = "1-Emitida em contigencia off-line","1"
		else:	infcTgn, cTgn = "", ""
		
		if rsConTigencia.strip() == "1":	infcTgn, cTgn = "2-Contigencia Resolvida "+str( agora ),"2"
		

		conn = sqldb()
		sql  = conn.dbc("Caixa: Relatorios Diversos", fil = self.p.Filial, janela = self.p )
		grv  = False
		rGNF = ''
		
		if sql[0] == True:	


			try:
			

				EMD = datetime.datetime.now().strftime("%Y-%m-%d") #---------------------------: Data de Recebimento
				HOJ = datetime.datetime.now().strftime("%d/%m/%Y %T ")+str( login.usalogin ) #-: Data de Recebimento 
				DHO = datetime.datetime.now().strftime("%T") #---------------------------------: Hora do Recebimento 
				USA = login.usalogin
				
				"""  
					Grava o numero da NFCe,Serie no pedido-Dav Vendas  
					lsT = nfis,nSerie,nDavs,_cod,_doc,_fan,_nom
				""" 
				if passo == 1:


					achei = sql[2].execute("SELECT * FROM nfes WHERE nf_nnotaf='"+str(lisTa[0])+"' and nf_nfesce='"+str(TNF)+"' and nf_oridav='"+str(ORI)+"' and nf_nserie='"+str(lisTa[1])+"' and nf_idfili='"+str( self.p.Filial )+"'")
					sql[2].execute("UPDATE cdavs SET cr_nota='"+str( lisTa[0] )+"', cr_seri='"+str( lisTa[1] )+"', cr_tnfs='"+str( TNF )+"' WHERE cr_ndav='"+str( lisTa[2] )+"'")
					
					if achei == 0:

						"""  Incluir no Gerenciador de NFs   """
						gerente = "INSERT INTO nfes (nf_nfesce,nf_tipnfe,nf_tipola,nf_envdat,nf_envhor,nf_envusa,nf_numdav,nf_oridav,nf_ambien,nf_idfili,nf_nnotaf,\
													 nf_codigc,nf_cpfcnp,nf_fantas,nf_clforn,nf_nserie,nf_vlnota)\
													 VALUES(%s,%s,%s,%s,%s,\
													 %s,%s,%s,%s,%s,%s,\
													 %s,%s,%s,%s,%s,%s)"

						sql[2].execute( gerente, ( TNF, TEM, TLA, EMD, DHO, USA, lisTa[2], ORI, r[7], self.p.Filial, lisTa[0],\
												lisTa[3], lisTa[4], lisTa[5], lisTa[6], lisTa[1], vNF ) )


				"""   Gravacao da Confirmacao da NFs Vendas  """
				if passo == 2:

					"""
						Dav,NF,Chave,Protocolo,DTEmissao,pasTa,qrCode 
						nDavs, nfis, rTNFCe[3][4], rTNFCe[3][6], rTNFCe[1][5], pasTa, qrCode, nSerie
					"""

					dTa = str( datetime.datetime.strptime(lisTa[4].split(' ')[0], '%d/%m/%Y').date() )
					emi = dTa+' '+lisTa[4].split(' ')[1]+' '+lisTa[3]+' '+login.usalogin
					RET = str( datetime.datetime.strptime(lisTa[4].split(' ')[0], '%d/%m/%Y').date() )

					"""
					
						Atualiza o DAV
						
					"""

					AtualDav = "UPDATE cdavs SET cr_nota='"+str( lisTa[1] )+"',cr_chnf='"+str( lisTa[2] )+"',cr_nfem='"+str( emi )+"',cr_cont='"+str( infcTgn )+"',cr_csta='"+str( csTaTr )+"' WHERE cr_ndav='"+str( lisTa[0] )+"'"
					sql[2].execute( AtualDav )


					""" 
					
						Atualiza o Gerenciador de NFs
						Limpa o QR-CODE 
						
					"""
					qrc = str( lisTa[6] )
					qr1 = qrc[3:]
					qr2 = qr1[:len(qr1)-2]
					prT = lisTa[3]
					cST = csTaTr
					
					AtualGer = "UPDATE nfes SET nf_tipola='"+str( TLA )+"', nf_retorn='"+str( RET )+"',nf_rsefaz='"+str( his )+"',\
					nf_rethor='"+str( DHO )+"',nf_protoc='"+str( prT )+"',nf_nchave='"+str( lisTa[2] )+"',nf_urlqrc='"+qr2+"',nf_contig='"+str( infcTgn )+"', nf_nconti='"+str( cTgn )+"',nf_ncstat='"+str( cST )+"' \
					WHERE nf_nnotaf='"+str( lisTa[1] )+"' and nf_nfesce='"+str( TNF )+"' and nf_oridav='"+str( ORI )+"' and nf_nserie='"+str(lisTa[7])+"' and nf_idfili='"+str( self.p.Filial )+"'"
					sql[2].execute( AtualGer )

					"""
					
						Incluir ocorrencia
						
					"""
					ocorren = "INSERT INTO ocorren (oc_docu,oc_usar,oc_corr,oc_tipo,oc_inde) VALUES (%s,%s,%s,%s,%s)"
					sql[2].execute( ocorren, ( lisTa[0], HOJ, his, 'NFCe', self.p.Filial ) )

					"""
					
						Atualiza no Contas Areceber
						
					"""
					receber = "UPDATE receber SET rc_notafi='"+str( lisTa[2] )+"' WHERE rc_ndocum='"+str( lisTa[0] )+"'"
				

				"""
				
					Incluir o xml no banco
					
				"""
				
				if passo == 3:
				
					lerXML = str( lisTa[5] )+str( lisTa[2] )+"-nfe.xml"
					arqXML = str( open( lerXML, 'r' ).read() )

					IncluXML = "INSERT INTO sefazxml (sf_numdav,sf_notnaf,sf_xmlarq,sf_nchave,sf_tiponf,sf_filial)\
					VALUES(%s,%s,%s,%s,%s,%s)"
					sql[2].execute( IncluXML, ( lisTa[0], lisTa[1], arqXML, lisTa[2], TNF, self.p.Filial ) )


				"""   
					Inclusao Exclusiva p/Recuperaca do XML
				"""
				if passo == 4:

					lerXML = str( lisTa[5] )+str( lisTa[2] )+"-nfe.xml"
					arqXML = str( open( lerXML, 'r' ).read() )

					IncluXML = "INSERT INTO sefazxml (sf_numdav,sf_notnaf,sf_xmlarq,sf_nchave,sf_tiponf,sf_filial)\
					VALUES(%s,%s,%s,%s,%s,%s)"

					AlterXML = "UPDATE sefazxml SET sf_xmlarq='"+str( arqXML )+"' WHERE sf_numdav='"+str( lisTa[0] )+"' and sf_nchave='"+str( lisTa[2] )+"' and sf_filial='"+str( self.p.Filial )+"'"
					

					achDANFE = sql[2].execute("SELECT sf_numdav FROM sefazxml WHERE sf_numdav='"+str( lisTa[0] )+"' and sf_nchave='"+str( lisTa[2] )+"' and sf_filial='"+str( self.p.Filial )+"'")
					if achDANFE == 0:	sql[2].execute( IncluXML, ( lisTa[0], lisTa[1], arqXML, lisTa[2], TNF, self.p.Filial ) )
					if achDANFE != 0:	sql[2].execute( AlterXML )
					
				
				if passo == 5:

					nChAnTe = str( lisTa[0] )
					nChNova = str( lisTa[1] )
					ncsTaT  = str( lisTa[2] )
					
					recuperaDanfe = ncsTaT+"|"+nChNova
					AtualDav = "UPDATE nfes SET nf_rconti='"+str( recuperaDanfe )+"' WHERE nf_nchave='"+str( nChAnTe )+"'"
					sql[2].execute( AtualDav )
					

				if passo == 6:

					"""   Grava o XML-Protocolo de Cancelamento recuperado  """
					nChave = str( lisTa[0] )
					AtualDav = "UPDATE nfes SET nf_prtcan='"+str( lisTa[1] )+"', nf_tipola='3' WHERE nf_nchave='"+str( nChave )+"'"
					sql[2].execute( AtualDav )
					
					
				sql[1].commit()
				grv = True
			
			except Exception, rGNF:

				grv = False
				de = str( datetime.datetime.now().strftime("%d-%m-%Y %T") )+" "+login.usalogin
				open( nfclogs, "a" ).write(de+" GRAVAR DADOS DA NFS:\n"+str( rGNF )+"\n")

				
			conn.cls( sql[1] )
		
		return grv,rGNF


class AcbrBoleto:

	def emisaoBoleto( self, parent, filial ):

		#self.p = parent
		
		"""  Conexao com acbr  """
		login.acbrEsta = "192.168.86.143"
		con = acbrTCP()

		cn = con.acbrAbrir( cnT=1, par = parent, TipoNF = 1, fls = filial )
		if cn[0] == False:	return
		
		self.s = cn[1]
		Bol = ""
		Bol +="[Titulo1]\n"
		Bol +="NumeroDocumento=000010\n"
		Bol +="NossoNumero=0000001\n"
		Bol +="Carteira=20\n"
		Bol +="ValorDocumento=100,50\n"
		Bol +="Vencimento=10/09/2010\n"
		Bol +="ValorMoraJuros=0,50\n"
		Bol +="DataDocumento=10/08/2010\n"
		Bol +="DataProcessamento=10/08/2010\n"
		Bol +="DataAbatimento=05/09/2010\n"
		Bol +="DataDesconto=07/09/2010\n"
		Bol +="DataMoraJuros=12/09/2010\n"
		Bol +="DataProtesto=10/10/2010\n"
		Bol +="ValorAbatimento=5,00\n"
		Bol +="ValorDesconto=0,50\n"
		Bol +="ValorMoraJuros=0,55\n"
		Bol +="ValorIOF=3,50\n"
		Bol +="ValorOutrasDespesas=2,50\n"
		Bol +="PercentualMulta=05,00\n"
		Bol +="LocalPagamento=Pagável em qualquer agência bancária mesmo após o vencimento\n"
		Bol +="Especie=DM\n"
		Bol +="EspecieMod=R$\n"
		Bol +="Sacado.NomeSacado=Sacado Teste\n"
		Bol +="Sacado.CNPJCPF=999.999.999.99\n"
		Bol +="Sacado.Pessoa=0\n"
		Bol +="Sacado.Logradouro=Rua Jose Rodrigues\n"
		Bol +="Sacado.Numero=100\n"
		Bol +="Sacado.Bairro=Jardim Moderno\n"
		Bol +="Sacado.Complemento=Casa\n"
		Bol +="Sacado.Cidade=Tatui\n"
		Bol +="Sacado.UF=SP\n"
		Bol +="Sacado.CEP=18277.500\n"
		Bol +="Sacado.Email=teste@email.com\n"
		Bol +="Mensagem=teste1|teste2\n"
		Bol +="Instrucao1=10\n"
		Bol +="Instrucao2=11\n"
		Bol +="Aceite=1\n"
		Bol +="OcorrenciaOriginal=0\n"
		Bol +="Parcela=1\n"
		Bol +="TotalParcelas=1\n"
		Bol +="SeuNumero=000020\n"
		Bol +="TipoDiasProtesto=1\n"
		Bol +="TipoImpressao=1\n"

		cmd1 = "BOLETO.IncluirTitulo("+str( Bol )+")"+chr(13)+chr(10)+chr(46)+chr(13)+chr(10)
		self.s.send(cmd1)








		print "ola"
	

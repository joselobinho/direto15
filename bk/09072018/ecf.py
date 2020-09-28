#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import datetime
import os
import shutil
import ctypes

from conectar import sqldb,gerenciador,listaemails,dialogos,cores,login,menssagem,formasPagamentos,MostrarHistorico,diretorios,numeracao,truncagem
from decimal import Decimal

alertas = dialogos()
mens    = menssagem()
forma   = formasPagamentos()

nF      = numeracao()
Trunca  = truncagem()

				
class daruma:
#---------------------Comeco

	def statusCupomFiscal(self,_par,_sTaTus,_error,_lisTa):

		rStatus = (" "*18)
		if _sTaTus.upper() == "STATUS":
			
			_mensagem = mens.showmsg("Coletando Status do ECF!!\n\nAguarde...")
			reTorno = login.libEcf.rStatusImpressoraBinario_ECF_Daruma(rStatus)
			del _mensagem
			
			if reTorno !=1:
				_sTaTus = "erro"
				_error  = str(reTorno)
				
		sTatus = open("srv/errosecf.csv","r")
		linha  = ''
		for i in sTatus.readlines():	linha += i+"\n"
		sTatus.close()

		ecfStatus = linha.split('\n')
		posicao   = 1
		retornos  = ''
		
		volTar    = True

		if _sTaTus.upper() == "STATUS":
		
			for i in rStatus:
				
				for s in ecfStatus:
					
					if s.split(';')[0] !='' and s.split(';')[1].upper() == 'STATUS' and s.split(';')[0] == str(posicao) and i == s.split(';')[2]:
						
						if _lisTa[0] !='':
							if  s.split(';')[0] in _lisTa:	retornos +=str(posicao).zfill(2)+" ["+s.split(';')[2]+"]-"+s.split(';')[4]+"\n"
						else:	retornos +=str(posicao).zfill(2)+" ["+s.split(';')[2]+"]-"+s.split(';')[4]+"\n"
					
				posicao +=1
			
			if retornos !='':	
				_reTorno,_dados = self.reTornosEcf(_par)
				if _reTorno == True:
					retornos +="\n\nNº COO: "+str(_dados[0])+"\nCCF: "+str(_dados[1])+"\nGrande Total: "+str(_dados[2])+"\nDATA Hora ECF: "+str(_dados[3])+"\nCódigo ECF: "+str(_dados[4])+"\nIns.Estadual: "+str(_dados[5])+"\nNº Fabricante: "+str(_dados[6])+"\nTipo Documento Atual: "+str(_dados[7]+" { 1-CF, 2=CNF }")
					DaTaHora  = str(_dados[3])
					
		elif  _sTaTus.upper() == "ERRO":
			
			for i in ecfStatus:
				if i.split(';')[0] !='' and i.split(';')[1].upper() == 'ERRO' and i.split(';')[0] == _error:
					retornos ="Codigo do Erro: [ "+_error+" ]\nDescrição: "+i.split(';')[4]
		
		if retornos !='':	alertas.dia(_par,"Retorno do ECF:\n\n"+retornos+"\n"+(" "*120),"Cupom Fiscal")
		if retornos !='':	volTar = False

		return volTar,retornos


	def emiTirCupom(self,_par,_Ldav,_Lcli,pagTo, Filial = '' ):

			coo = ccf = ies = fab = seq = ''
			ecf = False

			_rT,dados = self.statusCupomFiscal(_par,"status","",['6','8','11','12','17','18'])
			
			if _rT == True:
				
				_pgT = pagTo.GetItemCount()
				conn = sqldb()
				sql  = conn.dbc("Caixa: Impressão Cupom", fil = Filial, janela = _par )

				if sql[0] == True:
					
					dav = "SELECT * FROM idavs WHERE it_ndav='"+str(_Ldav[0][2])+"'"
					ach = sql[2].execute(dav)
					vac = ( Decimal(_Ldav[0][24]) + Decimal(_Ldav[0][23]) )
					vds = Decimal( _Ldav[0][25] )

					acT, vad = "D$", "0,00"
					if vac > vds:	acT,vad = "A$", str( ( vac - vds ) ).replace('.',',')
					if vds > vac:	vad = str( ( vds - vac ) ).replace('.',',')
					
					rsl = sql[2].fetchall()
					conn.cls(sql[1])
		
					if ach == 0:	alertas.dia(_par,"[Emissão Cupom], DAV: ["+str(_Ldav[0][2])+"], não localizado...\n"+(" "*100),"Emissão do Cupom")	
					if ach !=0:

						if _Lcli!='':	endereco = _Lcli[0][1]
						else:	endereco = ''

						error = login.libEcf.iCFAbrir_ECF_Daruma(_Ldav[0][39],_Ldav[0][4],endereco)

						if error !=1:	self.statusCupomFiscal(_par,"erro",str(error),[''])
						else:

							""" Retorno do coo ccf... """
							_reTorno,_dados = self.reTornosEcf(_par)
							if _reTorno == True:

								coo, ccf, fab, seq = _dados[0], _dados[1], _dados[6], _dados[4]
								for i in rsl:

									impo, quan, vlun = str(i[44]+i[44]), Trunca.intquantidade(i[12]).replace('.',','), format(i[11],',')[:len( str(i[11]) ) - 1]
									unid = i[8]

									if ( i[15] + i[16] + i[17] ) > 0: #--------------------: Medidas do Cliente COM X LAR X EXP

										vlun = format(i[14],',')[:len( str(i[14]) ) - 2] #-: Valor unitario da qt-unidade medida
										quan = Trunca.intquantidade(i[23])
										unid = i[8]

									vlun = format( Decimal( vlun ),',' ) 
									
									if i[6].strip()!='':	codi=i[6]
									else:	codi=i[5]
							
									""" Mercadorias com ICMS """
									if impo == "TT" and i[29] != 0:	impo = "T"+str( i[29] )
									if impo == "TT" and i[29] == 0:	impo = "T19" #-: Se esqueceu de colocar o percentual coloca do RJ 19%

									"""   Impressao do Produto   """
									error = login.libEcf.iCFVenderSemDesc_ECF_Daruma(impo,quan,vlun,codi,unid,i[7])
									if error !=1:	self.statusCupomFiscal(_par,"erro",str(error),[''])
									if error !=1:	break

								if error == 1:

									error = login.libEcf.iCFTotalizarCupom_ECF_Daruma(acT,vad)
									if error !=1:	self.statusCupomFiscal(_par,"erro",str(error),[''])

									indice = 0
									for i in range(_pgT):

										FPaga = str(pagTo.GetItem(indice,15).GetText())
										Receb = str(pagTo.GetItem(indice, 3).GetText()).replace('.',',')

										error = login.libEcf.iCFEfetuarPagamentoFormatado_ECF_Daruma(FPaga,Receb)
										if error !=1:	self.statusCupomFiscal(_par,"erro",str(error),[''])
										indice +=1

									""" Dados do Rodape """
									dia,mes,ano = datetime.datetime.now().strftime("%d-%m-%Y").split('-')

									cpmn  = ( _dados[5].strip() + dia+mes+ano[2:] + _dados[0].strip() + _dados[4].strip() )
									aprox = "\nValor Aproximado de Tributos (Lei 12.741):\nR$ "+_Ldav[0][72]+" Fonte: IBPT"
									opera = "Operador: "+login.usalogin.encode('utf-8')+" DAV: "+str(_Ldav[0][2])
									_noTa = "MD-5: "+str(login.pgemd5)+"\n"+opera+"\n"+login.pginfa.replace("6789: ","6789: "+cpmn)+aprox
									error = login.libEcf.iCFEncerrar_ECF_Daruma("0",_noTa)						

									if error != 1:	self.statusCupomFiscal(_par,"erro",str(error),[''])
									if error == 1:	ecf = True

								if error !=1:	self.cancelamentoEcf("automatico",_Ldav[0][2],_par)
								if error ==1 and login.gaveecfs == "T":

									leituraz = wx.MessageDialog(_par,"Confirme para abrir gaveta...\n"+(" "*100),"Caixa: [ECF] Abertura da Gaveta",wx.YES_NO|wx.YES_DEFAULT)
									if leituraz.ShowModal() ==  wx.ID_YES:	self.abrirGaveTa(_par)
						
			return ecf, coo, ccf, fab, seq


	def reducaoEcf(self,_par):

		reTor = self.statusCupomFiscal(_par,"status","",['6'])
		_reTorno,_dados = self.reTornosEcf(_par)
		dia,hora="",""
		
		""" Busca a data e Hora para fazer a reducao, sem esses parametros da falha se seguimentacao """
		if _reTorno == True:

			dia,hora = _dados[3][:8],_dados[3][8:]
			dia = dia[:4]+dia[6:]
			

		if reTor[0] == True:	alertas.dia(_par,"Ecf Redução da Leitura Z\n\n{ Não há RZ pendente }\n"+(" "*100),"Caixa: Redução Z")
		else:

			leituraz = wx.MessageDialog(_par,reTor[1]+"\n\nDATA e Hora Passada como Parâmetro: { "+str(dia)+"  [ "+str(hora)+" ] }\nConfirme para emissão da leitura\n"+(" "*100),"Caixa: [ECF] Leitura Z",wx.YES_NO|wx.NO_DEFAULT)
			if leituraz.ShowModal() ==  wx.ID_YES:

				_mensagem = mens.showmsg("Gerando Leitura da Redução Z!!\n\nAguarde...")
				error = login.libEcf.iReducaoZ_ECF_Daruma(dia,hora)
				del _mensagem
				if error !=1:	self.statusCupomFiscal(_par,"erro",str(error),[''])

	def LeituraXEcf(self,_par):

		_mensagem = mens.showmsg("Gerando Leitura X!!\n\nAguarde...")
		error = login.libEcf.iLeituraX_ECF_Daruma()
		del _mensagem
		
		if error !=1:	self.statusCupomFiscal(_par,"erro",str(error),[''])
			

	def UltimoEcfCancelar(self,_par, Filial = '' ):

		v,_dados = self.reTornosEcf(_par)
		if v==False:	return

		
		conn = sqldb()
		sql  = conn.dbc("Caixa: Cancelamento de ECF", fil = Filial, janela = _par )

		if _dados[7]=="0":	alertas.dia(_par,u"Nenhum documento disponivel para cancelar\nO COO Nº: "+str(_dados[0])+", não foi vinculado e não é cupom fiscal\n"+(" "*100),"Caixa: Cancelamento de ECF")
		if _dados[7]!="0":

			if sql[0] == True:

				pesq  = "SELECT * FROM cdavs WHERE cr_cupo='"+str(_dados[0].strip())+"' and cr_ecfb='"+str(_dados[6].strip())+"'"
				achei = sql[2].execute(pesq)
				resul = sql[2].fetchall()
				conn.cls(sql[1])

				""" Cancelamento avulso-automatico """
				if achei == 0:

					cancela = wx.MessageDialog(_par,u"COO Nº "+str(_dados[0])+", não vinculado { Cancelamento avulso }\n\nConfirme para cancelar!!\n"+(" "*100),"[ECF] Leitura Z",wx.YES_NO|wx.NO_DEFAULT)
					if cancela.ShowModal() ==  wx.ID_YES:	self.cancelamentoEcf('automatico','',_par)
						
				elif achei !=0:
						
					if _dados[6].strip() != resul[0][92].strip():	alertas.dia(_par,u"COO Nº: "+str(_dados[0])+" DAV Nº: "+resul[0][2]+"\n\nFabricante do DAV: "+resul[0][92]+"\nFabricante do ECF Local: "+_dados[6]+", Fabricantes não confere...\n\nLocaliza o ECF referente ao cupom emitido\n"+(" "*140),"Caixa: Cancelamento de cupom")
					if _dados[6].strip() == resul[0][92].strip():	alertas.dia(_par,u"COO Nº: "+str(_dados[0])+" DAV Nº: "+resul[0][2]+"\n\nFabricante do DAV: "+resul[0][92]+"\nFabricante do ECF Local: "+_dados[6]+", Ok ! confere...\n\nUtilize o icone de cancelamento na tela do caixa para fazer o cancelamento!!\n"+(" "*140),"Caixa: Cancelamento de cupom")

	def reTornosEcf(self,_par):

		volTar = True

		"""Retorno do COO,CCF,GT,ECF,IE,FAB,TIPO DOC ATUAL"""
		sTaTus = (" "*97)
		reTorn = ['']
	
		_mensagem = mens.showmsg("Coletando Informações do ECF!!\n\nAguarde...")
		error = login.libEcf.rRetornarInformacaoSeparador_ECF_Daruma("26+30+1+66+107+91+78+46","0",sTaTus)
		del _mensagem
		
		if error !=1:	self.statusCupomFiscal(_par,"erro",str(error),[''])
		if error !=1:	volTar = False
		else:	reTorn = sTaTus.split(';')
			
		return volTar,reTorn


	def cancelamentoEcf(self,_Tipo,_dav,_par):
		
		volTar = False
		reTorn = False
		_dados = ['']

		if _Tipo.upper() == "AUTOMATICO":

			_mensagem = mens.showmsg("Cancelamento de Cupom!!\n\nAguarde...")
			error = login.libEcf.iCFCancelar_ECF_Daruma()
			del _mensagem
			
			if error != 1:	self.statusCupomFiscal(_par,"erro",str(error),[''])
			if error == 1:

				volTar = True
				reTorn,_dados = self.reTornosEcf(_par)
			
		return volTar,reTorn,_dados

	def ArquivoMFD(self,_par,_dI,_dF,_indice,_Tipo, Filial = "" ):

		_chave = diretorios.homeLib+"chave.pem"
		if os.path.exists(_chave) == False:	alertas.dia(_par,u"Chave para assinatura do arquivo, não foi localizada!!\n\n"+_chave+" \n"+(" "*110),"Caixa: Relatórios Fiscais")
		if os.path.exists(_chave) == True:

			dTI = datetime.datetime.strptime(_dI.FormatDate(),'%d-%m-%Y').strftime("%d%m%Y")
			dTF = datetime.datetime.strptime(_dF.FormatDate(),'%d-%m-%Y').strftime("%d%m%Y")
			hoj = datetime.datetime.now().strftime("%d%m%Y")

			ach = False
			grv = False

			_mensagem = mens.showmsg("Aguardando o ECF Gerar Arquivo { "+str(_indice)+" }\n\nAguarde...")

			print _indice+"+[EAD]"+diretorios.homeLib+"chave.pem",_Tipo,dTI,dTF
			error = login.libEcf.rGerarRelatorio_ECF_Daruma(_indice+"+[EAD]"+diretorios.homeLib+"chave.pem",_Tipo,str(dTI),str(dTF))
			del _mensagem
			
			if error !=1:	self.statusCupomFiscal(_par,"erro",str(error),[''])
			if error ==1: #-: Copia do arquivo

				try:

					if _indice == "TDM":	ach = os.path.exists(diretorios.homeLib+"ATO_TDM_DATA.TXT")
					if _indice == "MFD":	ach = os.path.exists(diretorios.homeLib+"ATO_MFD_DATA.TXT")
					if _indice == "TDM" and ach == True:	rT = shutil.copy2(diretorios.homeLib+"ATO_TDM_DATA.TXT", diretorios.usPasta+hoj+"_"+dTI+"_"+dTF+"ATO_TDM_DATA.TXT")
					if _indice == "MFD" and ach == True:	rT = shutil.copy2(diretorios.homeLib+"ATO_MFD_DATA.TXT", diretorios.usPasta+hoj+"_"+dTI+"_"+dTF+"ATO_MFD_DATA.TXT")

					grv = True
					
				except Exception, _reTornos:  

					alertas.dia(_par,u"Arquivo "+_indice+", Processo Interrompido...\n\nRetrono: "+str(_reTornos)+"\n"+(" "*130),"Caixa: Relatórios Fiscais")

			if grv == True:
				
				gerenciador.imprimir = False
				if _indice == "TDM":	gerenciador.Anexar = diretorios.usPasta+hoj+"_"+dTI+"_"+dTF+"ATO_TDM_DATA.TXT"
				if _indice == "MFD":	gerenciador.Anexar = diretorios.usPasta+hoj+"_"+dTI+"_"+dTF+"ATO_MFD_DATA.TXT"
				gerenciador.emails   = ""
				gerenciador.TIPORL   = "ECF"
				gerenciador.parente  = _par
				gerenciador.Filial   = Filial

				ger_frame=gerenciador(parent=_par,id=-1)
				ger_frame.Centre()
				ger_frame.Show()

	def abrirGaveTa(self,_par):

		_mensagem = mens.showmsg("Abrindo Gaveta...\n\nAguarde...")
		error = login.libEcf.eAbrirGaveta_ECF_Daruma()
		del _mensagem
		
		if error !=1:	self.statusCupomFiscal(_par,"erro",str(error),[''])

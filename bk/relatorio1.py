#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 05-10-2014 21:41 JoseLobinho

import datetime
import wx
import ast

from conectar import login,dialogos,relatorios,gerenciador,formasPagamentos,truncagem,listaemails,diretorios,menssagem,numeracao
from decimal import *

from reportlab.lib.pagesizes import A4,landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.graphics import shapes
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import PCMYKColor, PCMYKColorSep,Color, black, blue, red, green, yellow, orange, magenta, violet, pink, brown,HexColor
from reportlab.lib.units import inch
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart

alertas = dialogos()
rls     = relatorios()
mens    = menssagem()
nF      = numeracao()

class RelatorioArecebr:
	
	def rldiversos(self, mdl, par, _di, _df, __id, __mod, Filiais = "", Filial = "" ):

		def cabccnf(_separa):

			""" Cabecalho """
			pag = str(pg).zfill(3)
			if __id == "01" and __mod == "CA":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filial ,"CHQS ESTORNADOS",2)
			if __id == "03" and __mod == "CA":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filial ,"CONTAS RECEBIDAS",2)
			if __id == "02" and __mod == "CA":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filial ,"CONTAS A RECEBER",2)
			if __id == "04" and __mod == "CA":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filial ,"CONFERE CARTÃO",2)
			if __id == "05" and __mod == "CA":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filial ,"BOLETOS EMITIDOS",2)
			if __id == "06" and __mod == "CA":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filial ,"Cobrança Borderô",2)
			if __id == "07" and __mod == "CA":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filial ,"LIQUIDAÇÃO",2)

			cv.setFillColor(HexColor('0x636363'))
			if __mod == "CA":

				if __id == "06":

					cv.drawString(155,33,"Nº Lote:")
					cv.drawString(155,23,"Movimento:")
					cv.drawRightString(250, 33, str( par.p.bdnBo.GetValue() ).strip() ) 
					cv.drawRightString(250, 23, str( par.mvb) )

					cv.drawString(260,33,"Somatorio:")
					cv.drawString(260,23,"QT Cheques:")
					cv.drawRightString(375, 33, str( par.som ))
					cv.drawRightString(375, 23, str( par.TCb ))

					cv.setFillColor(HexColor('0x0D0DD5'))
					cv.drawString(385,33,"Valor Total:")
					cv.drawString(385,23,"Favorecido/Portador:")
					cv.drawRightString(500, 33, str( par.vlb ))
					cv.drawString(463, 23, str( par.fvb ))
					cv.setFillColor(HexColor('0x000000'))

				if __id != "05" and __id != "06":

					cv.drawString(155,33,"01-Dinheiro:")
					cv.drawString(155,23,"02-Ch.Avista:")
					cv.drawRightString(250, 33,format(par.vlrdin,','))
					cv.drawRightString(250, 23,format(par.vlrcha,','))
					
					cv.drawString(260,33,"03-Ch.Predatado:")
					cv.drawString(260,23,"04-Catão Crédito:")
					cv.drawRightString(375, 33,format(par.vlrchp,','))
					cv.drawRightString(375, 23,format(par.vlrccr,','))

					cv.drawString(385,33,"05-Carão Débito:")
					cv.drawString(385,23,"06-Faturado Boleto:")
					cv.drawRightString(500, 33,format(par.vlrcdb,','))
					cv.drawRightString(500, 23,format(par.vlrbol,','))

					cv.drawString(510,33,"07-Carteira:")
					cv.drawString(510,23,"08-Financeira:")
					cv.drawRightString(610, 33,format(par.vlrcar,','))
					cv.drawRightString(610, 23,format(par.vlrfin,','))

					cv.drawString(620,33,"09-Tickete:")
					cv.drawString(620,23,"10-PG/Crédito:")
					cv.drawRightString(720, 33,format(par.vlrtic,','))
					cv.drawRightString(720, 23,format(par.vlrpgc,','))

					cv.drawString(730,33,"11-Deposito:")
					cv.drawString(730,23,"12-RC.Local:")
					cv.drawRightString(818, 33,format(par.vlrdep,','))
					cv.drawRightString(818, 23,format(par.vlrloc,','))

				if __id != "06":
					
					cv.setFillColor(HexColor('0x0D0DD5'))
					cv.drawString(22,23,"Valor Total:")
					if __id !="07":	cv.drawRightString(150, 23,format(par.TAreceber,','))
					if __id =="07":	cv.drawRightString(150, 23,format(par.vlTLiq,','))

				cv.setFillColor(HexColor('0x000000'))
			
			""" Titulo de Cabecalho """
			_fl = ""
			_us = "" #-: Vendedor
			
			if Filiais == True:	_fl = "  Filial: "+str( Filial )
			if par.vendedo.GetValue().strip() !="":	_us = "   Vendedor: "+par.vendedo.GetValue()
			
			cb1 = cb2= cb3= cb4= cb5= cb6= cb7= cb8= cb9= cb10= cb11= cb12='' 
			rel = u'Usuário: '+login.usalogin+u"  PERÌODO: "+cIni+" A "+cFim+_fl+_us

			if __mod == "CA":
				
				cb1  =   "22|540|Filial|"
				if __id !="06" and __id !="07":	cb2 = " 55|540|Nº DAV|"
				if __id !="06" and __id !="07":	cb3 = "130|540|Emissão|#7F7F7F"

				if __id == "01":

					cb4  =  "290|540|Estorno|#7F7F7F"
					cb5  =  "460|540|Descrição do Cliente|"
					cb6  =  "700|540|NºCheque|"
					cb7  =  "750|540|Valor|"

				elif __id == "03":

					cb4  =  "290|540|Vencimento|#7F7F7F"
					cb5  =  "335|540|Pagamento|#7F7F7F"
					cb6  =  "495|540|Forma de Pagamento|"
					cb7  =  "595|540|ValorRecebido|"
					cb8  =  "645|540|Descrição do Cliente|"

				elif __id == "02":
					
					cb4  =  "290|540|Vencimento|#7F7F7F"
					cb5  =  "340|540|Forma de Pagamento|"
					cb6  =  "450|540|Valor AReceber|"
					cb7  =  "505|540|Descrição do Cliente|"

				elif __id == "04":

					cb4  =  "175|540|Vencimento|#7F7F7F"
					cb5  =  "220|540|Forma de Pagamento|"
					cb6  =  "350|540|Bandeira|"
					cb7  =  "450|540|Nº Autorizalção|"
					cb8  =  "520|540|Valor|"
					cb9  =  "585|540|Descrição do Cliente|"
				elif __id == "05":

					cb4  =  "175|540|Vencimento|#7F7F7F"
					cb5  =  "220|540|Bco-AG-CC-Carteira|"
					cb6  =  "350|540|Nosso Numero|"
					cb7  =  "450|540|NFe - NFCe|"
					cb8  =  "520|540|Valor|"
					cb9  =  "585|540|Descrição do Cliente|"

				elif __id == "06":

					cb2  =   "56|540|SEQ|#7F7F7F"
					cb3  =   "72|540| CPF-CNPJ|#7F7F7F"
					cb4  =  "140|540|COMP|#7F7F7F"
					cb5  =  "158|540|  BCO|#7F7F7F"
					cb6  =  "180|540|Agência|#7F7F7F"
					cb7  =  "210|540|Nº Conta|#7F7F7F"
					cb8  =  "272|540|Nº Cheque|#7F7F7F"
					cb9  =  "340|540|Nº Boleto|"
					cb10 =  "420|540|Vencimento|"
					cb11 =  "465|540|Valor|"
					cb12 =  "530|540|Nº DAV-Parcela [ Correntista - Cliente ]|"

				elif __id == "07":

					cb2  =   "56|540|Nº DAV-Parcela|#7F7F7F"
					cb3  =  "133|540|Vencimento|#7F7F7F"
					cb4  =  "180|540|Baixa|#7F7F7F"
					cb5  =  "320|540|Valor|"
					cb6  =  "400|540|Forma Pagamento|"
					cb7  =  "510|540|Descrição do Cliente|"


			if _separa == False:	mdl.mtitulo(rel,cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12,7,2)
			else:
		
				if __mod == "CA":
					
					cv.line((float(cb2.split('|')[0])-2), float(ccampo), (float(cb2.split('|')[0])-2), float(lcampo))
					cv.line((float(cb3.split('|')[0])-2), float(ccampo), (float(cb3.split('|')[0])-2), float(lcampo))
					cv.line((float(cb4.split('|')[0])-2), float(ccampo), (float(cb4.split('|')[0])-2), float(lcampo))
			
					if __id == "01" or __id == "07":

						cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float(lcampo))
						cv.line((float(cb6.split('|')[0])-2), float(ccampo), (float(cb6.split('|')[0])-2), float(lcampo))
						cv.line((float(cb7.split('|')[0])-2), float(ccampo), (float(cb7.split('|')[0])-2), float(lcampo))

					if __id == "03":

						cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float(lcampo))
						cv.line((float(cb6.split('|')[0])-2), float(ccampo), (float(cb6.split('|')[0])-2), float(lcampo))
						cv.line((float(cb7.split('|')[0])-2), float(ccampo), (float(cb7.split('|')[0])-2), float(lcampo))
						cv.line((float(cb8.split('|')[0])-2), float(ccampo), (float(cb8.split('|')[0])-2), float(lcampo))

					if __id == "02":

						cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float(lcampo))
						cv.line((float(cb6.split('|')[0])-2), float(ccampo), (float(cb6.split('|')[0])-2), float(lcampo))
						cv.line((float(cb7.split('|')[0])-2), float(ccampo), (float(cb7.split('|')[0])-2), float(lcampo))

					if __id == "04":

						cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float(lcampo))
						cv.line((float(cb6.split('|')[0])-2), float(ccampo), (float(cb6.split('|')[0])-2), float(lcampo))
						cv.line((float(cb7.split('|')[0])-2), float(ccampo), (float(cb7.split('|')[0])-2), float(lcampo))
						cv.line((float(cb8.split('|')[0])-2), float(ccampo), (float(cb8.split('|')[0])-2), float(lcampo))
						cv.line((float(cb9.split('|')[0])-2), float(ccampo), (float(cb9.split('|')[0])-2), float(lcampo))

					if __id == "05":

						cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float(lcampo))
						cv.line((float(cb6.split('|')[0])-2), float(ccampo), (float(cb6.split('|')[0])-2), float(lcampo))
						cv.line((float(cb7.split('|')[0])-2), float(ccampo), (float(cb7.split('|')[0])-2), float(lcampo))
						cv.line((float(cb8.split('|')[0])-2), float(ccampo), (float(cb8.split('|')[0])-2), float(lcampo))
						cv.line((float(cb9.split('|')[0])-2), float(ccampo), (float(cb9.split('|')[0])-2), float(lcampo))


					if __id == "06":

						cv.line((float(cb2. split('|')[0])-2), float(ccampo), (float(cb2. split('|')[0])-2), float(lcampo))
						cv.line((float(cb3. split('|')[0])-2), float(ccampo), (float(cb3. split('|')[0])-2), float(lcampo))
						cv.line((float(cb4. split('|')[0])-2), float(ccampo), (float(cb4. split('|')[0])-2), float(lcampo))
						cv.line((float(cb5. split('|')[0])-2), float(ccampo), (float(cb5. split('|')[0])-2), float(lcampo))
						cv.line((float(cb6. split('|')[0])-2), float(ccampo), (float(cb6. split('|')[0])-2), float(lcampo))
						cv.line((float(cb7. split('|')[0])-2), float(ccampo), (float(cb7. split('|')[0])-2), float(lcampo))
						cv.line((float(cb8. split('|')[0])-2), float(ccampo), (float(cb8. split('|')[0])-2), float(lcampo))
						cv.line((float(cb9. split('|')[0])-2), float(ccampo), (float(cb9. split('|')[0])-2), float(lcampo))
						cv.line((float(cb10.split('|')[0])-2), float(ccampo), (float(cb10.split('|')[0])-2), float(lcampo))
						cv.line((float(cb11.split('|')[0])-2), float(ccampo), (float(cb11.split('|')[0])-2), float(lcampo))
						cv.line((float(cb12.split('|')[0])-2), float(ccampo), (float(cb12.split('|')[0])-2), float(lcampo))

				#-----: Linha Final
				cv.line(20,float(lcampo),820,float(lcampo))


		#----------------------------: Emissao do Relatorio :-----------------------------:
		self.T = truncagem()
				
		if par.CHQEstornado.GetItemCount() !=0:
			
			nRegisT = par.CHQEstornado.GetItemCount()
			indice  = 0

			dIni = datetime.datetime.strptime(_di.FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			dFim = datetime.datetime.strptime(_df.FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			hoje = format(datetime.datetime.now(),'%Y/%m/%d')

			cIni = datetime.datetime.strptime(_di.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			cFim = datetime.datetime.strptime(_df.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")

			dh  = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
			pg  = 1

			if __id == "01" and __mod == "CA":	nomeArquivo = diretorios.usPasta+"chestornados_"+login.usalogin.lower()+".pdf"
			if __id == "03" and __mod == "CA":	nomeArquivo = diretorios.usPasta+"recebidas_"+login.usalogin.lower()+".pdf"
			if __id == "02" and __mod == "CA":	nomeArquivo = diretorios.usPasta+"areceber_"+login.usalogin.lower()+".pdf"
			if __id == "04" and __mod == "CA":	nomeArquivo = diretorios.usPasta+"conferir_"+login.usalogin.lower()+".pdf"
			if __id == "05" and __mod == "CA":	nomeArquivo = diretorios.usPasta+"boletosemi_"+login.usalogin.lower()+".pdf"
			if __id == "06" and __mod == "CA":	nomeArquivo = diretorios.usPasta+"bordero_"+login.usalogin.lower()+".pdf"
			if __id == "07" and __mod == "CA":	nomeArquivo = diretorios.usPasta+"liquidacao_"+login.usalogin.lower()+".pdf"
			
			cv = canvas.Canvas(nomeArquivo, pagesize=landscape(A4))
			cabccnf(False)
			
			lcampo = 515
			ccampo = 525
			linhas = 1
			if __id == "01" and __mod == "CA":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (CHQs Estornados)|'
			if __id == "03" and __mod == "CA":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Contas Recebidas)|'
			if __id == "02" and __mod == "CA":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Contas AReceber)|'
			if __id == "04" and __mod == "CA":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Conferência Cartão)|'
			if __id == "05" and __mod == "CA":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Boletos Emitidos)|'
			if __id == "06" and __mod == "CA":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' ( Borderô de Cobrança )|'
			if __id == "07" and __mod == "CA":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' ( Liquidação de Títulos )|'
			
			for i in range( nRegisT ):

				_rc = par.CHQEstornado.GetItem(indice,13).GetText().split(';')
				indice +=1

				if __mod == "CA" and __id == "06":

					cv.setFont('Helvetica', 8)
					cv.drawString(22, float(lcampo), str( par.CHQEstornado.GetItem(i,0).GetText() ))
					
					cv.setFillColor(HexColor('#7F7F7F'))
					cv.drawString(56, float(lcampo), str( par.CHQEstornado.GetItem(i,1).GetText() )) 

					cv.setFont('Helvetica', 7)
					cv.drawRightString(136, float(lcampo), str( par.CHQEstornado.GetItem(i, 2).GetText() ))
					cv.setFont('Helvetica', 8)

					cv.drawRightString(154, float(lcampo), str( par.CHQEstornado.GetItem(i, 3).GetText() ))
					cv.drawRightString(177, float(lcampo), str( par.CHQEstornado.GetItem(i, 4).GetText() ))
					cv.drawRightString(205, float(lcampo), str( par.CHQEstornado.GetItem(i, 5).GetText() ))
					cv.drawRightString(267, float(lcampo), str( par.CHQEstornado.GetItem(i, 6).GetText() ))
					cv.drawRightString(335, float(lcampo), str( par.CHQEstornado.GetItem(i, 7).GetText() ))
					cv.setFillColor(HexColor('0x000000'))
					
					cv.drawRightString(415, float(lcampo), str( par.CHQEstornado.GetItem(i, 8).GetText() ))
					cv.drawRightString(460, float(lcampo), str( par.CHQEstornado.GetItem(i,12).GetText() ))
					cv.drawRightString(525, float(lcampo), str( par.CHQEstornado.GetItem(i, 9).GetText() ))

					cv.setFont('Helvetica', 7)
					davCorren = str( par.CHQEstornado.GetItem(i,13).GetText() )+"  "+str( par.CHQEstornado.GetItem(i,10).GetText() )
					
					cv.drawString(532, float(lcampo), davCorren[:70] )
					

				if __mod == "CA" and __id == "07":

					cv.setFont('Helvetica', 8)
					cv.drawString(22, float(lcampo), str( par.CHQEstornado.GetItem(i,0).GetText() ))
					
					cv.setFillColor(HexColor('#7F7F7F'))
					cv.drawString(56, float(lcampo), str( par.CHQEstornado.GetItem(i,1).GetText() )) 
					cv.drawString(133, float(lcampo), str( par.CHQEstornado.GetItem(i, 2).GetText() ))
					cv.drawString(180, float(lcampo), str( par.CHQEstornado.GetItem(i, 3).GetText() ))
					cv.setFillColor(HexColor('#000000'))
					cv.drawRightString(395, float(lcampo), str( par.CHQEstornado.GetItem(i, 4).GetText() ))
					cv.drawString(400, float(lcampo), str( par.CHQEstornado.GetItem(i, 6).GetText() ))
					cv.drawString(510, float(lcampo), str( par.CHQEstornado.GetItem(i, 5).GetText() ))

					
				if __mod == "CA" and _rc[0] !='' and __id != "06" and __id != "07": #-: Contas AReceber

					_emi = _ven = _est = _pag = _lan = ''

					if _rc[4] !='None':	_emi = format(datetime.datetime.strptime(str(_rc[4]),"%Y-%m-%d"),"%d/%m/%Y")+" "+str(_rc[5])+" "+str(_rc[6])
					if _rc[4] !='None':	_lan = format(datetime.datetime.strptime(str(_rc[4]),"%Y-%m-%d"),"%d/%m/%Y")
					if _rc[14]!='None': _ven = format(datetime.datetime.strptime(str(_rc[14]),"%Y-%m-%d"),"%d/%m/%Y")
					if _rc[10]!='None':	_pag = format(datetime.datetime.strptime(str(_rc[10]),"%Y-%m-%d"),"%d/%m/%Y")+" "+str(_rc[11])+" "+str(_rc[8])
					if _rc[18]!='None' and len(_rc[18].split('|')) > 1:	_est=_rc[18].split('|')[0]

					cv.setFont('Helvetica', 8)

					cv.drawString(22, float(lcampo),str(_rc[13]))
					cv.drawRightString(124, float(lcampo),str(_rc[0])+"/"+str(_rc[1]))
			
					if   __id == "04":	cv.drawString(130,float(lcampo),_lan)
					elif __id == "05":	cv.drawString(130,float(lcampo),_rc[20])
					else:	cv.drawString(130,float(lcampo),_emi)
				
					if __id == "01":

						cv.drawString(290,float(lcampo),_est)
						cv.drawString(460,float(lcampo),str(_rc[7]))
						cv.drawString(700,float(lcampo),str(_rc[16]))
						cv.drawRightString(817, float(lcampo),format(Decimal(_rc[2]),','))

					elif __id == "03":

						cv.drawString(290,float(lcampo),_ven)
						cv.drawString(335,float(lcampo),_pag)
						cv.drawString(495,float(lcampo),str(_rc[12]))
						cv.drawRightString(640, float(lcampo),format(Decimal(_rc[9]),','))

						if len(_rc[7]) > 32:	cv.setFont('Helvetica', 6)
						cv.drawString(645,float(lcampo), _rc[7][:47] )

					elif __id == "02":

						cv.drawString(290,float(lcampo),_ven)
						cv.drawString(340,float(lcampo),str(_rc[3]))
						cv.drawRightString(500, float(lcampo),format(Decimal(_rc[2]),','))
						
						if par.totaliza_cliente.GetValue():	cv.setFont('Helvetica', 6)
						cv.drawString(505,float(lcampo), _rc[7] )
						cv.setFont('Helvetica', 8)

						q = len( format(Decimal( _rc[20] ),',') )
						if par.totaliza_cliente.GetValue() and Decimal( _rc[20] ) > 0:

							if int( _rc[21]  ) > 1:

								linhas +=1
								lcampo -= 10

								cv.setFillGray(0.5,0.1) 
								cv.rect(20,float( lcampo - 2 ), 800,10, fill=1) #--: Fundo do cabecalho
								cv.setFillColor(HexColor('0x000000'))
								cv.setFont('Helvetica-Bold', 6)
								cv.drawString(340,float(lcampo), "Total do cliente:")
								cv.setFont('Helvetica-Bold', 8)
								cv.drawRightString(500, float(lcampo),format(Decimal( _rc[20] ),','))
								
							else:
								cv.setFillGray(0.5,0.1) 
								cv.rect(20,float( lcampo - 2 ),( 800 - ( q * 6 )  ),10, fill=1) #--: Fundo do cabecalho
								cv.setFont('Helvetica-Bold', 8)
								cv.setFillColor(HexColor('0x000000'))
								cv.drawRightString(818, float(lcampo),format(Decimal( _rc[20] ),','))

							cv.setFont('Helvetica', 8)
						
					elif __id == "04":

						cv.drawString(175,float(lcampo),_ven)
						cv.drawString(220,float(lcampo),str(_rc[3]))
						cv.drawString(350,float(lcampo),str(_rc[15]))
						cv.drawString(450,float(lcampo),str(_rc[17]))
						cv.drawRightString(580, float(lcampo),format(Decimal(_rc[9]),','))
						
						if len(_rc[7]) > 40:	cv.setFont('Helvetica', 7)
						cv.drawString(585,float(lcampo),str(_rc[7])+str(len(_rc[7])))
						cv.setFont('Helvetica', 8)

					elif __id == "05":
						
						cv.drawString(175,float(lcampo),_ven)
						cv.drawString(220,float(lcampo),str(_rc[3]))
						cv.drawRightString(445,float(lcampo),str(_rc[15]).zfill(8))
						cv.drawRightString(515,float(lcampo),str(_rc[19]))
						cv.drawRightString(580, float(lcampo),format(Decimal(_rc[2]),','))
						if len(_rc[7]) > 40:	cv.setFont('Helvetica', 7)
						cv.drawString(585,float(lcampo),str(_rc[7])+str(len(_rc[7])))
						cv.setFont('Helvetica', 8)

				
				if linhas !=1:	cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))

				linhas +=1
				lcampo -= 10
				if linhas >= 48:

					cabccnf(False)
					mdl.rodape(cv,rd1,'','','','','','','','',6)

					pg +=1
					cv.addPageLabel(pg)
					cv.showPage()						
					linhas = 1
					lcampo = 515
					ccampo = 525
					
					cabccnf(False if par.totaliza_cliente.GetValue() else True )
			
			cabccnf( False if par.totaliza_cliente.GetValue() else True )
			mdl.rodape(cv,rd1,'','','','','','','','',6)
			cv.save()

			gerenciador.TIPORL = ''
			gerenciador.Anexar = nomeArquivo
			gerenciador.imprimir = True
			gerenciador.Filial   = Filial
				
			ger_frame=gerenciador(parent=par,id=-1)
			ger_frame.Centre()
			ger_frame.Show()

""" Contas Apagar """
class RelatoriosApagar:
	
	def rldiversos(self,mdl,par,_di,_df,__id, __pc, Filiais = False, Filial = "" ):

		def cabccnf(_separa):


			""" Cabecalho """
			pag = str(pg).zfill(3)
			if __id == "01":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filial,"CONTAS APAGAR",2)
			if __id == "02":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filial,"CONTAS PAGAS",2)
			if __id == "03":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filial,"PLANO DE CONTAS",2)
			if __id == "04":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filial,"FLUXO DE CAIXA",2)
			
			cv.setFillColor(HexColor('0x636363'))

			if __id == "01" and not par.extrato.GetValue():
				
				cv.drawString(200,23,"Total do Contas Apagar:")
				cv.drawRightString(365, 23,format(par._sTAp,','))
				
			if __id == "02" and not par.extrato.GetValue():

				cv.drawString(200,23,"Total de Contas Pagas:")
				cv.drawString(400,23,"Juros:")
				cv.drawString(400,33,"Desconto:")
				
				cv.drawRightString(365, 23,format(par._sTPg,','))

				if par._sJur !=0:	cv.drawRightString(465, 23,format(par._sJur,','))
				if par._sDes !=0:	cv.drawRightString(465, 33,format(par._sDes,','))


			if __id == "04":
				

				cv.drawString(200,33,"Total de Contas Areceber:")
				cv.drawString(380,33,"+Saldo Inicial:")
				cv.drawString(380,23,"++Fluxo de Caixa:")
				cv.drawString(200,23,"Total de Contas Apagar:")
				cv.drawString(520,23,"Saldo Final:")
				cv.drawRightString(360, 33,format(par.T1,','))
				cv.drawRightString(360, 23,format(par.T2,','))
				cv.drawRightString(500, 33,format( par.fluxo_inicial.GetValue(),','))
				cv.drawRightString(500, 23,format(par.fluxoAcumulado,','))

				if par.T3 < 0:	cv.setFillColor(HexColor('0x873232'))
				cv.drawRightString(620, 23, '('+format(par.T3,',')+')' if par.T3 < 0 else format(par.T3,',') )

				cv.setFont('Helvetica-Bold', 7)
				if par.fluxo_inicial.GetValue() > 0:	cv.drawString(550,528,"Saldo Inicial: "+format( par.fluxo_inicial.GetValue(),',')+"  { Não acumulativo }" )

				cv.setFillColor(HexColor('0x9B7070'))
				cv.drawString(22,23,"Bandeiras: Comissão: ("+format( self.T.trunca( 3, par.T4 ), ',')+")" )
					
					
			cv.setFillColor(HexColor('0x636363'))
			
			""" Titulo de Cabecalho """
			cb1= cb2= cb3= cb4= cb5= cb6= cb7= cb8= cb9= cb10= cb11= cb12=''
			_Tipo = ""
			if par.selecao.GetValue() !='':	_Tipo += (" "*10)+u"Lançamento: "+par.selecao.GetValue()
			if par.fpagame.GetValue() !='':	_Tipo += (" "*10)+"Formas de Pagamentos: "+par.fpagame.GetValue()
			if __id == "04" and par.flAnali.GetValue() == True:	_Tipo += (" "*10)+"{ ANALITICO }  "
			if __id == "04" and par.flAnali.GetValue() == False:	_Tipo += (" "*10)+"{ SINTETICO }  "
			
			filial = "{ Geral }"
			if Filiais == True and par.rFilial.GetValue() == True:	filial = (" "*10)+"Filial: { "+str( Filial )+" }"
			if par.umanejo.GetValue():	_Tipo = "Unidade de manejo {"+str( par.umanejo.GetValue() )+"} "+_Tipo 
			
			rel = u'Usuário: '+login.usalogin+u"  PERÌODO: "+cIni+" A "+cFim+(" "*10)+_Tipo+filial

			if __id == "01" or __id == "02" and par.filbanc.GetValue():
	
				indice_bancos = par.ListaBanco.GetFocusedItem()
				__bn = par.ListaBanco.GetItem( indice_bancos, 2 ).GetText().strip()
				__ag = par.ListaBanco.GetItem( indice_bancos, 3 ).GetText().strip()
				__cc = par.ListaBanco.GetItem( indice_bancos, 4 ).GetText().strip()

				rel = rel + " Banco: "+__bn+u" Agência: "+__ag+" Conta corrente: "+__cc

					
			cb1  =   "22|540|Filial|"
			cb2  =  " 55|540|Nº Lançamento|"
			cb3  =  "130|540|Emissão|#7F7F7F"

			if __id == "01":

				cb4  =  "290|540|Vencimento|#7F7F7F"
				cb5  =  "340|540|Valor Apagar|"
				cb6  =  "410|540|Nota Fiscal|"
				cb7  =  "460|540|Descricão do Fornecedor-Credor|"
				
				if par.extrato.GetValue():
					cb5 = cb6 = cb7 = ""
					cb1 = "22|540|Extrato do Fornecedor { Contas Pagas e Apagar }   "+str( par.fornecedor.GetValue() )+"|"
					cb2  = " 55|540||"
					cb3  = "130|540||"
					cb4  = "290|540||"
					

			if __id == "02":

				cb3  =  "130|540|Duplicata-Cheque|#7F7F7F"
				cb4  =  "200|540|Emissão|#7F7F7F"
				cb5  =  "290|540|Vencimento|#7F7F7F"
				cb6  =  "335|540|Pagamento|#7F7F7F"
				cb7  =  "432|540|Juros|#7F7F7F"
				cb8  =  "467|540|Desconto|#7F7F7F"
				cb9  =  "502|540|V a l o r|"
				cb10 =  "555|540|Descricão do Fornecedor-Credor|"

				if par.extrato.GetValue():
					cb5 = cb6 = cb7 = cb8 = cb9 = cb10 = ""
					cb1 = "22|540|Extrato do Fornecedor { Contas Pagas e Apagar }   "+str( par.fornecedor.GetValue() )+"|"
					cb2  = " 55|540||"
					cb3  = "130|540||"
					cb4  = "200|540||"

			if __id == "03":

				cb1  =   "22|540|Ordem|"
				cb2  =   "55|540|Descrição das Contas|"
				cb3  =  "555|540|Valor|"
				cb4  =  "630|540|ToTaliza Contas|#7F7F7F"

			if __id == "04":

				cb1  =   "22|540|Ordem|"
				cb2  =   "55|540|Recebimento/Pagamento|"
				cb3  =  "150|540|Valor Receber||R"
				cb4  =  "250|540|Valor Apagar||R"
				cb5  =  "350|540|Saldo Receber-Apagar||R"
				cb6  =  "450|540|Saldo||R"
				cb7  =  "550|540|Fechamento|"
				
				
			if _separa == False:	mdl.mtitulo(rel,cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12,7,2)
			else:
					
				
				cv.line((float(cb2.split('|')[0])-2), float(ccampo), (float(cb2.split('|')[0])-2), float(lcampo))
				cv.line((float(cb3.split('|')[0])-2), float(ccampo), (float(cb3.split('|')[0])-2), float(lcampo))
				cv.line((float(cb4.split('|')[0])-2), float(ccampo), (float(cb4.split('|')[0])-2), float(lcampo))
			
				if __id == "01" and not par.extrato.GetValue():

					cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float(lcampo))
					cv.line((float(cb6.split('|')[0])-2), float(ccampo), (float(cb6.split('|')[0])-2), float(lcampo))
					cv.line((float(cb7.split('|')[0])-2), float(ccampo), (float(cb7.split('|')[0])-2), float(lcampo))

				if __id == "02" and not par.extrato.GetValue():

					cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float(lcampo))
					cv.line((float(cb6.split('|')[0])-2), float(ccampo), (float(cb6.split('|')[0])-2), float(lcampo))
					cv.line((float(cb7.split('|')[0])-2), float(ccampo), (float(cb7.split('|')[0])-2), float(lcampo))
					cv.line((float(cb8.split('|')[0])-2), float(ccampo), (float(cb8.split('|')[0])-2), float(lcampo))
					cv.line((float(cb9.split('|')[0])-2), float(ccampo), (float(cb9.split('|')[0])-2), float(lcampo))
					cv.line((float(cb10.split('|')[0])-2), float(ccampo),(float(cb10.split('|')[0])-2), float(lcampo))

				if __id == "04":

					cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float(lcampo))
					cv.line((float(cb6.split('|')[0])-2), float(ccampo), (float(cb6.split('|')[0])-2), float(lcampo))
					cv.line((float(cb7.split('|')[0])-2), float(ccampo), (float(cb7.split('|')[0])-2), float(lcampo))

				#-----: Linha Final
				cv.line(20,float(lcampo),820,float(lcampo))


			if __id == "03":
				
				"""  Verifica se Tem Lancamentos disponives acima de 10 p/imprimir na ultima pagina   """
				if ( len(__pc) - ordems ) > 10:
					
					cv.setFont('Helvetica-Bold', 9)
					cv.drawString(650,500,"{ Total das Contas } ")	
					cv.drawString(650,480,"Ativo:")
					cv.drawString(650,470,"Passivo:")	
					cv.drawString(650,460,"Receitas:")	
					cv.drawString(650,450,"Despesas:")	

					cv.drawRightString(773, 480, vlcnT1 )	
					cv.drawRightString(773, 470, vlcnT2 )	
					cv.drawRightString(773, 460, vlcnT3 )	
					cv.drawRightString(773, 450, vlcnT4 )
					
					cv.rect(645,445,130,70)
					cv.line(645,488,775,488)
					cv.line(645,478,775,478)
					cv.line(645,468,775,468)
					cv.line(645,458,775,458)

		def cabExtrato():

			cv.setFont('Helvetica-Bold', 7)
			cv.setFillColor(HexColor('0x000000'))

			cv.drawString(22,  515,"Filial")
			cv.drawString(55,  515,"Nº Controle")
			cv.drawString(120, 515,"Nº NF")
			cv.drawRightString(240, 515,"Nº Duplicata")
			cv.drawString(250, 515,"Lançamento")
			cv.drawString(300, 515,"Vencimento")
			cv.drawRightString(400, 515,"Valor Apagar")
			cv.drawString(410, 515,"Pagamento")
			cv.drawRightString(510, 515,"Valor Pago")
			cv.drawRightString(580, 515,"Saldo Apagar")
			cv.drawRightString(735, float(lcampo),"Juros" )
			cv.drawRightString(815, float(lcampo),"Descontos" )

		#----------------------------: Emissao do Relatorio :-----------------------------:
		qTregs = par.APAContas.GetItemCount()
		vlcnT1 = vlcnT2 = vlcnT3 = vlcnT4 = ""
		
		if __id == "03":
			
			qTregs = len( __pc )
			for rr in __pc:
				
				rrCon = rr.split('|')
				
				if rrCon[0] == "1" and rrCon[1].split(" ")[0] == "1" :	vlcnT1 = rrCon[2]
				if rrCon[0] == "1" and rrCon[1].split(" ")[0] == "2" :	vlcnT2 = rrCon[2]	
				if rrCon[0] == "1" and rrCon[1].split(" ")[0] == "3" :	vlcnT3 = rrCon[2]
				if rrCon[0] == "1" and rrCon[1].split(" ")[0] == "4" :	vlcnT4 = rrCon[2]

		self.T = truncagem()
		ordems = 1
		Tcab = True
		if __id == "04" and par.flAnali.GetValue() == True:	Tcab = False
		if par.extrato.GetValue():	Tcab = False

		if qTregs	!=0:

			cIni = datetime.datetime.strptime(_di.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			cFim = datetime.datetime.strptime(_df.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			
			dh  = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
			pg  = 1

			if __id == "01":	nomeArquivo = diretorios.usPasta+"apagar_"+login.usalogin.lower()+".pdf"
			if __id == "02":	nomeArquivo = diretorios.usPasta+"pagas_"+login.usalogin.lower()+".pdf"
			if __id == "03":	nomeArquivo = diretorios.usPasta+"planos_"+login.usalogin.lower()+".pdf"
			if __id == "04":	nomeArquivo = diretorios.usPasta+"fluxos_"+login.usalogin.lower()+".pdf"
			
			cv = canvas.Canvas(nomeArquivo, pagesize=landscape(A4))
			cabccnf(False)
			
			lcampo = 515
			ccampo = 525
			linhas = 1
	
			if par.extrato.GetValue():

				cabExtrato()

				linhas +=1
				lcampo -= 10
			
			if __id == "01":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Contas Apagar)|'
			if __id == "02":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Contas Pagas)|'
			if __id == "03":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Plano de Contas)|'
			if __id == "04":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Fluxo de Caixa)|'

			_mensagem = mens.showmsg("Contas Apagar-Pagas, Montando Relatório!!\n.\nAguarde...")

			if __id == "03":
				

				"""
				
					Relatorio de Planos de Contas analitico
					
				"""
				if par.plAnali.GetValue() == True:
					
					ToTalConTa = Decimal('0.00')
					for r in __pc:
						
						rCon = r.split('|')
						ToTalConTa += Decimal( rCon[3].replace(",","") )
						
					cv.drawString(60, float(lcampo),par.slplcon.GetValue().strip())
					cv.drawRightString(625, float(lcampo),format( ToTalConTa,',' ) )
					lcampo = 505
				
				for r in __pc:
				
					rCon = r.split('|')
					Tabu = 60
					if rCon[0] == "2":	Tabu = 80	
					if rCon[0] == "3":	Tabu = 100	
					if rCon[0] == "4":	Tabu = 120

					if rCon[0] == "1":	cv.setFont('Helvetica-Bold', 9)
					else:	cv.setFont('Helvetica', 9)
					
					"""
					
						Relatorio de Planos de Contas analitico
						
					"""
					if par.plAnali.GetValue() == True:

						cv.drawString(25,   float(lcampo),str( ordems ).zfill(4))	
						cv.drawString(( 60 + ( len(rCon[0].split(".")) *10) ), float(lcampo),rCon[0])	
						cv.drawString( 200, float(lcampo),rCon[1] )
						cv.setFont('Helvetica', 7)
						cv.drawString( 300, float(lcampo),rCon[2] )
						cv.setFont('Helvetica', 9)
						cv.drawRightString(625, float(lcampo),rCon[3])

						if rCon[3] != "":

							cv.line(20,( lcampo -2 ),628,( lcampo -2 ))
							if linhas == 1:	cv.line(20,( lcampo +10 ),628,( lcampo +10 ))
							else:	cv.line(20,( lcampo +8 ),628,( lcampo +8 ))

					
					else:

						if len( rCon[1].split(".") ) == 2:	cv.setFillColor(HexColor('0xA52A2A'))
						cv.drawString(25,   float(lcampo),str( ordems ).zfill(4))	
						cv.drawString(Tabu, float(lcampo),rCon[1])	
						cv.drawRightString(625, float(lcampo),rCon[2])	

						if rCon[2] != "":

							cv.line(20,( lcampo -2 ),628,( lcampo -2 ))
							if linhas == 1:	cv.line(20,( lcampo +10 ),628,( lcampo +10 ))
							else:	cv.line(20,( lcampo +8 ),628,( lcampo +8 ))

						if rCon[0] == "1":
							
							cv.setFillGray(0.1,0.1) 
							if linhas == 1:	cv.rect(20,( lcampo - 2 ),608,12, fill=1) #--: Fundo do cabecalho
							else:	cv.rect(20,( lcampo - 2 ),608,10, fill=1) #--: Fundo do cabecalho
						
						
					cv.setFillColor(HexColor('0x000000'))

					ordems +=1
					linhas +=1
					lcampo -= 10

					if linhas >= 48:

						cabccnf(True)
						mdl.rodape(cv,rd1,'','','','','','','','',6)

						pg +=1
						cv.addPageLabel(pg)
						cv.showPage()						
						linhas = 1
						lcampo = 515
						ccampo = 525
							
						cabccnf(False)

			elif __id == "04":
				
				rNg = par.APAContas.GetItemCount()
				for i in range( rNg ):
					
					_ord = par.APAContas.GetItem(i, 0).GetText()
					_dTa = par.APAContas.GetItem(i, 1).GetText()
					_vRc = par.APAContas.GetItem(i, 2).GetText()
					_vAp = par.APAContas.GetItem(i, 3).GetText()
					_sAR = par.APAContas.GetItem(i, 4).GetText()
					_sal = par.APAContas.GetItem(i, 5).GetText()
					_lsT = par.APAContas.GetItem(i, 6).GetText()
					_qRR = par.APAContas.GetItem(i, 7).GetText()
					_qRA = par.APAContas.GetItem(i, 8).GetText()
					_dia = par.APAContas.GetItem(i, 9).GetText()
					_con = par.APAContas.GetItem(i,10).GetText()
					_com = par.APAContas.GetItem(i,11).GetText()

					_sRA = self.T.trunca(3, Decimal( _vRc.replace(",","") ) - Decimal( _vAp.replace(",","") ) )
					cv.setFont('Helvetica-Bold', 9)
					cv.setFillColor(HexColor('0x000000'))
					cv.drawString(25,  float(lcampo),_ord)	

					cv.setFont('Helvetica', 6)
					cv.setFillColor(HexColor('0x7F7F7F'))
					cv.drawString(55, float(lcampo),  '{ '+_dia +' }' )

					cv.setFont('Helvetica-Bold', 9)
					cv.setFillColor(HexColor('0x000000'))
					cv.drawString(100, float(lcampo),_dTa)
					
					if Decimal( _vRc.replace(",","") ) > Decimal( _vAp.replace(",","") ):	cv.setFillColor(HexColor('0x0000FF'))
						
					if Decimal( _vRc.replace(",","") ) > 0:	cv.drawRightString(245, float(lcampo),_vRc)
					if Decimal( _com.replace(",","") ) > 0 and par.comband.GetValue() == True:
						
						cv.setFont('Helvetica', 5)
						cv.setFillColor(HexColor('0xA52A2A'))
						cv.drawRightString(180, float(lcampo+4), "{ Comissão }")
						cv.drawRightString(180, float(lcampo-1), '('+_com+')')
						cv.setFont('Helvetica-Bold', 9)
					
					cv.setFillColor(HexColor('0x000000'))

					if Decimal( _vAp.replace(",","") ) > 0:	cv.drawRightString(345, float(lcampo),_vAp)

					cv.setFont('Helvetica-Bold', 8.5)
					if _sRA < 0:	cv.setFillColor(HexColor('0x812727'))
					else:	cv.setFillColor(HexColor('0x0000FF'))
					if _sRA !=0:	cv.drawRightString(445, float(lcampo), '('+format( _sRA,',')+')' if _sRA < 0 else format( _sRA,',') )
					
					cv.setFillColor(HexColor('0x000000'))
					if Decimal( _sal.replace(",","") ) < 0:	cv.setFillColor(HexColor('0x812727'))
					if Decimal( _sal.replace(",","") ) !=0: cv.drawRightString(545, float(lcampo), "("+format( Decimal(_sal.replace(",","")) ,"," )+')' if Decimal(_sal.replace(",","") ) < 0 else format( Decimal(_sal.replace(",","")), ',' ) )


					"""    So mostra o valor diario de fluxo de caixa p/dias contabilizados    """
					if Decimal( par.fluxoCaixa.GetValue() ) > 0 and _con.strip() == "" :

						cv.setFillColor(HexColor('0x7F7F7F'))
						cv.setFont('Helvetica-Bold', 4.5)
						if Decimal( par.fluxoCaixa.GetValue() ) > 0:	cv.drawRightString(480,  float(lcampo-1), str( self.T.trunca(3, Decimal( par.fluxoCaixa.GetValue() ) ) )+'+{C}' )	
						cv.setFillColor(HexColor('0x000000'))

					"""   Saldo Receber - Apagar   """
					cv.setFillColor(HexColor('0x7F7F7F'))
					cv.setFont('Helvetica', 6)
					if Decimal( _sAR.replace(",","") ) < 0 or Decimal( _sal.replace(",","") ) < 0:	cv.drawString(552,  float(lcampo),"Fechamento Negativo")
					if _con !="":	cv.drawString(652,  float(lcampo),'{'+ _con +'}' )
					
					if par.flAnali.GetValue() == False:
						
						if linhas == 1:	cv.line(20,( lcampo +10 ),820,( lcampo +10 ))
						else:	cv.line(20,( lcampo +8 ),820,( lcampo +8 ))

					
					linhas +=1
					lcampo -= 10
					
					if par.flAnali.GetValue() == True:

						if linhas == 2:	cv.line(20,( lcampo +8 ),820,( lcampo +8 ))
						else:
							cv.line(20,( lcampo+18 ),820,( lcampo+18 ))
							cv.line(20,( lcampo +8 ),820,( lcampo +8 ))
					
					nIndice = 0
					if par.flAnali.GetValue() == True and _lsT !="":

						cv.setFont('Helvetica-Bold', 8)
						cv.setFillColor(HexColor('0x7F7F7F'))
						cv.drawString(50,  float(lcampo),"TipoConta")	
						cv.drawString(100, float(lcampo),"Descrição do Credor-Cliente")	
						cv.drawRightString(560, float(lcampo),"Documento-Duplicata")
						cv.drawRightString(660, float(lcampo),"Valor")
						cv.drawString(670, float(lcampo),"Forma Recebimento-Pagamento")	

						linhas +=1
						lcampo -= 10

						for l in _lsT.split("\n"):
								
							if l !="":
									
								lsT = l.split(";")
								Tra = "Receber"
								if lsT[0] == "A":	Tra = "Apagar"

								cv.setFont('Helvetica', 9)
								cv.setFillColor(HexColor('0x4D4D4D'))
								if lsT[0] == "A":	cv.setFillColor(HexColor('0x812727'))
								cv.drawString(50,  float(lcampo),Tra)	
								cv.drawString(100, float(lcampo),str( lsT[1] ))	
								cv.drawRightString(560, float(lcampo),str( lsT[2] )+"-"+str( lsT[3] ))
								cv.drawRightString(660, float(lcampo),format( Decimal( lsT[4] ),',' ))
								cv.drawString(670, float(lcampo),str( lsT[5] ))	
								cv.setFillColor(HexColor('0x000000'))	
									
								nIndice +=1

								linhas +=1
								lcampo -= 10

								if linhas >= 48:

									cabccnf( Tcab )
									mdl.rodape(cv,rd1,'','','','','','','','',6)

									pg +=1
									cv.addPageLabel(pg)
									cv.showPage()						
									linhas = 1
									lcampo = 515
									ccampo = 525
										
									cabccnf(False)

									cv.setFont('Helvetica-Bold', 8)
									cv.setFillColor(HexColor('0x7F7F7F'))
									cv.drawString(50,  float(lcampo),"TipoConta")	
									cv.drawString(100, float(lcampo),"Descrição do Credor-Cliente")	
									cv.drawRightString(560, float(lcampo),"Documento-Duplicata")
									cv.drawRightString(660, float(lcampo),"Valor")
									cv.drawString(670, float(lcampo),"Forma Recebimento-Pagamento")	
									linhas +=1
									lcampo -= 10
					
					if linhas >= 47:

						cabccnf( Tcab )
						mdl.rodape(cv,rd1,'','','','','','','','',6)

						pg +=1
						cv.addPageLabel(pg)
						cv.showPage()						
						linhas = 1
						lcampo = 515
						ccampo = 525
										
						cabccnf(False)
				cv.line(20,( lcampo +8 ),820,( lcampo +8 ))
				
			else:

				__nReg = par.APAContas.GetItemCount()
				vlr = jur = des = Decimal('0.00')
				
				for r in range(__nReg):

					if par.extrato.GetValue():
				
						cv.setFillColor(HexColor('0x4D4D4D'))
						rel = par.APAContas.GetItem(r, 16).GetText().split('|') if __id == "01" else par.APAContas.GetItem(r, 18).GetText().split('|')
						cv.setFont('Helvetica', 8)
						cv.drawString(22,  float(lcampo),rel[0])
						cv.drawString(55,  float(lcampo),rel[1])
						cv.drawString(120, float(lcampo),rel[2])
						cv.drawRightString(240, float(lcampo),rel[3])
						cv.drawString(250, float(lcampo),rel[4])
						cv.drawString(300, float(lcampo),rel[5])
						cv.drawRightString(400, float(lcampo),rel[6])
						cv.drawString(410, float(lcampo),rel[7])
						if Decimal( rel[8].replace(',','') ):	cv.drawRightString(510, float(lcampo),rel[8])
						if Decimal( rel[9].replace(',','') ):	cv.drawRightString(580, float(lcampo),rel[9])
						if Decimal( rel[10].replace(',','') ):	cv.drawRightString(735, float(lcampo),rel[10] )
						if Decimal( rel[11].replace(',','') ):	cv.drawRightString(815, float(lcampo),rel[11] )
						
					else:
						_rel = par.APAContas.GetItem(r, 13).GetText().split('|')
						_emi = _rel[2]+" "+_rel[4]
						_ven = _rel[5]
						_pag = _rel[8]+" "+_rel[11]
							
						cv.setFont('Helvetica', 8)
						cv.drawString(22, float(lcampo),_rel[12])

						if __id !="02":
							
							cv.drawRightString(124, float(lcampo),_rel[1]+"-"+_rel[6])
							cv.drawString(130,float(lcampo),_emi)
							cv.drawString(290,float(lcampo),_ven)

						if __id == "02":
							
							vlr +=Decimal( _rel[10].replace(',','') )
							jur +=Decimal( _rel[17].replace(',','') )
							des +=Decimal( _rel[18].replace(',','') )
							
						else:	vlr +=Decimal( _rel[7].replace(',','') )
						
						"""   Contas Apagar    """
						if __id == "01":

							if _rel[13]!='':	cv.drawImage(ImageReader("imagens/confere.png"), 410,float(lcampo), width=5, height=5)
							cv.drawRightString(405, float(lcampo),format( Decimal(_rel[7]) ,',') )
					
							if _rel[13]!='':	cv.setFillColor(HexColor('0x125712'))
							cv.drawRightString(455,float(lcampo),_rel[14])
							cv.drawString(460,float(lcampo),_rel[0])
					
							if _rel[15].strip() !="" or _rel[16].strip() !="":

								linhas +=1
								lcampo -= 10
								
								__dp = __nf = __ch = ""
								if _rel[15] !="":	__dp = u"Nº Duplicata: "+ _rel[15] +"  "
								if _rel[16] !="":	__ch = _rel[16]
								
								cv.drawString(460,float(lcampo), __dp+__ch)


							ToTaliza = False
							if r  == ( __nReg -1 ):	ToTaliza = True
							else:

								if par.APAContas.GetItem(r+1, 13).GetText().split('|')[5] != par.APAContas.GetItem(r, 13).GetText().split('|')[5]:	ToTaliza = True
								
							if ToTaliza == True:

								cv.setFont('Helvetica-Bold', 6)
								cv.drawString(290,float(lcampo),"Total-"+_ven)

								cv.setFont('Helvetica-Bold', 8)
								cv.drawRightString(405,float(lcampo), format( vlr,',' ) )
								cv.setFont('Helvetica', 8)
								
								vlr = Decimal("0.00")
								
							cv.setFillColor(HexColor('0x000000'))
							
						"""   Contas Pagas   """
						if __id == "02":
							
							cv.drawRightString(124, float(lcampo),_rel[1]+"-"+_rel[6])
							cv.drawRightString(195, float(lcampo),_rel[15])
							cv.drawString(200,float(lcampo),_emi)
							cv.drawString(290,float(lcampo),_ven)

							cv.drawString(335,float(lcampo),_pag)

							cv.setFont('Helvetica', 7)
							if _rel[17] and Decimal( _rel[17].replace(',','') ):	cv.drawRightString(464, float(lcampo),_rel[17])
							if _rel[18] and Decimal( _rel[18].replace(',','') ):	cv.drawRightString(499, float(lcampo),_rel[18])
							cv.setFont('Helvetica', 8)

							cv.drawRightString(550, float(lcampo),format(Decimal(_rel[10]),','))

							cv.setFont('Helvetica', 7)
							cv.drawString(555,float(lcampo),_rel[0][:80])
							cv.setFont('Helvetica', 8)

							ToTaliza = False

							if r  == ( __nReg -1 ):	ToTaliza = True
							else:

								if par.APAContas.GetItem(r+1, 13).GetText().split('|')[8] != par.APAContas.GetItem(r, 13).GetText().split('|')[8]:	ToTaliza = True
																
							if ToTaliza == True:

								linhas +=1
								lcampo -= 10

								cv.setFont('Helvetica-Bold', 6)
								cv.drawString(335,float(lcampo),"Total-"+_rel[8])

								if jur !=0:	cv.drawRightString(464,float(lcampo), format( jur,',' ) )
								if des !=0:	cv.drawRightString(499,float(lcampo), format( des,',' ) )

								cv.setFont('Helvetica-Bold', 8)
								cv.drawRightString(550,float(lcampo), format( vlr,',' ) )
								cv.setFont('Helvetica', 8)
								
								vlr = jur = des = Decimal("0.00")
								
							cv.setFillColor(HexColor('0x000000'))

					linhas +=1
					lcampo -= 10

					if linhas >= 47:

						cabccnf(True) if not par.extrato.GetValue() else cabccnf( False )
						mdl.rodape(cv,rd1,'','','','','','','','',6)

						pg +=1
						cv.addPageLabel(pg)
						cv.showPage()						
						linhas = 1
						lcampo = 515
						ccampo = 525
							
						cabccnf(False)

						if par.extrato.GetValue():

							cabExtrato()

							linhas +=1
							lcampo -= 10

					else:
						
						if r+1 != __nReg and not par.extrato.GetValue():

							if __id == "02" and linhas !=1:	cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))
							else:	cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))
		
			cabccnf( Tcab )
			if par.extrato.GetValue() and linhas < 47:	cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))
			
			mdl.rodape(cv,rd1,'','','','','','','','',6)
			cv.save()

			del _mensagem
			
			gerenciador.TIPORL = ''
			gerenciador.Anexar = nomeArquivo
			gerenciador.imprimir = True
			gerenciador.Filial   = Filial
				
			ger_frame=gerenciador(parent=par,id=-1)
			ger_frame.Centre()
			ger_frame.Show()

""" Contas Apagar """
class RelatoriosProdutos:
	
	def rldiversos( self, mdl, par, _di, _df, __id, Filiais = False, Filial = "" ):

		carga = False
		def cabecalho_segundo():

			cv.setFillColor(HexColor('0x000000'))
			cv.setFont('Helvetica-Bold', 6)
			cv.drawString(22,  float(lcampo), "Codigo")
			if par.anacum.GetValue():	cv.drawString(100, float(lcampo), "QT DAV - Descrição dos produtos")
			else:	cv.drawString(100, float(lcampo), "Nº DAV - Descrição dos produtos")
			cv.drawString(400, float(lcampo), "Fabricante")
			cv.drawString(460, float(lcampo), "Grupo")
			cv.drawString(520, float(lcampo), "Sub-Grupo_1")
			cv.drawString(580, float(lcampo), "Sub-Grupo_2")
			cv.drawString(640, float(lcampo), "Quantidade")
			cv.drawString(680, float(lcampo), "Vlr Unitario")
			cv.drawString(728, float(lcampo), "Vlr Total")
			cv.drawString(770, float(lcampo), "Comissão [ $-% ]")

				
		def cabccnf(_separa):


			""" Cabecalho """
			pag = str(pg).zfill(3)
			__rel = ""

			if __id == "01":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"Inventario Estoque",2)
			if __id == "02":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"ESTOQUE ZERO",2)
			if __id == "03":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"ESTOQUE NEGATIVO",2)
			if __id == "04":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"RESERVA LOCAL",2)
			if __id == "05":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"TOTALIZA PRODUTO",2)
			if __id == "06":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"ESTOQUE MÌNIMO",2)
			if __id == "07":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"GIRO DE PRODUTOS",2)
			if __id == "08":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"FICHA DE ESTOQUE",2)
			if __id == "11":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"TABELA DE PREÇOS",2)
			if __id == "12":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"Contagem Estoque",2)
			if __id == "13":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"COMPRAS",2)
			if __id == "15":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"Entrega Entre Filiais",2)
			if __id == "16":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"Compras p/Produtos",2)
			if __id == "17":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"Produtos Vendidos",2)
			if __id == "18":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"Unidade Manejo",2)
			if __id == "19":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"Produtos sem Giro",2)
			if __id == "20":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"Auxiliar compras",2)
			if __id == "22":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"Estoque local",2)

			if __id ==  "900":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"EXPEDIÇÂO",2)

			if __id == "05":

				cv.setFillColor(HexColor('0x0000FF'))
				cv.setFont('Helvetica', 8)

				cv.drawString(155,33,"Quantidade de Venda:")
				cv.drawString(155,23,"Quantidade de Devolução:")
				cv.drawString(320,23,"Saldo:")
				cv.drawRightString(310, 33,format(par.QTVenda,','))
				cv.drawRightString(310, 23,format(par.QTDevol,','))
				cv.drawRightString(410, 23,format(par.SaldoQT,','))

				cv.setFillColor(HexColor('0x000000'))
				cv.drawString(420,33,"Valor de Venda:")
				cv.drawString(420,23,"Valor de Devolução:")
				cv.drawString(570,23,"Saldo:")

				cv.drawRightString(560, 33,format(par.VVVenda,','))
				cv.drawRightString(560, 23,format(par.VDDevol,','))
				cv.drawRightString(650, 23,format(par.SaldoVD,','))
				cv.setFillColor(HexColor('0x000000'))

				cv.setFillColor(HexColor('0xA52A2A'))
				cv.drawString(570,33,"Desconto de vendas:")
				cv.drawString(695,33,"Desconto de devolução:")
				cv.drawRightString(692, 33,format(par.saldoDV,','))
				cv.drawRightString(818, 33,format(par.saldoDD,','))

				cv.setFillColor(HexColor('0x000000'))

			else:

				if __id not in ["900","06","07","08","11","12","13","15","16","17","18","19","20","22"]:
					
					cv.setFillColor(HexColor('0x636363'))
					cv.drawString(155,33,"01-Valor de Compra:")
					cv.drawString(155,23,"02-Valor de Custo:")
					cv.drawRightString(320, 33,format(par._sTTcp,','))
					cv.drawRightString(320, 23,format(par._sTTcu,','))

					cv.drawString(330,33,"03-Valor de Venda:")
					cv.drawString(330,23,"04-Valor do Custo Médio:")
					cv.drawRightString(510, 33,format(par._sTTvd,','))
					cv.drawRightString(510, 23,format(par._sTTcm,','))

				if __id == "08" or __id == "22":

					cv.setFillColor(HexColor('0x636363'))
					cv.drawString(185,33,"Entrada:")
					cv.drawString(185,23,"Saida:")
					if __id == "22":	cv.drawString(285,23,"Saldo:")
					
					cv.drawRightString(260, 33,format(par.entrada,','))
					cv.drawRightString(260, 23,format(par.saidasm,','))
					if __id == "22":	cv.drawRightString(365, 23,format( ( par.entrada - par.saidasm ),','))

				if __id == "13":

					cv.setFillColor(HexColor('0x1A1A1A'))
					cv.drawString(155,33,"Total Produtos:")
					cv.drawString(155,23,"Total Nota:")
					cv.drawString(290,33,"Valor ST:")
					cv.drawString(290,23,"Valor Frete:")
					cv.drawString(400,33,"Valor Seguro:")
					cv.drawString(400,23,"Outras Despesas:")

					cv.drawString(520,33,"IPI:")
					cv.drawString(520,23,"IPI Avulso:")
					cv.drawString(615,33,"ST Avulso:")

					if par.fixData.GetValue():

						cv.setFillColor(HexColor('0x0D0D87'))
						cv.drawString(615,23,"Compras:")
						cv.drawString(720,33,"Apagar:")
						cv.drawString(720,23,"Saldo:")
						cv.drawRightString(710, 23,format(par.vcp,','))
						cv.drawRightString(815, 33,format(par.vap,','))
						cv.drawRightString(815, 23,format(par.sac,','))

					cv.setFillColor(HexColor('0x000000'))

					cv.drawRightString(280, 33,format(par.vlp,','))
					cv.drawRightString(280, 23,format(par.vnf,','))

					if Decimal( par.vsT ) !=0:	cv.drawRightString(390, 33,format(par.vsT,','))
					if Decimal( par.vfr ) !=0:	cv.drawRightString(390, 23,format(par.vfr,','))

					if Decimal( par.vsg ) !=0:	cv.drawRightString(520, 33,format(par.vsg,','))
					if Decimal( par.vod ) !=0:	cv.drawRightString(520, 23,format(par.vod,','))

					if Decimal( par.ipi ) !=0:	cv.drawRightString(695, 33,format(par.ipi,','))
					if Decimal( par.ipa ) !=0:	cv.drawRightString(695, 23,format(par.ipa,','))
					if Decimal( par.sta ) !=0:	cv.drawRightString(710, 33,format(par.sta,','))
					
					cv.setFillColor(HexColor('0x3131B8'))
					cv.drawString(300,527,"Descirção do Representante")
					if par.fixData.GetValue():	cv.drawRightString(672, 527,"Partilha manejo-extrator" )
					cv.drawString(675,527,"Valor Frete")
					cv.drawString(725,527,"Valor Seguro")
					cv.setFont('Helvetica', 5.7)
					cv.drawString(775,527,"Outras Despesas")
					cv.setFont('Helvetica', 7)
					cv.setFillColor(HexColor('0x000000'))

				if __id == "17":

					cv.setFillColor(HexColor('0x636363'))
					cv.drawString(185,33,"Quantidade vendida:")
					cv.drawString(218,23,"Descontos:")
					cv.drawString(350,33,"Valor total do custo:")
					cv.drawString(350,23,"Valor total de venda:")
					cv.drawString(515,33,"Margem de lucro:")
					cv.drawString(515,23,"Media descontos:")

					margem_lucro = format( ( ( par._sTTvd - par._sTTcu ) / par._sTTcu * 100 ),'.4f' ) if par._sTTvd and par._sTTcu else "0.0000"
					margem_desco = format( (  par.saidasm / par._sTTvd * 100 ),'.4f' ) if par._sTTvd and par.saidasm else "0.000"
					cv.drawRightString(340, 33,format(par.QTVenda,','))
					cv.drawRightString(340, 23,format(par.saidasm,',')) #-: Desconto
					cv.drawRightString(505, 33,format(par._sTTcu,','))
					cv.drawRightString(505, 23,format(par._sTTvd,','))
					cv.drawRightString(635, 33, margem_lucro+" %" )
					cv.drawRightString(635, 23, margem_desco+" %" )

				if __id == "18":

					cv.setFillColor(HexColor('0x636363'))
					cv.drawString(185,33,"Quantidade:")
					cv.drawRightString(385,33,"Valor total do extrator")
					cv.drawRightString(485,33,"Valor total do fornecedor")

					cv.drawRightString(277,33,format(par.r18qt,','))
					cv.setFont('Helvetica-Bold',8)
					cv.drawRightString(385,23, format( Decimal( format(par.r18vt,'.2f') ), ',' ) )
					cv.drawRightString(485,23, format( Decimal( format(par.r18pc,'.2f') ), ',' ) )

				if __id in ["19","20"]:

					cv.setFillColor(HexColor('0x636363'))
					cv.drawRightString(385,33,u"Preço de custo: Valor total:")
					cv.drawRightString(385,23,u"Preço de venda: Valor total:")

					cv.setFont('Helvetica-Bold',8)
					cv.drawRightString(480,33, format( Decimal( format(par._sTTcu,'.2f') ), ',' ) )
					cv.drawRightString(480,23, format( Decimal( format(par._sTTvd,'.2f') ), ',' ) )

			if __id == "900":

				cv.setFont('Helvetica-Bold',9)
				cv.setFillColor(HexColor('0x3131B8'))
				cv.drawString(22, 55, u"Previsão de Entrega: "+format( par.rroma[0][22],'%d/%m/%Y' ) )
				cv.drawString(22, 45, "Transportadora: ")
				cv.drawString(114,45, str( par.rroma[0][23]) )
				cv.setFont('Helvetica-Bold',8)
				cv.drawString(500,55,"Fechamento: "+format( par.rroma[0][6],'%d/%m/%Y' )+" "+str( par.rroma[0][7] )+" "+str( par.rroma[0][8] )+"   Placa: "+str( par.rroma[0][19] ) )
				cv.drawString(500,45,"Romaneio....: "+str( par.rroma[0][1] )+"   Motorista: "+str( par.rroma[0][18].upper() ) )

			""" Titulo de Cabecalho """
			cb1= cb2= cb3= cb4= cb5= cb6= cb7= cb8= cb9= cb10= cb11= cb12=''
			if self.A == False and __id !="900" and par.selecao.GetValue() !='':

				_Tipo = par.selecao.GetValue()
				if par.pTodos.GetValue() == True:	_Tipo = "Geral: "+_Tipo
				if par.pGrupo.GetValue() == True:	_Tipo = "Grupo: "+_Tipo
				if par.psGru1.GetValue() == True:	_Tipo = "Sub-Grupo 1: "+_Tipo
				if par.psGru2.GetValue() == True:	_Tipo = "Sub-Grupo 2: "+_Tipo
				if par.pFabri.GetValue() == True:	_Tipo = "Fabricante: "+_Tipo
				if par.pEnder.GetValue() == True:	_Tipo = u"Endereço: "+_Tipo
			
			else:	_Tipo = ""
			if  __id == "900":	_Tipo = "Romaneio de Entrega"
			if self.A == False and __id != "900":
				
				if par.produT.GetValue() == True or __id == "08":	_Tipo = "{ Produto }"
				if par.produT.GetValue() == True and __id == "22":	_Tipo = par.pdDs.GetLabel()
			
			if __id == "16" and par.selecao.GetValue():	_Tipo = "Fabricante-Grupo: "+str( par.selecao.GetValue() )

			
			filia = ""
			if Filiais == True:	filia = "Filial: "+str( Filial )
			if   __id == "06":	rel =  u'Usuário: '+str(login.usalogin)+"  "+_Tipo+(" "*10)+Filial
			elif __id == "900":	rel =  u'Usuário: '+str(login.usalogin)+"  "+_Tipo+(" "*10)+Filial #-:expedicao
			else:	rel =  u'Usuário: '+str(login.usalogin)+u"  PERÌODO: "+cIni+" A "+cFim+(" "*5)+_Tipo+(" "*5)+Filial

			if __id == "18":
				
				if par.ordenQ.GetValue():	rel = u'Usuário: '+str(login.usalogin)+u"  PERÌODO: "+cIni+" A "+cFim+(" "*5)+_Tipo+(" "*5)+Filial+u"  { Totalizado p/produtos }"
				if par.ordenV.GetValue():	rel = u'Usuário: '+str(login.usalogin)+u"  PERÌODO: "+cIni+" A "+cFim+(" "*5)+_Tipo+(" "*5)+Filial+u"  { Totalizado p/unidade de manejo-roça }"
				if par.ordenD.GetValue():	rel = u'Usuário: '+str(login.usalogin)+u"  PERÌODO: "+cIni+" A "+cFim+(" "*5)+_Tipo+(" "*5)+Filial+"  { Totalizado p/fornecedor }"
				if par.ordenE.GetValue():	rel = u'Usuário: '+str(login.usalogin)+u"  PERÌODO: "+cIni+" A "+cFim+(" "*5)+_Tipo+(" "*5)+Filial+"  { Totalizado p/extrator }"


			__tamanho = 7
			if __id not in ["05","11","900"]:

				cb1 =  "22|540|Filial|"
				cb2 =  "50|540|Descrição dos Produtos|#7F7F7F"
				
			if __id == "01":

				cb3 = "323|540|NCM|#7F7F7F"
				cb4 = "360|540|Estoque Fisico|"
				cb5 = "420|540|Valor Compra-Total|"
				cb6 = "520|540|Valor Custo-Total|"
				cb7 = "620|540|Valor Custo Medio-Total|"
				cb8 = "720|540|Valor Venda-Total|"

			if __id in ["02","03","04"]:

				cb3  =  "300|540|Grupo|"
				cb4  =  "390|540|Sub-Grupo 1|"
				cb5  =  "480|540|Sub-Grupo 2|"
				cb6  =  "570|540|Fabricante|"
				cb7  =  "660|540|Endereço|"
				cb8  =  "705|540|Estoque Fisico|"
				cb9  =  "765|540|Reserva Local|"

			if __id=="05":

				cb1 =  "22|540|Vendedor|#7F7F7F"
				cb2 = "200|540|Quantidade de Venda||R"
				cb3 = "290|540|Quantidade de Devolução||R"
				cb4 = "380|540|Saldo||R"
				cb5 = "440|540|Valor de Venda||R"
				cb6 = "530|540|Valor de Devolução||R"
				cb7 = "620|540|Saldo||R"
				cb8 = "680|540|Média Quantidade||R"
				cb9 = "750|540|Média Valor||R"

			if __id=="06":

				cb1 =  "22|540|Filial|#7F7F7F"
				cb2 = " 50|540|Descrição dos Produtos|"
				cb3 = "390|540|Estoque Fisico|"
				cb4 = "480|540|Estoque Mínimo|"
				cb5 = "570|540|Estoque Máximo|"
				cb6 = "660|540|Sugestão|"
				cb7 = "750|540|Observação|"

			if __id=="07":

				cb1 =  "22|540|Código|#7F7F7F"
				cb2 = " 90|540|Descrição dos Produtos|#7F7F7F"
				cb3 = "380|540|QT Compra|#7F7F7F"
				cb4 = "440|540|QT Vendas|#7F7F7F"
				cb5 = "500|540|QT Devolução|#7F7F7F"
				cb6 = "560|540|Saldo Vendas|#7F7F7F"
				cb7 = "620|540|Média Compra|#008000"
				cb8 = "685|540|Média Venda|#008000"
				cb9 = "750|540|Média Marcação|#008000"

			if __id=="08":
				cb1 =  "22|540|NºDAV-Controle|#7F7F7F"
				cb2 = " 90|540|Descrição do Cliente-Fornecedor|#7F7F7F"
				cb3 = "300|540|Emissão|#7F7F7F"
				cb4 = "440|540|Estoque Anterior|#7F7F7F"
				cb5 = "500|540|Entrada|#1212DA"
				cb6 = "560|540|Saida|#C20B0B"
				cb7 = "620|540||#008000"
				cb8 = "685|540|Histórico|#0B710B"

				cv.setFillColor(HexColor('0x1212DA'))
				cv.drawString(620, 540,"Sal")
				cv.setFillColor(HexColor('0xC20B0B'))
				cv.drawString(632, 540,"do")
				cv.setFillColor(HexColor('0x000000'))

			if __id=="11":

				cb1 =  "22|540|Filial|#7F7F7F"
				cb2 = " 50|540|Código|"
				cb3 = "120|540|Descrição dos Produtos|"
				cb4 = "380|540|Grupo|"
				cb5 = "480|540|Fabricante|"
				cb6 = "580|540|Tabela_1|"
				cb7 = "620|540|Tabela_2|"
				cb8 = "660|540|Tabela_3|"
				cb9 = "700|540|Tabela_4|"
				cb10= "740|540|Tabela_5|"
				cb11= "780|540|Tabela_6|"

			if __id=="12":

				cb1 =  "22|540|Filial|#7F7F7F"
				cb2 = " 50|540|Código|"
				cb3 = "120|540|Código Barras|"
				cb4 = "190|540|Referência|"
				cb5 = "260|540|Código Interno|"
				cb6 = "340|540|Descrição dos Produtos|"
				if not par.pEnder.GetValue():	cb6 = "340|540|Descrição dos Produtos"+(" "*105)+"Endereço|"
				cb7 = "660|540|EstoqueFisico UN|"
				cb8 = "740|540|<===>|"
				if par.pTodos.GetValue() == True:	cb8 = "740|540|Geral|"
				if par.pGrupo.GetValue() == True:	cb8 = "740|540|Grupo|"
				if par.psGru1.GetValue() == True:	cb8 = "740|540|Sub-Grupo 1|"
				if par.psGru2.GetValue() == True:	cb8 = "740|540|Sub-Grupo 2|"
				if par.pFabri.GetValue() == True:	cb8 = "740|540|Fabricante|"
				if par.pEnder.GetValue() == True:	cb8 = "740|540|Endereço|"

			if __id=="13":

				cb1 =  "22|540|Filial|#7F7F7F"
				cb2 = " 50|540|Nº Controle|"
				cb3 = "100|540|Nº NotaFiscal|"
				cb4 = "150|540|Compra-Lançamento|"
				cb5 = "300|540|Descrição do Fornecedor|"
				cb6 = "675|540|Total Produtos|"
				cb7 = "725|540|Total Nota|"
				cb8 = "775|540|Valor ST|"

			if __id=="15":

				cb1 =  "22|540|Nº DAV|#7F7F7F"
				cb2 = " 80|540|Emissao|#7F7F7F"
				cb3 = "200|540|Descrição dos produtos|"
				cb4 = "480|540|QT Anterior|"
				cb5 = "540|540|QT Entregue|"
				cb6 = "600|540|Filiais|"
				cb7 = "668|540|Portador|"

			if __id=="16":

				cb2 = " 50|540|Nº Controle|#7F7F7F"
				cb3 = "100|540|Lançamento|"
				cb4 = "230|540|Codigo|"
				cb5 = "310|540|Descrição dos produtos|"
				cb6 = "600|540|QT.Compra|"
				cb7 = "643|540|Vl.Unitario|"
				cb8 = "683|540|Vl.Compra|"

			if __id=="17":

				cb1 = " 22|540|Nº DAVS|#7F7F7F"
				cb2 = " 50|540|Codigo||R"
				cb3 = "132|540|Descrição dos produtos|"
				cb4 = "480|540|QT vendida||R"
				cb5 = "540|540|Total custo||R"
				cb6 = "610|540|Total vendas||R"
				cb7 = "680|540|Margem lucro||R"
				cb8 = "750|540|"+(" "*11)+"Desconto $-%|#7F7F7F"

			if __id=="18":

				__tamanho = 6

				if par.ordenQ.GetValue():

					cb1 = " 22|540|Nº+Controle|#7F7F7F"
					cb2 = " 65|540|Filial|"
					cb3 = " 95|540|Laçamento|"
					cb4 = "167|540|Codigo|"
					cb5 = "230|540|Descrição dos produtos|"
					cb6 = "450|540|Quantidade+Compra||R"
					cb7 = "490|540|Extrator+Custo||R"
					cb8 = "520|540|Extrator+Total||R"
					cb9 = "560|540|Fornecedor+Custo||R"
					cb10= "600|540|Fornecedor+Total|"
					cb11= "640|540|Unidade de manejo-roça+Descrição fornecedor|"

					__rel = "18"

				if par.ordenV.GetValue():

					cb1 = " 22|540|Ordem|#7F7F7F"
					cb2 = " 50|540|Unidade manejo|"
					cb3 = "180|540|Laçamentos|"
					cb4 = "265|540|Extrator+Total|"
					cb5 = "318|540|Fornecedor+Total|"

					__rel = "18A"

				if par.ordenD.GetValue() or par.ordenE.GetValue():

					cb1 = " 22|540|Ordem|#7F7F7F"
					cb2 = " 50|540|Descrição do fornecedor|" if par.ordenD.GetValue() else "50|540|Descrição do extrator|"
					cb3 = "380|540|Laçamentos|"
					cb4 = "476|540|Extrator+Total|"
					cb5 = "536|540|Fornecedor+Total|"

					__rel = "18A"

			if __id=="19":

				cb1 = " 22|540|Codigo|#7F7F7F"
				cb2 = " 79|540|Descrição dos produtos  [ Clientes ]|"
				cb3 = "370|540|Ultima venda|"
				cb4 = "420|540|Fabricante|"
				cb5 = "510|540|Endereço|"
				cb6 = "600|540|Quantidade|"
				cb7 = "642|540|Custo [ Valor total ]||R"
				cb8 = "732|540|"+(" "*10)+"Venda [ Valor total ]||R"

			if __id=="20":

				cb1 = " 22|540|Codigo/Codigo interno|#7F7F7F"
				cb2 = " 79|540|Descrição dos produtos|"
				cb3 = "370|540|Fabricante|"
				cb4 = "420|540|UN|"
				cb5 = "440|540|Preço custo|"
				cb6 = "540|540|Preço venda|"
				cb7 = "640|540|Quantidade||R"
				cb8 = "732|540|Quantidade X Preço custo||R"

			if __id=="22":

				cb1 =  "22|540|Filial|#7F7F7F"
				cb2 = " 55|540|Nº DAV/Pedido||R"
				cb3 = u"145|540|Emissão||R"
				cb4 = "327|540|Entrada||R"
				cb5 = "405|540|Saida||R"
				cb6 = u"485|540|Observação|"

			if __id=="900" and carga == False:

				cb1 =  "22|540|Filial|#7F7F7F"
				cb2 = " 60|540|Nº DAV|"
				cb3 = "110|540|Descrição do Cliente|"
				cb4 = "450|540|Receber No Local|"
				cb5 = "600|540|Vendedor|"
				cb6 = "650|540|Telefone(s)|"
			
			if __id=="900" and carga == True:	cb1 = "22|540|Relação de material para separação|#7F7F7F"	
			if _separa == False:	mdl.mtitulo(rel,cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12, __tamanho, 2)
			else:
				
				if   __id == "07":	lnh = 2.7
				else:	lnh = 0
				
				cv.line((float(cb2.split('|')[0])-2), float(ccampo), (float(cb2.split('|')[0])-2), float(lcampo-lnh))
				cv.line((float(cb3.split('|')[0])-2), float(ccampo), (float(cb3.split('|')[0])-2), float(lcampo-lnh))
				if __rel == "18A":

					cv.line((float(cb4.split('|')[0])-2), float(ccampo), (float(cb4.split('|')[0])-2), float(lcampo))
					cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float(lcampo))
				
				if __id in ["01","06","11","900","15","17","19","20","22"]:

					if __id !="900":	cv.line((float(cb4.split('|')[0])-2), float(ccampo), (float(cb4.split('|')[0])-2), float(lcampo))
					cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float(lcampo))
					cv.line((float(cb6.split('|')[0])-2), float(ccampo), (float(cb6.split('|')[0])-2), float(lcampo))

					if __id != "900" and __id != "22":	cv.line((float(cb7.split('|')[0])-2), float(ccampo), (float(cb7.split('|')[0])-2), float(lcampo))
					if __id in ["01","17","19","20"]:	cv.line((float(cb8.split('|')[0])-2), float(ccampo), (float(cb8.split('|')[0])-2), float(lcampo))


					if __id =="11":
						cv.line((float(cb8.split('|')[0])-2), float(ccampo), (float(cb8.split('|')[0])-2), float(lcampo))
						cv.line((float(cb9.split('|')[0])-2), float(ccampo), (float(cb9.split('|')[0])-2), float(lcampo))
						cv.line((float(cb10.split('|')[0])-2),float(ccampo), (float(cb10.split('|')[0])-2),float(lcampo))
						cv.line((float(cb11.split('|')[0])-2),float(ccampo), (float(cb11.split('|')[0])-2),float(lcampo))

				if __id in ["02","03","04","05","07","08","12","13","16"] or __rel == "18":

					cv.line((float(cb4.split('|')[0])-2), float(ccampo), (float(cb4.split('|')[0])-2), float(lcampo-lnh))
					cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float(lcampo-lnh))
					cv.line((float(cb6.split('|')[0])-2), float(ccampo), (float(cb6.split('|')[0])-2), float(lcampo-lnh))
					cv.line((float(cb7.split('|')[0])-2), float(ccampo), (float(cb7.split('|')[0])-2), float(lcampo-lnh))
					cv.line((float(cb8.split('|')[0])-2), float(ccampo), (float(cb8.split('|')[0])-2), float(lcampo-lnh))
					if __id not in ["08","12","13","16"]:	cv.line((float(cb9.split('|')[0])-2), float(ccampo), (float(cb9.split('|')[0])-2), float(lcampo-lnh))

					if __rel == "18":
						cv.line((float(cb10.split('|')[0])-2), float(ccampo), (float(cb10.split('|')[0])-2), float(lcampo-lnh))
						cv.line((float(cb11.split('|')[0])-2), float(ccampo), (float(cb11.split('|')[0])-2), float(lcampo-lnh))

					"""   Totalizar Media Geral do Custo e de Vendas   """
					if __id == "07":
						
						_MediaMarca = Decimal("0.000")
						if _vlMVen !=0 and _vlMCus !=0:	_MediaMarca = ( ( _vlMVen - _vlMCus ) / _vlMCus * 100 )

						cv.setFont('Helvetica-Bold', 7)
						cv.setFillColor(HexColor('0x0000FF'))
						cv.drawRightString(435,527, str( _vTcompra ) )
						cv.drawRightString(495,527, str( _vTvendas ) )
						cv.drawRightString(555,527, str( _vTdevolu ) )
						cv.drawRightString(615,527, str( _vTsaldoc ) )

						cv.drawRightString(680,527, str( self.T.trunca(5,  _vlMCus ) ) )
						cv.drawRightString(745,527, str( self.T.trunca(5,  _vlMVen ) ) )
						cv.drawRightString(817,527, str( self.T.trunca(1,  _MediaMarca ) ) + "%")
						
						cv.setFillColor(HexColor('0x000000'))
						
						cv.drawString(222,35, "a-Total de vendas: ")
						cv.drawString(370,35, "b-Total de devoluções: ")
						cv.drawString(222,25, "c-Saldo de vendas: ")
						cv.drawString(370,25, "d-Saldo do custo (e-f): ")

						cv.drawString(520,35, "e-Total do custo de vendas: ")
						cv.drawString(520,25, "f-Total do custo de devoluções: ")

						cv.drawString(690,35, "g->-------->: ")
						cv.drawString(690,25, "h-Margem: ")

						cv.drawRightString(352,35, format( self.T.trunca(3,  _TTVendas ) ,',' ) )
						cv.drawRightString(500,35, format( self.T.trunca(3,  _TTDevolu ) ,',' ) )
						cv.drawRightString(500,25, format( self.T.trunca(3,  ( total_custovendas - total_custodevolu ) ) ,',' ) )
						cv.drawRightString(352,25, format( self.T.trunca(3,  ( _TTVendas - _TTDevolu ) ) ,',' ) )
						cv.drawRightString(680,35, format( self.T.trunca(3,  total_custovendas ) ,',' ) )
						cv.drawRightString(680,25, format( self.T.trunca(3,  total_custodevolu ) ,',' ) )

						final_vendas = ( _TTVendas - _TTDevolu )
						final_custos = ( total_custovendas - total_custodevolu )
						perce_custos = ( final_custos / final_vendas * 100 )
						marge_lucros = ( 100 - perce_custos )

						cv.drawRightString(780,35, format( self.T.trunca(5,  perce_custos ) ,',' )+' %' ) #-: Percentual do custo
						cv.drawRightString(780,25, format( self.T.trunca(5,  marge_lucros ) ,',' )+' %' ) #-: Margem de lucro


				#-----: Linha Final
				if __id == "07":	cv.line(20,float(lcampo-3),820,float(lcampo-3))
				else:	cv.line(20,float(lcampo),820,float(lcampo))


		#----------------------------: Emissao do Relatorio :-----------------------------:
		self.T = truncagem()
		self.A = False
		if str( _df ).upper() == "APURACAO":	self.A = True
			
		if self.A == True:
			
			indice = par.list_compra.GetFocusedItem()
			cLisTa = par.list_compra.GetItem(indice, 26).GetText().split(";")
			qLisTa = 1
			
		
		else:	
			cLisTa = par.RLTprodutos
			qLisTa = cLisTa.GetItemCount()


		if  qLisTa !=0:

			_mensagem = mens.showmsg("Produtos: Montando Relatório\nAguarde...")
			if self.A == True:	cIni,cFim = "","{ Compras }"
			
			if __id !="900" and self.A == False:	cIni = datetime.datetime.strptime(_di.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			if __id !="900" and self.A == False:	cFim = datetime.datetime.strptime(_df.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			
			dh  = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
			pg  = 1

			if __id == "01":	nomeArquivo = diretorios.usPasta+"custoEsFisico_"+login.usalogin.lower()+".pdf"
			if __id == "02":	nomeArquivo = diretorios.usPasta+"estoquezero_"+login.usalogin.lower()+".pdf"
			if __id == "03":	nomeArquivo = diretorios.usPasta+"estoquenegativo_"+login.usalogin.lower()+".pdf"
			if __id == "04":	nomeArquivo = diretorios.usPasta+"reservalocal_"+login.usalogin.lower()+".pdf"
			if __id == "05":	nomeArquivo = diretorios.usPasta+"totalizaProduto_"+login.usalogin.lower()+".pdf"
			if __id == "06":	nomeArquivo = diretorios.usPasta+"estoqueMinimo_"+login.usalogin.lower()+".pdf"
			if __id == "07":	nomeArquivo = diretorios.usPasta+"giroProdutos_"+login.usalogin.lower()+".pdf"
			if __id == "08":	nomeArquivo = diretorios.usPasta+"fichaEstoque_"+login.usalogin.lower()+".pdf"
			if __id == "11":	nomeArquivo = diretorios.usPasta+"TabelaPreco_"+login.usalogin.lower()+".pdf"
			if __id == "12":	nomeArquivo = diretorios.usPasta+"contagemEstoque_"+login.usalogin.lower()+".pdf"
			if __id == "13":	nomeArquivo = diretorios.usPasta+"compras_"+login.usalogin.lower()+".pdf"
			if __id == "15":	nomeArquivo = diretorios.usPasta+"entrega_filiais_"+login.usalogin.lower()+".pdf"
			if __id == "16":	nomeArquivo = diretorios.usPasta+"compras_produtos_"+login.usalogin.lower()+".pdf"
			if __id == "17":	nomeArquivo = diretorios.usPasta+"vendas_produtos_"+login.usalogin.lower()+".pdf"
			if __id == "18":	nomeArquivo = diretorios.usPasta+"vendas_produtos_"+login.usalogin.lower()+".pdf"
			if __id == "19":	nomeArquivo = diretorios.usPasta+"sem_giro_"+login.usalogin.lower()+".pdf"
			if __id == "20":	nomeArquivo = diretorios.usPasta+"auxiliar_compras_"+login.usalogin.lower()+".pdf"
			if __id == "22":	nomeArquivo = diretorios.usPasta+"estoque_local_"+login.usalogin.lower()+".pdf"
			if __id == "900":	nomeArquivo = diretorios.usPasta+"manejo_"+login.usalogin.lower()+".pdf"

			"""   Totalizar Media Geral do Custo e de Vendas   """
			if __id == "07":
				
				_vTcompra = Decimal( "0.0000" )
				_vTvendas = Decimal( "0.0000" )
				_vTdevolu = Decimal( "0.0000" )
				_vTsaldoc = Decimal( "0.0000" )

				_TTVendas = Decimal( "0.0000" )
				_TTDevolu = Decimal( "0.0000" )
				
				_Tempoc = 0
				_Tempov = 0 
				
				_valCus = Decimal( "0.0000" )
				_valVen = Decimal( "0.0000" ) 

				_vlMCus = Decimal( "0.0000" )
				_vlMVen = Decimal( "0.0000" ) 
				
				for rma in range( qLisTa ):

					if self.A == True:

						if cLisTa[2] !="":	_vTcompra +=Decimal( cLisTa[2].replace(",",'') )
						if cLisTa[3] !="":	_vTvendas +=Decimal( cLisTa[3].replace(",",'') )
						if cLisTa[4] !="":	_vTdevolu +=Decimal( cLisTa[4].replace(",",'') )
						if cLisTa[5] !="":	_vTsaldoc +=Decimal( cLisTa[5].replace(",",'') )

						if Decimal( cLisTa[8].split("|")[7] ) !=0:	_TTVendas +=Decimal( cLisTa[8].split("|")[7] )
						if Decimal( cLisTa[8].split("|")[8] ) !=0:	_TTDevolu +=Decimal( cLisTa[8].split("|")[8] )

					else:
						if cLisTa.GetItem(rma, 2).GetText() !="":	_vTcompra +=Decimal( cLisTa.GetItem(rma, 2).GetText().replace(",",'') )
						if cLisTa.GetItem(rma, 3).GetText() !="":	_vTvendas +=Decimal( cLisTa.GetItem(rma, 3).GetText().replace(",",'') )
						if cLisTa.GetItem(rma, 4).GetText() !="":	_vTdevolu +=Decimal( cLisTa.GetItem(rma, 4).GetText().replace(",",'') )
						if cLisTa.GetItem(rma, 5).GetText() !="":	_vTsaldoc +=Decimal( cLisTa.GetItem(rma, 5).GetText().replace(",",'') )

						if Decimal( cLisTa.GetItem(rma, 8).GetText().split("|")[7] ) !=0:	_TTVendas +=Decimal( cLisTa.GetItem(rma, 8).GetText().split("|")[7] )
						if Decimal( cLisTa.GetItem(rma, 8).GetText().split("|")[8] ) !=0:	_TTDevolu +=Decimal( cLisTa.GetItem(rma, 8).GetText().split("|")[8] )

					if self.A == True:	ccLisTa = cLisTa[7].split("\n")
					else:	ccLisTa = cLisTa.GetItem(rma, 7).GetText().split("\n")
						
					for ms in ccLisTa:
					
						rgT  = ms.split("|")
						if rgT[0] !='' and rgT[5] !="" and int( rgT[5] ) > 0 and Decimal( rgT[6] ) > 0: #-: Custo
					
							_Tempoc +=int( rgT[5] )
							_valCus +=Decimal( rgT[6] )
							

						if rgT[0] !='' and rgT[5] !="" and int( rgT[5] ) > 0 and Decimal( rgT[7] ) > 0: #-: Vendas

							_Tempov +=int( rgT[5] )
							_valVen +=Decimal( rgT[7] )

				if _Tempoc !=0 and _valCus !=0:	_vlMCus = ( _valCus / _Tempoc )
				if _Tempov !=0 and _valVen !=0:	_vlMVen = ( _valVen / _Tempov )
			
			cv = canvas.Canvas(nomeArquivo, pagesize=landscape(A4))
			
			cabccnf(False)

			if __id == "15":
				
				cv.setFont('Helvetica', 7)
				cv.setFillColor(HexColor('0x000000'))
				cv.drawString(600,528, "Origem         Destino")

			pular  = 48
			if __id in ["07"]:	pular = 46
			lcampo = 515
			ccampo = 525
			linhas = 1

			if __id == "01":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+'%Relatorio: Totalizar Estoque|'
			if __id == "02":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Estoque Zero)|'
			if __id == "03":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Estoque Negativo)|'
			if __id == "04":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Reserva Local)|'
			if __id == "05":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Totaliza Vendas)|'
			if __id == "06":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Estoque Mínimo)|'
			if __id == "07":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Giro de Produtos)|'
			if __id == "08":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Ficha de Estoque)|'
			if __id == "11":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Tabela de Preços)|'
			if __id == "12":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Contagem Estoque)|'
			if __id == "13":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Compras)|'
			if __id == "15":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Entrega Entre Filiais)|'
			if __id == "16":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Comrpas p/Produtos)|'
			if __id == "17":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Produtos vendidos)|'
			if __id == "18":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Unidade Manejo-Extrator)|'
			if __id == "19":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Produtos sem Giro)|'
			if __id == "20":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Auxiliar compras)|'
			if __id == "22":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Estoque local )|'

			if __id == "900":	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Romaneio de Entrega)|'

			if __id == "900":
				
				relacao = _di #-: Lista de Davs para entregar
				NumeroD = ( len( relacao.split("[p]") ) -1 )
				ordem   = 1
				saida   = 1

				for le in relacao.split("[p]"):

					rlc = le.split("|")
					
					if rlc[0]:

						cv.setFont('Helvetica', 7)
						cv.setFillColor(HexColor('0x000000'))
						
						cv.drawString(22,  float(lcampo),rlc[0])
						cv.drawString(50,  float(lcampo),rlc[1])
						cv.drawString(110, float(lcampo),rlc[2])

						cv.drawString(22, float(lcampo-20),"{"+str( ordem ).zfill(3)+"}")
						ordem +=1
						saida +=1
						
						cv.setFont('Helvetica-Bold', 6)
						if rlc[5] != "":	cv.drawString(450, float(lcampo),rlc[5].split(";")[0]+"  "+rlc[5].split(";")[1])
		
						cv.setFont('Helvetica', 7)
						cv.drawString(600, float(lcampo),rlc[3])
						
						ende = ""
						refe = ""
						dado = ""

						if rlc[4].split(";") !="":

							_in = 0
							for Tx in rlc[4].split(";")[0].split("\n"):
								
								refe +=Tx+" "
								_in +=1
								if _in == 3:	break

								
						if rlc[6] !="":	cv.drawString(650, float(lcampo),rlc[6].split(";")[5]+" "+rlc[6].split(";")[6]+" "+rlc[6].split(";")[7])
						if rlc[6] !="":	ende = str( rlc[6].split(";")[0] )+", "+str( rlc[6].split(";")[3] )+" "+str( rlc[6].split(";")[4])+" Bairro: "+str( rlc[6].split(";")[1] )
							
						cv.setFillColor(HexColor('0x4D4D4D'))
						cv.drawString(110, float(lcampo-10),"Endereço..: "+ende )
						cv.drawString(110, float(lcampo-20),"Referencia: "+refe[:110] )

						if linhas !=1:	cv.line(20,( lcampo + 7 ),820,( lcampo + 7 ))

						lcampo -= 30
						linhas +=1

						if linhas == 16 and NumeroD > ( ordem -1 ):

							cabccnf(True)
							mdl.rodape(cv,rd1,'','','','','','','','',6)

							pg +=1
							cv.addPageLabel(pg)
							cv.showPage()						
							linhas = 1
							saida  = 1
							lcampo = 515
							ccampo = 525
								
							cabccnf(False)

				"""   Relacionar os itens p/carga do caminhao   """
				if par.relacionarCargar and par.listar_romaneio:
					
					cv.line(20,( lcampo + 7 ),820,( lcampo + 7 ))

					carga = True
					
					pg +=1
					cv.addPageLabel(pg)
					cv.showPage()						
					cabccnf(False)

					linhas = 1
					lcampo = 505
					ccampo = 525

					cv.setFont('Helvetica-Bold', 8)
					cv.setFillColor(HexColor('0x000000'))
					cv.drawString(22,  515, "Código" )
					cv.drawString(120, 515, "Descrição dos produtos")

					cv.drawRightString( 540, 515, "Quantidade" )
					cv.drawRightString( 590, 515, "QT Pçs" )
					cv.drawRightString( 750, 515, "Metros" )
					cv.drawRightString( 818, 515, "Ocorrencias" )
					
					for rc in par.listar_romaneio:
												
						cg = rc.split(";")
						if Decimal( cg[9] ):
							
							cv.setFont('Helvetica', 8)
							cv.setFillColor(HexColor('0x000000'))
							cv.drawString( 22,  float(lcampo-2), cg[0] )
							cv.drawString( 120, float(lcampo-2), cg[1] )

							saldo = cg[9] ## if not Decimal( cg[10] ) else str( ( Decimal( cg[9] ) - Decimal( cg[10] ) ) )
							colun = 540

							if Decimal( cg[10] ):
								
								saldo = "( Venda: "+cg[9]+" Devolucao: "+cg[10]+"  SALDO: "+ str( ( Decimal( cg[9] ) - Decimal( cg[10] ) ) )+" )"
								colun = 700
							
							cv.drawRightString( colun, float(lcampo-2), saldo+' '+cg[2] )
							if cg[4].split('|')[0]:	cv.drawRightString( 590, float(lcampo-2), cg[4].split('|')[0] )
							if len( cg[4].split('|')[0] ) >= 2:	cv.drawRightString( 750, float(lcampo-2), cg[4].split('|')[1] )

							cv.setFont('Helvetica', 5)
							if cg[5].split('|')[0]:
								
								cv.drawRightString( 800, float(lcampo+2), "{ Numero do dav }" ) #-: Numero dav
								cv.drawRightString( 800, float(lcampo-4), cg[5].split('|')[0] ) #-: Numero dav

							cv.setFont('Helvetica', 8)

							cv.drawRightString( 818, float(lcampo-2), cg[5].split('|')[1] ) #-: Ocorrencias
							cv.line(20,( lcampo + 7 ),820,( lcampo + 7 ))
							
							lcampo -= 13
							linhas +=1

							if linhas == 35:

								cv.line(20,( lcampo + 7 ),820,( lcampo + 7 ))
								cabccnf(False)
								mdl.rodape(cv,rd1,'','','','','','','','',6)

								pg +=1
								cv.addPageLabel(pg)
								cv.showPage()						
								linhas = 1
								saida  = 1
								lcampo = 505
								ccampo = 525
								cabccnf(False)

								cv.setFont('Helvetica-Bold', 8)
								cv.setFillColor(HexColor('0x000000'))
								cv.drawString(22,  515, "Código" )
								cv.drawString(120, 515, "Descrição dos produtos")

								cv.drawRightString( 540, 515, "Quantidade" )
								cv.drawRightString( 590, 515, "QT Pçs" )
								cv.drawRightString( 750, 515, "Metros" )
								cv.drawRightString( 818, 515, "Ocorrencias" )

			else:
				
				if self.A:	__nReg = 1
				else:	__nReg = par.RLTprodutos.GetItemCount()

				"""
					Totalizar custo medio monfardini utiliza custo medio p/alisar o grupos e fabricantes 
				"""
				total_custovendas = Decimal("0.00")
				total_custodevolu = Decimal("0.00")
				if __id == "07":

					_mensagem = mens.showmsg("Produtos: Totalizando custo médio\nAguarde...")
					xIndice = 0

					for _xr in range( __nReg ):

						if self.A:	_xrel1 = cLisTa[7]
						else:	_xrel1 = cLisTa.GetItem(xIndice, 7).GetText()

						for _xmm in _xrel1.split("\n"):

							_xmes = _xmm.split("|")

							if _xmes[0] !="":

								xqT = Decimal( _xmes[5] )
								xmc = Decimal( _xmes[6] )
								
								_xvnd = _xdev = _xcM = Decimal("0.00")

								if xqT and xmc:	_xcM = self.T.trunca( 1, ( xmc / xqT ) )
								if Decimal( _xmes[2].replace(',','') ) !=0:	_xvnd = Decimal( _xmes[2].replace(',','') )
								if Decimal( _xmes[3].replace(',','') ) !=0:	_xdev = Decimal( _xmes[3].replace(',','') )

								if _xcM and _xvnd:	total_custovendas += ( _xvnd * _xcM )
								if _xcM and _xdev:	total_custodevolu += ( _xdev * _xcM )
									
						xIndice +=1
					_mensagem = mens.showmsg("Produtos: Montando Relatório\nAguarde...")

				"""  Utilizado no relatorio 18 """
				nome_filial    = ""
				codigo_produto = ""
				nome_produto   = ""
				unidade_manejo = ""
				nome_extrator  = ""
				
				Indice = 0
				for r in range( __nReg ):

					moT  = ''
					if self.A:	_rel = [""]
					else:	_rel = par.RLTprodutos.GetItem(Indice, 11).GetText().split('|')

					if __id == "05":	_rel = par.RLTprodutos.GetItem(Indice, 9).GetText().split('|')
					if __id == "06":	_rel = par.RLTprodutos.GetItem(Indice, 6).GetText().split('|')
								
					if __id not in ["05","06","07","08","11","12","13","15","16","17","18","19","20","22"]:
						
						_sTcp = _sTcu = _sTcm = _sTvd = Decimal('0.0000')
						if Decimal( _rel[2] ) > 0 and Decimal( _rel[3] ) > 0:	_sTcp = self.T.trunca(5, ( Decimal( _rel[3] ) * Decimal( _rel[2] ) ) )
						if Decimal( _rel[2] ) > 0 and Decimal( _rel[4] ) > 0:	_sTcu = self.T.trunca(5, ( Decimal( _rel[4] ) * Decimal( _rel[2] ) ) )
						if Decimal( _rel[2] ) > 0 and Decimal( _rel[5] ) > 0:	_sTcm = self.T.trunca(5, ( Decimal( _rel[5] ) * Decimal( _rel[2] ) ) )
						if Decimal( _rel[2] ) > 0 and Decimal( _rel[6] ) > 0:	_sTvd = self.T.trunca(5, ( Decimal( _rel[6] ) * Decimal( _rel[2] ) ) )
							
						cv.setFont('Helvetica', 7)
						cv.drawString(22, float(lcampo),_rel[0])
						cv.drawString(50, float(lcampo),_rel[1][:65])

					if __id == "01":

						cv.drawString(325, float(lcampo),_rel[13])
						if Decimal(_rel[2]) !=0:	cv.drawRightString(415, float(lcampo), format(Decimal(_rel[2]),',') )
						
						cv.drawString( 422, float(lcampo), "("+format( Decimal( str( _rel[3] ).rstrip("0") ),",")+") " )
						cv.drawString( 522, float(lcampo), "("+format( Decimal( str( _rel[4] ).rstrip("0") ),",")+") " )
						cv.drawString( 622, float(lcampo), "("+format( Decimal( str( _rel[5] ).rstrip("0") ),",")+") " )
						cv.drawString( 722, float(lcampo), "("+format( Decimal( str( _rel[6] ).rstrip("0") ),",")+") " )

						if _sTcp !=0:	cv.drawRightString( 515, float(lcampo), format(_sTcp,',') )
						if _sTcu !=0:	cv.drawRightString( 615, float(lcampo), format(_sTcu,',') )
						if _sTcm !=0:	cv.drawRightString( 715, float(lcampo), format(_sTcm,',') )
						if _sTvd !=0:	cv.drawRightString( 818, float(lcampo), format(_sTvd,',') )
				
					elif __id in ["02","03","04"]:
						
						cv.drawString(300, float(lcampo),_rel[8])
						cv.drawString(390, float(lcampo),_rel[9])
						cv.drawString(480, float(lcampo),_rel[10])
						cv.drawString(570, float(lcampo),_rel[11])
						cv.drawString(660, float(lcampo),_rel[12])

						cv.drawRightString(761, float(lcampo),format(Decimal(_rel[2]),','))
						cv.drawRightString(818, float(lcampo),format(Decimal(_rel[7]),','))

					elif __id == "05":

						cmv = par.RLTprodutos.GetItem(Indice, 10).GetText()
						cmd = par.RLTprodutos.GetItem(Indice, 11).GetText()
						cv.setFont('Helvetica-Bold', 7)
						if Decimal( _rel[3] ) < 0:	cv.setFillColor(HexColor('0xCD1D1D'))
						cv.drawString(22, float(lcampo),_rel[0])

						cv.setFont('Helvetica-Bold', 4)
						cv.setFillColor(HexColor('0x7F7F7F'))
						cv.drawRightString(160,( float(lcampo) + 4 ),"vendas")
						cv.drawRightString(200,( float(lcampo) + 4 ),"devolução")
						
						cv.setFillColor(HexColor('0x000000'))
						cv.setFont('Helvetica-Bold', 5)
						cv.drawString(100,( float(lcampo) - 1 ),"Comissão:")
						cv.drawRightString(160, ( float(lcampo) - 1 ), str( cmv ) )
						cv.drawRightString(200, ( float(lcampo) - 1 ), str( cmd ) )
						cv.setFont('Helvetica-Bold', 7)
	
						desconto_vendas = format( Decimal(  _rel[9].split(";")[11] ),',') if _rel[9]  and Decimal( _rel[9].split(";")[11] ) else ""
						desconto_devolu = format( Decimal( _rel[10].split(";")[11] ),',') if _rel[10] and Decimal( _rel[10].split(";")[11] ) else ""

						cv.setFont('Helvetica-Bold', 4)
						cv.setFillColor(HexColor('0x7F7F7F'))
						sv = sd = 0
						if desconto_vendas:

							cv.drawRightString(525,float(lcampo) + 6,str( desconto_vendas )+" Descontos")
							sv = 1

						if desconto_devolu:

							cv.drawRightString(615,float(lcampo) + 6,str( desconto_devolu )+" Descontos")
							sd = 1

						cv.setFillColor(HexColor('0x000000'))
						cv.setFont('Helvetica-Bold', 7)

						cv.drawRightString(285,float(lcampo),_rel[1])
						cv.drawRightString(375,float(lcampo),_rel[2])
						cv.drawRightString(435,float(lcampo),_rel[3])
						
						cv.drawRightString( 525, float(lcampo) - sv, _rel[4] )
						cv.drawRightString( 615, float(lcampo) - sd, _rel[5] )

						cv.drawRightString(675,float(lcampo),_rel[6])
						cv.drawRightString(745,float(lcampo),_rel[7])
						cv.drawRightString(815,float(lcampo),_rel[8])
						
						if par.ananal.GetValue() or par.anacum.GetValue():

							if _rel[9] or _rel[10]:
							
								cv.setFillGray(0.1,0.1) 
								if linhas == 1:

									cv.rect(20,( lcampo - 2 ),800,12, fill=1) #--: Fundo do cabecalho
									linhas +=2
									lcampo -= 10

									cabecalho_segundo()
									
								else:
									cv.rect(20,( lcampo - 2 ),800,10, fill=1) #--: Fundo do cabecalho
									linhas +=1
									lcampo -= 10

									cabecalho_segundo()

									if linhas >= 47:
											
										cabccnf(False)
										mdl.rodape(cv,rd1,'','','','','','','','',6)
										pg +=1
										cv.addPageLabel(pg)
										cv.showPage()						
										linhas = 1
										lcampo = 515
										ccampo = 525
										cabccnf( False )
										cabecalho_segundo()
																
								if _rel[9]:

									emiss_relatorio = _rel[9] if par.ananal.GetValue() else par.RLTprodutos.GetItem(Indice, 12).GetText().split('|')[0]
									for Tv in emiss_relatorio.split('\n'):
	
										cv.setFillColor(HexColor('0x7F7F7F'))
										cv.setFont('Helvetica', 7)

										sad = Tv.split(";")
										if sad[0]:
											
											linhas +=1
											lcampo -= 10

											cv.drawString( 22, float(lcampo),sad[0] )

											cv.setFont('Helvetica-Bold', 6)
											if  par.anacum.GetValue():
												
												cv.drawString( 100, float(lcampo), sad[11].zfill(7) )
												cv.drawString( 128, float(lcampo), sad[1] )
												
											else:	cv.drawString( 100, float(lcampo), sad[9]+'-'+sad[1] )
											
											cv.setFont('Helvetica-Bold', 5)
											cv.drawString( 400, float(lcampo), sad[2] )
											cv.drawString( 460, float(lcampo), sad[3] )
											cv.drawString( 520, float(lcampo), sad[4] )
											cv.drawString( 580, float(lcampo), sad[5] )
											cv.drawRightString( 672, float(lcampo), sad[6] )
											cv.drawRightString( 712, float(lcampo), sad[7] )
											cv.drawRightString( 752, float(lcampo), sad[8] )
											cv.drawRightString( 815, float(lcampo), sad[10] )

											if linhas >= 47:
												
												cabccnf(False)
												mdl.rodape(cv,rd1,'','','','','','','','',6)
												pg +=1
												cv.addPageLabel(pg)
												cv.showPage()						
												linhas = 1
												lcampo = 515
												ccampo = 525
												cabccnf( False )
												cabecalho_segundo()
											
								if _rel[10]:

									emiss_relatorio = _rel[10] if par.ananal.GetValue() else par.RLTprodutos.GetItem(Indice, 12).GetText().split('|')[1]
									for Td in emiss_relatorio.split('\n'):

										cv.setFillColor(HexColor('0x4D4D4D'))
										cv.setFont('Helvetica-Bold', 6)

										sdd = Td.split(";")
										if sdd[0]:
											
											linhas +=1
											lcampo -= 10
											
											if len(sdd[3]) > 45:	cv.setFont('Helvetica-Bold', 5)
											else:	cv.setFont('Helvetica-Bold', 6)
											cv.drawString( 22, float(lcampo),sdd[0] )

											cv.setFont('Helvetica-Bold', 6)
											if  par.anacum.GetValue():
												
												cv.drawString( 100, float(lcampo), sdd[11].zfill(7) )
												cv.drawString( 128, float(lcampo), sdd[1] )
												
											else:	cv.drawString( 100, float(lcampo), sdd[9]+'-'+sdd[1] )

											cv.setFont('Helvetica-Bold', 5)
											cv.drawString( 400, float(lcampo), sdd[2] )
											cv.drawString( 460, float(lcampo), sdd[3] )
											cv.drawString( 520, float(lcampo), sdd[4] )
											cv.drawString( 580, float(lcampo), sdd[5] )
											cv.drawRightString( 672, float(lcampo), sdd[6] )
											cv.drawRightString( 712, float(lcampo), sdd[7] )
											cv.drawRightString( 752, float(lcampo), sdd[8] )
											cv.drawRightString( 815, float(lcampo), sdd[10] )

											if linhas >= 47:
												
												cabccnf(False)
												mdl.rodape(cv,rd1,'','','','','','','','',6)
												pg +=1
												cv.addPageLabel(pg)
												cv.showPage()						
												linhas = 1
												lcampo = 515
												ccampo = 525
												cabccnf( False )
												cabecalho_segundo()


						cv.setFillColor(HexColor('0x000000'))
						cv.setFont('Helvetica-Bold', 7)

					elif __id == "06":

						cv.setFont('Helvetica', 7)
						cv.drawString(22, float(lcampo),_rel[0])
						cv.drawString(50, float(lcampo),_rel[1])
						cv.drawRightString(475,float(lcampo),_rel[2])
						cv.drawRightString(565,float(lcampo),_rel[3])
						cv.drawRightString(655,float(lcampo),_rel[4])
						cv.drawRightString(745,float(lcampo),_rel[5])

					elif __id == "11":

						cv.setFont('Helvetica', 7)
						cv.drawString(22,  float(lcampo), par.RLTprodutos.GetItem( Indice, 0 ).GetText() )
						cv.drawString(50,  float(lcampo), par.RLTprodutos.GetItem( Indice, 1 ).GetText() )
						cv.drawString(120, float(lcampo), par.RLTprodutos.GetItem( Indice, 2 ).GetText() )
						cv.drawString(380, float(lcampo), par.RLTprodutos.GetItem( Indice, 3 ).GetText() )
						cv.drawString(480, float(lcampo), par.RLTprodutos.GetItem( Indice, 4 ).GetText() )

						if Decimal( par.RLTprodutos.GetItem( Indice, 6 ).GetText().replace(',','') ) > 0:	cv.drawRightString(616, float(lcampo), par.RLTprodutos.GetItem( Indice, 6 ).GetText() )
						if Decimal( par.RLTprodutos.GetItem( Indice, 7 ).GetText().replace(',','') ) > 0:	cv.drawRightString(656, float(lcampo), par.RLTprodutos.GetItem( Indice, 7 ).GetText() )
						if Decimal( par.RLTprodutos.GetItem( Indice, 8 ).GetText().replace(',','') ) > 0:	cv.drawRightString(696, float(lcampo), par.RLTprodutos.GetItem( Indice, 8 ).GetText() )
						if Decimal( par.RLTprodutos.GetItem( Indice, 9 ).GetText().replace(',','') ) > 0:	cv.drawRightString(736, float(lcampo), par.RLTprodutos.GetItem( Indice, 9 ).GetText() )
						if Decimal( par.RLTprodutos.GetItem( Indice,10 ).GetText().replace(',','') ) > 0:	cv.drawRightString(776, float(lcampo), par.RLTprodutos.GetItem( Indice,10 ).GetText() )
						if Decimal( par.RLTprodutos.GetItem( Indice,11 ).GetText().replace(',','') ) > 0:	cv.drawRightString(818, float(lcampo), par.RLTprodutos.GetItem( Indice,11 ).GetText() )

						cv.setFont('Helvetica', 8)

					elif __id == "12":

						gfe = fsc = ""
						if par.pGrupo.GetValue() == True:	gfe = par.RLTprodutos.GetItem( Indice, 9 ).GetText()
						if par.psGru1.GetValue() == True:	gfe = par.RLTprodutos.GetItem( Indice, 10).GetText()
						if par.psGru2.GetValue() == True:	gfe = par.RLTprodutos.GetItem( Indice, 11).GetText()
						if par.pFabri.GetValue() == True:	gfe = par.RLTprodutos.GetItem( Indice, 8 ).GetText()
						if par.pEnder.GetValue() == True:	gfe = par.RLTprodutos.GetItem( Indice, 7 ).GetText()
						if Decimal( par.RLTprodutos.GetItem( Indice, 6 ).GetText() ) != 0:	fsc = par.RLTprodutos.GetItem( Indice, 6 ).GetText()+' '+par.RLTprodutos.GetItem( Indice, 12 ).GetText()

						if Decimal( par.RLTprodutos.GetItem( Indice, 6 ).GetText() ) < 0:	cv.setFillColor(HexColor('0xC00505'))
						cv.setFont('Helvetica', 6.7)
						cv.drawString(22,  float(lcampo), par.RLTprodutos.GetItem( Indice, 0 ).GetText() )
						cv.setFont('Helvetica', 8)
						cv.drawRightString(117, float(lcampo), par.RLTprodutos.GetItem( Indice, 1 ).GetText() )
						cv.drawRightString(187, float(lcampo), par.RLTprodutos.GetItem( Indice, 2 ).GetText() )
						cv.drawRightString(257, float(lcampo), par.RLTprodutos.GetItem( Indice, 3 ).GetText() )
						cv.drawRightString(337, float(lcampo), par.RLTprodutos.GetItem( Indice, 4 ).GetText() )

						if not par.pEnder.GetValue():	cv.setFont('Helvetica', 6)
						
						cv.drawString(340, float(lcampo), par.RLTprodutos.GetItem( Indice, 5 ).GetText() )
						
						if not par.pEnder.GetValue():	cv.drawRightString(657, float(lcampo), par.RLTprodutos.GetItem( Indice, 7 ).GetText() )
						if not par.pEnder.GetValue():	cv.setFont('Helvetica', 8)

						cv.drawRightString(737, float(lcampo), fsc )
						cv.drawString(740, float(lcampo), gfe )

						cv.setFillColor(HexColor('0x000000'))

					elif __id == "13":

						cv.setFont('Helvetica', 6.7)
						cv.drawString(22,  float(lcampo), par.RLTprodutos.GetItem( Indice, 0 ).GetText() )
						cv.setFont('Helvetica', 8)
						cv.drawRightString(97, float(lcampo), par.RLTprodutos.GetItem( Indice, 1 ).GetText() )
						cv.drawRightString(147, float(lcampo), par.RLTprodutos.GetItem( Indice, 2 ).GetText() )
						cv.drawString(150, float(lcampo), par.RLTprodutos.GetItem( Indice, 3 ).GetText() )
						if par.fixData.GetValue():	cv.setFont('Helvetica', 7)
						cv.drawString(300, float(lcampo), par.RLTprodutos.GetItem( Indice, 4 ).GetText() )

						if par.fixData.GetValue():

							cv.setFillColor(HexColor('0x7F7F7F'))
							cv.setFont('Helvetica', 6.7)
							cv.drawRightString(672, float(lcampo),    par.RLTprodutos.GetItem( Indice, 18 ).GetText()+' Apagar' )
							cv.setFillColor(HexColor('0x3131B8'))
							cv.drawRightString(672, float(lcampo-10), par.RLTprodutos.GetItem( Indice, 19 ).GetText()+' Saldo  ' )
							cv.setFillColor(HexColor('0x000000'))

						cv.setFont('Helvetica', 8)

						cv.drawRightString(722, float(lcampo), par.RLTprodutos.GetItem( Indice, 5 ).GetText() )
						cv.drawRightString(772, float(lcampo), par.RLTprodutos.GetItem( Indice, 6 ).GetText() )

						cv.setFillColor(HexColor('0x3131B8'))
						if Decimal(  par.RLTprodutos.GetItem( Indice, 7 ).GetText().replace(",","") ) !=0:	cv.drawRightString(820, float(lcampo), par.RLTprodutos.GetItem( Indice, 7 ).GetText() )
						cv.drawString(300, float(lcampo-10), par.RLTprodutos.GetItem( Indice, 11 ).GetText() )
						if Decimal(  par.RLTprodutos.GetItem( Indice, 8 ).GetText().replace(",","") ) !=0:	cv.drawRightString(722, float(lcampo-10), par.RLTprodutos.GetItem( Indice, 8 ).GetText() )
						if Decimal(  par.RLTprodutos.GetItem( Indice, 9 ).GetText().replace(",","") ) !=0:	cv.drawRightString(772, float(lcampo-10), par.RLTprodutos.GetItem( Indice, 9 ).GetText() )
						if Decimal(  par.RLTprodutos.GetItem( Indice, 10).GetText().replace(",","") ) !=0:	cv.drawRightString(820, float(lcampo-10), par.RLTprodutos.GetItem( Indice, 10 ).GetText() )

						cv.setFillColor(HexColor('0x000000'))

						if linhas >= pular:

							cabccnf(True)
							mdl.rodape(cv,rd1,'','','','','','','','',6)

							pg +=1
							cv.addPageLabel(pg)
							cv.showPage()						
							linhas = 1
							lcampo = 515
							ccampo = 525
								
							cabccnf(False)

					elif __id == "07":
					
						if self.A == True:

							_rel1 = cLisTa[7]
							_rel2 = cLisTa[8].split("|")

							codigo = cLisTa[0]
							descri = cLisTa[1]
							compra = cLisTa[2]
							vendas = cLisTa[3]
							devolu = cLisTa[4]
							saldoc = cLisTa[5]

						else:
							_rel1 = cLisTa.GetItem(Indice, 7).GetText()
							_rel2 = cLisTa.GetItem(Indice, 8).GetText().split("|")

							codigo = cLisTa.GetItem(Indice, 0).GetText()
							descri = cLisTa.GetItem(Indice, 1).GetText()
							compra = cLisTa.GetItem(Indice, 2).GetText()
							vendas = cLisTa.GetItem(Indice, 3).GetText()
							devolu = cLisTa.GetItem(Indice, 4).GetText()
							saldoc = cLisTa.GetItem(Indice, 5).GetText()

						cv.setFillGray(0.3,0.1) 
						TM = 8
						if linhas == 1:	TM = 11
						cv.rect(20,( lcampo - 1 ),800,( ( lcampo - lcampo ) + TM ), fill=1)
						cv.setFillColor(HexColor('0x000000'))

						cv.setFont('Helvetica-Bold', 7)
						cv.drawString(22, float(lcampo),codigo)
						cv.drawString(90, float(lcampo),descri)
						cv.drawRightString(435,float(lcampo),compra)
						cv.drawRightString(495,float(lcampo),vendas)
						cv.drawRightString(555,float(lcampo),devolu)
						cv.drawRightString(615,float(lcampo),saldoc)

						""" Custo-Marcação """
						_cusMedio = _vndMedio = _marcacao = saldoCompra = ""
						__qC = __qV = __qD = __ea = Decimal('0.0000') 
						if compra !='':	__qC = Decimal(compra.replace(',',''))
						if vendas !='':	__qV = Decimal(vendas.replace(',',''))
						if devolu !='':	__qD = Decimal(devolu.replace(',',''))
						if _rel2[3] !="" and Decimal(_rel2[3]) > 0:	__ea = Decimal(_rel2[3])
						
						saldoCompra = ( ( __qC + __qD + __ea ) - __qV )
							
						_qT = Decimal( _rel2[0] )
						_cu = Decimal( _rel2[1] )
						_vd = Decimal( _rel2[2] )

						if _qT > 0 and _cu > 0:	_cusMedio = self.T.trunca( 1, ( _cu / _qT ) )
						if _qT > 0 and _vd > 0:	_vndMedio = self.T.trunca( 1, ( _vd / _qT ) )
						if _cu > 0 and _vd > 0:	_marcacao = self.T.trunca( 1, ( ( ( _vd / _cu ) - 1 ) * 100 ) )

						""" Medias Compra,Venda,Devolucao """
						mcom = mven = mdev = msal = 0
						for m in _rel1.split("\n"):

							_mes = m.split("|")
							if _mes[0] !="" and Decimal( _mes[1].replace(',','') ) !=0:	mcom+=1
							if _mes[0] !="" and Decimal( _mes[2].replace(',','') ) !=0:
								mven+=1
								msal+=1
							if _mes[0] !="" and Decimal( _mes[3].replace(',','') ) !=0:	mdev+=1

						if compra != "" and Decimal( compra.replace(",",'') ) > 0 and mcom > 1:
							mc = self.T.trunca( 5, ( Decimal( compra.replace(",",'') ) / mcom ) )
							mcom = "{ "+str(mcom)+" } "+format(mc,',')

						if vendas != "" and Decimal( vendas.replace(",",'') ) > 0 and mven > 1:
							mv = self.T.trunca( 5, ( Decimal( vendas.replace(",",'') ) / mven ) )
							mven = "{ "+str(mven)+" } "+format(mv,',')

						if devolu != "" and Decimal( devolu.replace(",",'') ) > 0 and mdev > 1:
							md = self.T.trunca( 5, ( Decimal( devolu.replace(",",'') ) / mdev ) )
							mdev = "{ "+str(mdev)+" } "+format(md,',')

						if saldoc != "" and Decimal( saldoc.replace(",",'') ) > 0 and msal > 1:
							ms = self.T.trunca( 5, ( Decimal( saldoc.replace(",",'') ) / msal ) )
							msal = "{ "+str(msal)+" } "+format(ms,',')

						cv.setFillColor(HexColor('#34A634'))
						if mcom !='' and mcom > 1:	cv.drawRightString(680,float(lcampo),str(mcom))
						if mven !='' and mven > 1:	cv.drawRightString(745,float(lcampo),str(mven))
						if mdev !='' and mdev > 1:	cv.drawRightString(805,float(lcampo),str(mdev))

						linhas +=1
						lcampo -= 10

						if linhas >= 46:

							cabccnf(True)
							mdl.rodape(cv,rd1,'','','','','','','','',6)

							pg +=1
							cv.addPageLabel(pg)
							cv.showPage()						
							linhas = 1
							lcampo = 515
							ccampo = 525

							cabccnf(False)


						"""  Totaliza Vendas   """
						cv.setFont('Helvetica', 6)
						cv.setFillColor(HexColor('0x000000'))
						cv.drawString(50, float(lcampo+3),"Total Vendas")
						cv.drawString(39, float(lcampo-10),"Total Devoluçoes")
						if Decimal(_rel2[7]) !=0:	cv.drawRightString(86,float(lcampo-3),format(Decimal(_rel2[7]),',') )
						if Decimal(_rel2[8]) !=0:	cv.drawRightString(86,float(lcampo-16),format(Decimal(_rel2[8]),',') )
						
						cv.setFont('Helvetica-Bold', 7)


						cv.setFillColor(HexColor('0x4B8BC8'))
						cv.drawString(305, float(lcampo),"Més")
						cv.drawRightString(435,float(lcampo),"QT Compra")
						cv.drawRightString(495,float(lcampo),"QT Vendas")
						cv.drawRightString(555,float(lcampo),"QT Devolução")
						cv.drawRightString(615,float(lcampo),"Saldo Vendas")
						cv.setFillColor(HexColor('0xFFA500'))
						cv.drawRightString(680,float(lcampo),"Média Custo")
						cv.drawRightString(745,float(lcampo),"Média Vendas")
						cv.drawRightString(818,float(lcampo),"Média Marcação")

						cv.setFillColor(HexColor('0x000000'))
						
						lnh_1 = lnh_2 = 0
						
						for mm in _rel1.split("\n"):

							_cmp = _vnd = _dev = _slv = ""
							_mes = mm.split("|")

							if _mes[0] !="":

								qT = Decimal( _mes[5] )
								mc = Decimal( _mes[6] )
								mv = Decimal( _mes[7] )

								_cM = _vM = _mc = ""
								if qT > 0 and mc > 0:	_cM = format( self.T.trunca( 1, ( mc / qT ) ),',' )
								if qT > 0 and mv > 0:	_vM = format( self.T.trunca( 1, ( mv / qT ) ),',' )
								if mc > 0 and mv > 0:	_mc = str( self.T.trunca( 1, ( ( ( mv / mc ) - 1 ) * 100 ) ) )
								
								if Decimal( _mes[1].replace(',','') ) !=0:	_cmp = _mes[1]
								if Decimal( _mes[2].replace(',','') ) !=0:	_vnd = _mes[2]
								if Decimal( _mes[3].replace(',','') ) !=0:	_dev = _mes[3]

								if Decimal( _mes[4].replace(',','') ) !=0:	_slv = _mes[4]

								""" Estoque Anterior """
								if lnh_1 == 0:

									cv.setFont('Helvetica', 6)
									daTa = ""
									if _rel2[4] !="":	daTa = format(datetime.datetime.strptime(_rel2[4], "%Y-%m-%d"),"%d/%m/%Y")

									cv.setFillColor(HexColor('0x8484D2'))
									cv.drawString(251,  float(lcampo+3),"Nº Ocorrências")
									cv.drawString(251,  float(lcampo-2),"{DAVs-Vendas}")
									cv.setFont('Helvetica', 7)
									cv.setFillColor(HexColor('0x5050B1'))
									cv.drawRightString(292,float(lcampo-12),str(_qT))
									cv.setFont('Helvetica', 6)
							
									cv.setFillColor(HexColor('0xA52A2A'))
									cv.drawString(90,  float(lcampo+3),"Estoque Anterior    Apuração"+(" "*25)+"Estoque Atual ")

									aj1 = 4
									aj2 = 12
									aj3 = 19
									if len( _rel1.split("\n") ) == 2:

										linhas +=1
										lcampo -= 10
										aj1 = -4
										aj2 = 3
										aj3 = 8
										
									cv.setFillColor(HexColor('0xDD1D1D'))
									cv.drawRightString(134,float(lcampo-aj1),_rel2[3])
									cv.drawString(141, float(lcampo-aj1),daTa+" "+_rel2[5])
									cv.drawRightString(247,float(lcampo-aj1),_rel2[6])
									
									cv.setFont('Helvetica', 6)
									cv.setFillColor(HexColor('0x63CA63'))
									cv.drawString(100,  float(lcampo-aj2),"Custo Médio"+(" "*5)+"Preço Médio"+(" "*27)+"Marcação")

									cv.setFillColor(HexColor('0x347F34'))
									cv.drawRightString(134,float(lcampo-aj3),str(_cusMedio))
									cv.drawRightString(176,float(lcampo-aj3),str(_vndMedio))
									if _marcacao!='':	cv.drawRightString(247,float(lcampo-aj3),str(_marcacao)+"%")

								lnh_1 +=1
								linhas +=1
								lcampo -= 10

								if linhas >= 46:

									lcampo -=8
									cabccnf(True)
									mdl.rodape(cv,rd1,'','','','','','','','',6)

									pg +=1
									cv.addPageLabel(pg)
									cv.showPage()						
									linhas = 1
									lcampo = 515
									ccampo = 525
									cabccnf(False)
								
								cv.setFont('Helvetica-Bold', 7)
								cv.setFillColor(HexColor('0x2727B6'))
								cv.drawString(305, float(lcampo),_mes[0])

								cv.drawRightString(435,float(lcampo),str(_cmp))
								cv.drawRightString(495,float(lcampo),str(_vnd))
								cv.drawRightString(555,float(lcampo),str(_dev))
								cv.drawRightString(615,float(lcampo),str(_slv))

								cv.setFillColor(HexColor('0xC68919'))
								cv.drawRightString(680,float(lcampo),str(_cM))

								cv.drawRightString(745,float(lcampo),str(_vM))
								if _mc !="" and _mc > 0:	cv.drawRightString(815,float(lcampo),str(_mc)+"%")
								cv.setFillColor(HexColor('0x000000'))

					elif __id == "08":

						nDC = par.RLTprodutos.GetItem(r, 0).GetText()
						emi = par.RLTprodutos.GetItem(r, 1).GetText()
						san = par.RLTprodutos.GetItem(r, 2).GetText()
						ent = par.RLTprodutos.GetItem(r, 3).GetText()
						sai = par.RLTprodutos.GetItem(r, 4).GetText()
						sal = par.RLTprodutos.GetItem(r, 5).GetText()
						his = par.RLTprodutos.GetItem(r, 6).GetText()
						cli = par.RLTprodutos.GetItem(r, 9).GetText()
						moT = par.RLTprodutos.GetItem(r,10).GetText()

						cv.setFont('Helvetica', 6)
						cv.setFillColor(HexColor('0x727070'))
						cv.drawString(22, float(lcampo),nDC)
						cv.setFillColor(HexColor('0x727070'))
						if moT.strip():	cv.drawString(90, float(lcampo+3),cli[:60] )
						else:	cv.drawString(90, float(lcampo),cli[:60] )

						if moT.strip():

							cv.setFont('Helvetica', 5)
							cv.setFillColor(HexColor('0x000000'))

							cv.drawString(90, ( float(lcampo-1) ),moT )
							cv.setFillColor(HexColor('0x727070'))
							cv.setFont('Helvetica', 6)

						cv.drawString(300,float(lcampo),emi)
						cv.setFont('Helvetica', 7)
						cv.drawRightString(497,float(lcampo),san)

						cv.setFillColor(HexColor('0x1212DA'))
						cv.drawRightString(557,float(lcampo),ent)

						cv.setFillColor(HexColor('0xC20B0B'))
						cv.drawRightString(617,float(lcampo),sai)

						if Decimal( str(sal).replace(',','') ) >=0:	cv.setFillColor(HexColor('0x1212DA'))
						cv.drawRightString(682,float(lcampo),sal)
						
						if len( his ) > 31:	cv.setFont('Helvetica', 5)
						cv.setFillColor(HexColor('0x0B710B'))
						cv.drawString(685,float(lcampo),his)
						cv.setFont('Helvetica', 7)
							
					elif __id == "15":

						dav = par.RLTprodutos.GetItem(r, 0).GetText()
						emi = par.RLTprodutos.GetItem(r, 1).GetText()
						des = par.RLTprodutos.GetItem(r, 2).GetText()
						qte = par.RLTprodutos.GetItem(r, 3).GetText()
						flo = par.RLTprodutos.GetItem(r, 4).GetText()
						fld = par.RLTprodutos.GetItem(r, 5).GetText()
						qta = par.RLTprodutos.GetItem(r, 6).GetText()
						por = par.RLTprodutos.GetItem(r, 7).GetText()

						cv.setFont('Helvetica', 7)
						cv.drawString(22,  float(lcampo), dav )
						cv.drawString(80,  float(lcampo), emi )
						cv.drawString(200, float(lcampo), des[:62] )
						cv.drawRightString(535, float(lcampo), qta )
						cv.drawRightString(595, float(lcampo), qte )

						cv.drawString(600, float(lcampo), flo )
						cv.drawString(640, float(lcampo), fld )

						cv.drawString(670, float(lcampo), por.lower()[:40] )

					elif __id == "16":

						fil = par.RLTprodutos.GetItem(r, 0).GetText()
						nct = par.RLTprodutos.GetItem(r, 1).GetText()
						lan = par.RLTprodutos.GetItem(r, 2).GetText()
						cod = par.RLTprodutos.GetItem(r, 3).GetText()
						des = par.RLTprodutos.GetItem(r, 4).GetText()
						qtc = par.RLTprodutos.GetItem(r, 5).GetText()
						vlu = par.RLTprodutos.GetItem(r, 6).GetText()
						vlc = par.RLTprodutos.GetItem(r, 7).GetText()
						frn = par.RLTprodutos.GetItem(r,10).GetText()

						cv.setFont('Helvetica', 7)
						cv.drawString(22,  float(lcampo), fil )
						cv.drawString(50,  float(lcampo), nct )
						cv.drawString(100, float(lcampo), lan )
						cv.drawRightString(295, float(lcampo), cod )
						cv.setFont('Helvetica', 6)
						cv.drawString(310, float(lcampo), des[:85] )

						cv.drawRightString(640, float(lcampo), qtc )
						cv.drawRightString(680, float(lcampo), format( Decimal( vlu ), ',' ) )
						cv.drawRightString(720, float(lcampo), format( Decimal( vlc ), ',' ) )

						cv.setFont('Helvetica', 5)
						cv.drawString(723, float(lcampo), frn[:30] )

					elif __id == "17":

						cv.setFont('Helvetica', 8) if not par.ananal.GetValue() else cv.setFont('Helvetica-Bold', 8)
						cv.drawString(22,       float(lcampo), par.RLTprodutos.GetItem(r, 0).GetText() )
						cv.drawRightString(128, float(lcampo), par.RLTprodutos.GetItem(r, 1).GetText() )
						cv.drawString(134,      float(lcampo), par.RLTprodutos.GetItem(r, 2).GetText() )
						cv.drawRightString(537, float(lcampo), par.RLTprodutos.GetItem(r, 3).GetText() )
						cv.drawRightString(607, float(lcampo), par.RLTprodutos.GetItem(r, 4).GetText() )
						cv.drawRightString(677, float(lcampo), par.RLTprodutos.GetItem(r, 5).GetText() )
						cv.drawRightString(747, float(lcampo), par.RLTprodutos.GetItem(r, 6).GetText() + " %" )
						cv.setFont('Helvetica', 7) if not par.ananal.GetValue() else cv.setFont('Helvetica-Bold', 7)
						if Decimal( par.RLTprodutos.GetItem(r, 7).GetText() ):	cv.drawRightString(780, float(lcampo), par.RLTprodutos.GetItem(r, 7).GetText() )
						if Decimal( par.RLTprodutos.GetItem(r, 8).GetText() ):	cv.drawRightString(818, float(lcampo), par.RLTprodutos.GetItem(r, 8).GetText() + " %" )

						if par.ananal.GetValue():

							if linhas !=1:	cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))
							cv.line(20,( lcampo - 2),820,( lcampo - 2 ))
							lcampo -= 10
							linhas +=1

							pular = 46

							cv.setFont('Helvetica', 7)
							cv.setFillColor(HexColor('0x5A5A5A'))
							cv.drawString(22,  float(lcampo), "Ordem" )
							cv.drawString(45,  float(lcampo), "Filial" )
							cv.drawString(80,  float(lcampo), "Numero dav" )
							cv.drawString(140, float(lcampo), "Lançamento" )
							cv.drawString(240, float(lcampo), "Descrição dos cliente" )

							cv.drawRightString(537, float(lcampo), "Quantidade" ) #-: QT Vendido
							cv.drawRightString(587, float(lcampo), "Valor custo" ) #-: Valor custo
							cv.drawRightString(637, float(lcampo), "Valor venda" ) #-: Valor venda
							cv.drawRightString(687, float(lcampo), "Total custo" ) #-: Total custo
							cv.drawRightString(737, float(lcampo), "Total venda" ) #-: Total venda
							cv.setFillColor(HexColor('0x000000'))

							numero_davs = 1
							produto_descricao = ""
							produto_filial = ""

							for ps in par.RLTprodutos.GetItem(r, 9).GetText().split('\n'):

								#print ps
								if ps:

									lcampo -= 10
									linhas +=1
									relaca  = ps.split('|')
									#print relaca
									cv.setFont('Helvetica', 7)
									cv.drawString(22,  float(lcampo), str( numero_davs ).zfill(5) )
									if produto_filial != relaca[0]:	cv.drawString(45,  float(lcampo), relaca[0] )
									cv.drawString(80,  float(lcampo), relaca[1] )
									cv.drawString(140, float(lcampo), relaca[2] )
									if produto_descricao != relaca[4]:	cv.drawString(240, float(lcampo), relaca[4] )
									
									cv.drawRightString(537, float(lcampo), relaca[5] ) #-: QT Vendido
									cv.drawRightString(587, float(lcampo), relaca[6] ) #-: Valor custo
									cv.drawRightString(637, float(lcampo), relaca[7] ) #-: Valor venda
									cv.drawRightString(687, float(lcampo), relaca[8] ) #-: Total custo
									cv.drawRightString(737, float(lcampo), relaca[9] ) #-: Total venda
									cv.setFont('Helvetica', 6)
									cv.drawRightString(819, float(lcampo), "Margem lucro: "+relaca[10]+" %" ) #-: Margem

									#-// Devolucoes
									if len( relaca ) >= 12 and relaca[11]:

										lcampo -= 10
										linhas +=1
										__d = relaca[11].split(";")

										cv.setFont('Helvetica', 8)
										cv.setFillColor(HexColor('0xC40808'))
										cv.drawString(240, float(lcampo), "Devolucao { "+__d[4]+" DAVs  Referente a venda: "+ relaca[1] +" }" )

										cv.drawRightString(537, float(lcampo), __d[0] ) #-: QT Vendido
										cv.drawRightString(687, float(lcampo), __d[1] ) #-: Total custo
										cv.drawRightString(737, float(lcampo), __d[2] ) #-: Total venda
										cv.setFont('Helvetica', 7)
										cv.setFillColor(HexColor('0x5A5A5A'))

									produto_filial = relaca[0]
									produto_descricao = relaca[4]
									numero_davs +=1

									if linhas >= pular:

										if __id == "13":	lcampo += 8

										cabccnf( False )
										mdl.rodape(cv,rd1,'','','','','','','','',6)

										pg +=1
										cv.addPageLabel(pg)
										cv.showPage()						
										linhas = 1
										lcampo = 515
										ccampo = 525
											
										cabccnf( False )

					elif __id =="18":
						
						if par.ordenV.GetValue() or par.ordenD.GetValue() or par.ordenE.GetValue():

							if len( par.RLTprodutos.GetItem(r, 4).GetText().split("\n") ):

								if linhas >= pular:

									cabccnf( False )
									mdl.rodape(cv,rd1,'','','','','','','','',6)

									pg +=1
									cv.addPageLabel(pg)
									cv.showPage()						
									linhas = 1
									lcampo = 515
									ccampo = 525
												
									cabccnf( False )

								cv.setFont('Helvetica-Bold', 9)
								tamanho = 13 if linhas == 1 else 12
									
								if par.ordenV.GetValue():
									
									cv.drawString(22,  float(lcampo), par.RLTprodutos.GetItem(r, 0).GetText() )
									cv.drawString(50,  float(lcampo), par.RLTprodutos.GetItem(r, 1).GetText() )
									cv.drawString(200, float(lcampo), par.RLTprodutos.GetItem(r, 2).GetText() )
									cv.drawRightString(288, float(lcampo), par.RLTprodutos.GetItem(r, 3).GetText() )
									cv.drawRightString(350, float(lcampo), par.RLTprodutos.GetItem(r, 6).GetText())
									cv.setFillColor(HexColor('0x7F7F7F'))
									cv.drawRightString(487, float(lcampo), par.RLTprodutos.GetItem(r, 5).GetText()+" Quantidade" )

									cv.setFillGray(0.1,0.1) 
									cv.rect(20,(lcampo -3 ),800,tamanho, fill=1) #--: Fundo do cabecalho
									cv.setFillColor(HexColor('0x000000'))

								if par.ordenD.GetValue() or par.ordenE.GetValue():

									cv.drawString(22,  float(lcampo), par.RLTprodutos.GetItem(r, 0).GetText() )
									cv.drawString(50,  float(lcampo), par.RLTprodutos.GetItem(r, 1).GetText() )
									cv.drawString(400, float(lcampo), par.RLTprodutos.GetItem(r, 2).GetText() )
									cv.drawRightString(500, float(lcampo), par.RLTprodutos.GetItem(r, 3).GetText() )
									cv.drawRightString(570, float(lcampo), par.RLTprodutos.GetItem(r, 6).GetText() )
									cv.setFillColor(HexColor('0x7F7F7F'))
									cv.drawRightString(817, float(lcampo), par.RLTprodutos.GetItem(r, 5).GetText()+" Quantidade" )

									cv.setFillGray(0.1,0.1) 
									cv.rect(20,(lcampo -3 ),800,tamanho, fill=1) #--: Fundo do cabecalho
									cv.setFillColor(HexColor('0x000000'))

								lcampo -= 10
								linhas +=1

								cv.setFont('Helvetica', 7)
								cv.setFillColor(HexColor('0x7F7F7F'))
								cv.drawString(22, float(lcampo), 'Nº Controle' )
								cv.drawString(66, float(lcampo), 'Filial' )
								cv.drawString(96, float(lcampo), 'Laçamento' )
								cv.drawRightString(226, float(lcampo), 'Codigo' )
								cv.drawString(232, float(lcampo), 'Descrição dos produtos' )

								cv.setFont('Helvetica', 6)
								cv.drawRightString(487, float(lcampo), 'Quantidade' )
								cv.drawRightString(527, float(lcampo), 'Extrator Custo' )
								cv.drawRightString(567, float(lcampo), 'Extrator Total' )
								cv.setFont('Helvetica', 5)
								cv.drawRightString(612, float(lcampo), 'Fornecedor Custo' )
								cv.drawRightString(657, float(lcampo), 'Fornecedor Total' )

								cv.setFont('Helvetica', 7)
								cv.drawString(660, float(lcampo), '[ Unidade de manejo-roça ]->Descrição fornecedor' )

								cv.setFillColor(HexColor('0x000000'))

								nome_filial    = ""
								codigo_produto = ""
								nome_produto   = ""
								unidade_manejo = ""
								nome_extrator  = ""

								for _cmp in par.RLTprodutos.GetItem(r, 4).GetText().split("\n"):

									if _cmp:

										if linhas !=1:	lcampo -= 10

										__rl = _cmp.split("-|-")
										cv.setFont('Helvetica', 7)
										cv.drawString(22, float(lcampo), __rl[0] )
										if nome_filial != __rl[1]:	cv.drawString(66, float(lcampo), __rl[1] )
										cv.drawString(96, float(lcampo), __rl[2] )
										if codigo_produto != __rl[3]:	cv.drawRightString(226, float(lcampo), __rl[3] )
										cv.setFont('Helvetica', 6)
										if nome_produto != __rl[4]:	cv.drawString(232, float(lcampo), __rl[4] )
										cv.setFont('Helvetica', 7)

										cv.drawRightString(487, float(lcampo), __rl[5] )
										cv.drawRightString(527, float(lcampo), __rl[6] )
										cv.drawRightString(567, float(lcampo), __rl[7] )
										cv.drawRightString(612, float(lcampo), __rl[10] )
										cv.drawRightString(657, float(lcampo), __rl[11] )

										cv.setFont('Helvetica', 4)
										if unidade_manejo != __rl[8]:	cv.drawString(660, ( float(lcampo) +4 ), __rl[8] )
										cv.setFont('Helvetica', 5)
										if nome_extrator != __rl[9]:	cv.drawString(660, ( float(lcampo) -1 ), __rl[9] )
										cv.setFont('Helvetica', 7)

										if linhas !=1:	cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))
										linhas +=1
										
										nome_filial    = __rl[1] 
										codigo_produto = __rl[3]
										nome_produto   = __rl[4]
										unidade_manejo = __rl[8] 
										nome_extrator  = __rl[9]

										if linhas >= pular:

											cabccnf( False )
											mdl.rodape(cv,rd1,'','','','','','','','',6)

											pg +=1
											cv.addPageLabel(pg)
											cv.showPage()						
											linhas = 1
											lcampo = 515
											ccampo = 525
												
											cabccnf( False )
						
						if par.ordenQ.GetValue():
							
							cv.setFont('Helvetica', 7)
							cv.drawString(22, float(lcampo), par.RLTprodutos.GetItem(r, 0).GetText() )
							if nome_filial != par.RLTprodutos.GetItem(r, 1).GetText():	cv.drawString(66, float(lcampo), par.RLTprodutos.GetItem(r, 1).GetText() )
							cv.drawString(96, float(lcampo), par.RLTprodutos.GetItem(r, 2).GetText() )
							if codigo_produto != par.RLTprodutos.GetItem(r, 3).GetText():	cv.drawRightString(226, float(lcampo), par.RLTprodutos.GetItem(r, 3).GetText() )
							cv.setFont('Helvetica', 6)
							if nome_produto != par.RLTprodutos.GetItem(r, 4).GetText():	cv.drawString(232, float(lcampo), par.RLTprodutos.GetItem(r, 4).GetText() )
							
							cv.setFont('Helvetica', 6)

							cv.drawRightString(487, float(lcampo), par.RLTprodutos.GetItem(r, 5).GetText() )
							cv.drawRightString(517, ( float(lcampo) - 1 ), par.RLTprodutos.GetItem(r, 6).GetText() )
							cv.drawRightString(557, float(lcampo), par.RLTprodutos.GetItem(r, 7).GetText() )
							cv.drawRightString(597, float(lcampo), par.RLTprodutos.GetItem(r,10).GetText() )
							cv.drawRightString(637, float(lcampo), par.RLTprodutos.GetItem(r,11).GetText() )

							cv.setFont('Helvetica', 4)
							cv.setFillColor(HexColor('0x7F7F7F'))
							if unidade_manejo != par.RLTprodutos.GetItem(r, 8).GetText():	cv.drawString(642, ( float(lcampo) + 4 ), par.RLTprodutos.GetItem(r, 8).GetText() )
							cv.setFillColor(HexColor('0x000000'))
							if nome_extrator != par.RLTprodutos.GetItem(r, 9).GetText():	cv.drawString(642, ( float(lcampo) - 1 ), par.RLTprodutos.GetItem(r, 9).GetText() )
							cv.setFont('Helvetica', 7)

							nome_filial    = par.RLTprodutos.GetItem(r, 1).GetText()
							codigo_produto = par.RLTprodutos.GetItem(r, 3).GetText()
							nome_produto   = par.RLTprodutos.GetItem(r, 4).GetText()
							unidade_manejo = par.RLTprodutos.GetItem(r, 8).GetText()
							nome_extrator  = par.RLTprodutos.GetItem(r, 9).GetText()

					elif __id == "19":

						cv.setFont('Helvetica', 6)
						cv.drawRightString(75, float(lcampo), par.RLTprodutos.GetItem(Indice, 0).GetText() )

						if par.grvCur.GetValue():

							cv.drawString(80,  float(lcampo+3), par.RLTprodutos.GetItem(Indice, 1).GetText() )
							cv.setFont('Helvetica', 4)
							cv.drawString(80,  float(lcampo-1), par.RLTprodutos.GetItem(Indice, 2).GetText() )
							cv.setFont('Helvetica', 6)
						else:
							cv.drawString(80,  float(lcampo), par.RLTprodutos.GetItem(Indice, 1).GetText() )

						cv.drawString(378, float(lcampo), par.RLTprodutos.GetItem(Indice, 3).GetText() )
						cv.drawString(422, float(lcampo), par.RLTprodutos.GetItem(Indice, 4).GetText() )
						cv.drawString(512, float(lcampo), par.RLTprodutos.GetItem(Indice, 5).GetText() )

						cv.drawRightString(638, float(lcampo), par.RLTprodutos.GetItem(Indice, 6).GetText() )
						cv.drawRightString(728, float(lcampo), par.RLTprodutos.GetItem(Indice, 7).GetText() +"  [ "+par.RLTprodutos.GetItem(Indice, 9).GetText()+" ]" )
						cv.drawRightString(818, float(lcampo), par.RLTprodutos.GetItem(Indice, 8).GetText() +"  [ "+par.RLTprodutos.GetItem(Indice, 10).GetText()+" ]" )

					elif __id == "20":

						cv.setFont('Helvetica', 6)
						if len( par.RLTprodutos.GetItem(Indice, 1).GetText().split(':') ) == 2:
							
							cv.setFont('Helvetica', 4)
							cv.drawRightString(75, float(lcampo) + 4, "Codigo interno" )

							cv.setFont('Helvetica', 6)
							cv.drawRightString(75, float(lcampo) - 1, par.RLTprodutos.GetItem(Indice, 1).GetText().split(':')[1] )

						else:	cv.drawRightString(75, float(lcampo), par.RLTprodutos.GetItem(Indice, 1).GetText() )
						
						cv.drawString(80, float(lcampo), par.RLTprodutos.GetItem(Indice, 2).GetText() )
						cv.setFont('Helvetica', 5)
						cv.drawString(370, float(lcampo), par.RLTprodutos.GetItem(Indice, 3).GetText() )
						cv.setFont('Helvetica', 7)
						cv.drawString(420, float(lcampo), par.RLTprodutos.GetItem(Indice, 4).GetText() )
						if Decimal( par.RLTprodutos.GetItem(Indice, 6).GetText().replace(",","") ):	cv.drawRightString(535, float(lcampo), par.RLTprodutos.GetItem(Indice, 5).GetText() )
						if Decimal( par.RLTprodutos.GetItem(Indice, 6).GetText().replace(",","") ):	cv.drawRightString(635, float(lcampo), par.RLTprodutos.GetItem(Indice, 6).GetText() )
						if Decimal( par.RLTprodutos.GetItem(Indice, 7).GetText().replace(",","") ):	cv.drawRightString(728, float(lcampo), par.RLTprodutos.GetItem(Indice, 7).GetText() )
						if Decimal( par.RLTprodutos.GetItem(Indice, 8).GetText().replace(",","") ):	cv.drawRightString(817, float(lcampo), par.RLTprodutos.GetItem(Indice, 8).GetText() )

					elif __id == "22":

						cv.setFont('Helvetica', 9)
						cv.drawString(22, float(lcampo), par.RLTprodutos.GetItem(Indice, 0).GetText() )
						cv.drawRightString(140, float(lcampo), par.RLTprodutos.GetItem(Indice, 1).GetText() )
						cv.drawString(210,float(lcampo), par.RLTprodutos.GetItem(Indice, 2).GetText() )
						cv.drawRightString(400,float(lcampo), par.RLTprodutos.GetItem(Indice, 3).GetText() )
						cv.drawRightString(480,float(lcampo), par.RLTprodutos.GetItem(Indice, 4).GetText() )
						cv.drawString(487,float(lcampo), par.RLTprodutos.GetItem(Indice, 5).GetText() )

					if linhas !=1 and __id not in ["05","07","13","17","18"]:	cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))
					if linhas !=1 and __id == "13":	cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))

					if linhas !=1 and __id in ["05","17"] and par.ansint.GetValue():	cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))

					Indice +=1

					if __id == "13":

						lcampo -= 20
						linhas +=2
						
					elif __id == "08" and moT !='':

						lcampo -= 20
						linhas +=2

					else:
						lcampo -= 10
						linhas +=1
						
					if linhas !=1 and __id in ["13"]:	cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))
					if linhas !=1 and __id in ["18"] and par.ordenQ.GetValue():	cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))
					
					if linhas >= pular:
						
						if __id == "13":	lcampo += 8
						if   __id == "18":	cabccnf( True if par.ordenQ.GetValue() else False )
						else:
							
							cabccnf( False if __id in ["17"] and par.ananal.GetValue() else True )

						
						mdl.rodape(cv,rd1,'','','','','','','','',6)

						pg +=1
						cv.addPageLabel(pg)
						cv.showPage()						
						linhas = 1
						lcampo = 515
						ccampo = 525
							
						cabccnf(False)

						if __id == "15":
							
							cv.setFont('Helvetica', 7)
							cv.setFillColor(HexColor('0x000000'))
							cv.drawString(600,528, "Origem         Destino")


			if __id == "17" and par.ananal.GetValue():
				
				cabccnf( False )
				cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))

			elif __id == "18" and par.ordenQ.GetValue():	cabccnf( True )
				
			else:	cabccnf( True if __id not in ["05","900","18"] else False )
				
			if __id in ["05","900","18"]:	cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))
			mdl.rodape(cv,rd1,'','','','','','','','',6)
			cv.save()
			
			del _mensagem

			gerenciador.TIPORL = ''
			gerenciador.Anexar = nomeArquivo
			gerenciador.imprimir = True
			gerenciador.Filial   = Filial
				
			ger_frame=gerenciador(parent=par,id=-1)
			ger_frame.Centre()
			ger_frame.Show()

class RelatoriosCaixa:
	
	def rldiversos(self,mdl,par,_di,_df,__id, Filiais = "" ):

		def cabccnf(_separa):

			""" Cabecalho """
			pag = str(pg).zfill(3)
			if relator == "01":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filiais ,"CAIXA: DEVOLUÇÔES",2)
			if relator == "02":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filiais ,"CAIXA: DAVs",2)
			if relator == "03":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filiais ,"CAIXA: BANDEIRAS",2)
			if relator == "08":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filiais ,"CAIXA: COMISSÃO",2)
			if relator == "10":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filiais ,"CAIXA: D O F",2)
			if relator == "11":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filiais ,"CAIXA: COMISSÃO",2)
			if relator == "12":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filiais ,"CAIXA: COMISSÃO",2)
			if relator == "14":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filiais ,"CAIXA: EFETIVADOS",2)
			if relator == "15":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filiais ,"CAIXA: Vendas",2)
			if relator == "16":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filiais ,"CAIXA: F R E T E",2)
			if relator == "90":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filiais ,"NFes Emitidas",2)
			if relator == "91":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filiais ,"C F O P "+str( par.relacacop.GetValue().split('-')[0] ),2)

			if relator == "01":

				cv.setFillColor(HexColor('0x636363'))
				cv.drawString(200,33,"Valor Total:")
				cv.drawString(330,33,"Valor em Aberto:")
				cv.drawString(200,23,"Valor Recebido:")
				cv.drawRightString(320, 33,format(par.ToTalGeral,','))
				cv.drawRightString(460, 33,format(par.ToTalAbert,','))
				cv.drawRightString(320, 23,format(par.ToTalReceb,','))

				cv.drawString(475,33,"CR-Conta Corrente:")
				cv.drawString(475,23,"DB-Conta Corrente:")
				cv.drawRightString(610, 33,format(par.contacre,','))
				cv.drawRightString(610, 23,format(par.contadeb,','))
				cv.setFillColor(HexColor('0x000000'))

			if relator == "08":

				cv.setFillColor(HexColor('0x636363'))
				cv.drawString(200,33,"Valor de vendas:")
				cv.drawString(200,23,"Desconosto de vendas:")
				cv.drawString(395,23,"Devoluções:")
				cv.drawString(530,23,"Descontos de Devoluções:")
				cv.drawString(395,33,"Saldo Final:")
				cv.setFillColor(HexColor('0x000000'))
				cv.drawRightString(377,33,format( par.com_vendas_produtos,','))
				cv.drawRightString(377,23,format( par.com_vendas_desconto,','))
				cv.drawRightString(510,23,format( par.com_devolu,','))
				cv.drawRightString(685,23,format( par.com_devolu_desconto,','))
				
				cv.drawRightString(510,33,format( par.com_saldo,','))


			if relator == "11":

				cv.setFillColor(HexColor('0x636363'))
				cv.drawString(200,33,"Produtos: Valor Total:")
				cv.drawString(200,23,"Produtos: Valor Descontos:")

				cv.drawString(380,33,"Devolução: Valor Total:")
				cv.drawString(380,23,"Devolução: Valor Descontos:")
				
				cv.drawString(580,33,"Comissão: Produtos:")
				cv.drawString(580,23,"Comissão: Devolução:")
				cv.drawRightString(818, 33, "Saldo de Comissão")

				cv.setFillColor(HexColor('0x000000'))
				cv.drawRightString(375, 33,format( par.com_vendas_produtos,','))
				cv.drawRightString(375, 23,format( par.com_vendas_desconto,','))

				cv.drawRightString(575, 33,format( par.com_devolu,','))
				cv.drawRightString(575, 23,format( par.com_devolu_desconto,','))

				cv.drawRightString(725, 33,format( par.com_vlr_comissao_vendas,','))
				cv.drawRightString(725, 23,format( par.com_vlr_comissao_devolu,','))
				cv.drawRightString(818, 23,format( par.com_saldo_comissao,','))

				cv.setFillColor(HexColor('0x000000'))

			if relator == "12":

				cv.setFillColor(HexColor('0x636363'))
				cv.drawString(200,33,"Recebimentos em Dinheiro:")
				cv.drawString(370,33,"Recebimentos Areceber:")
				cv.drawString(520,33,"Total Devoluções:")
				cv.drawString(650,33,"Comissão Cartão:")
				cv.drawString(200,23,"Saldo de Recebimentos:")
				cv.drawString(370,23,"Comissão Vendas:")
				cv.setFillColor(HexColor('0x000000'))
				if par.dinheiro:	cv.drawRightString(357, 33,format( par.dinheiro,','))
				if par.ToTalReceb:	cv.drawRightString(510, 33,format( par.ToTalReceb,','))
				if par.ToTalDevol:	cv.drawRightString(640, 33,format( par.ToTalDevol,','))
				if par.cartao_comissao:	cv.drawRightString(740, 33,format( par.cartao_comissao,','))
				if par.TotalGeral:	cv.drawRightString(357, 23,format( par.TotalGeral,','))
				cv.drawRightString(510, 23,par.vendas_comissao )
				cv.setFillColor(HexColor('0x000000'))

			if relator == "14":

				cv.setFillColor(HexColor('0x636363'))
				cv.drawString(200,33,"Valor Total Recebimentos Avista:")
				cv.drawString(200,23,"Valor Total Contas AReceber:")
				cv.drawString(400,33,"Valor Total Devoluçoes:")
				cv.drawString(400,23,"S  a  l  d  o:")

				cv.drawString(570,33,"ComissaoCartao:")
				cv.drawString(570,23,"Liquido:")

				cv.setFillColor(HexColor('0x000000'))
				cv.drawRightString(390, 33,format( par.EfeDinhe,','))
				cv.drawRightString(390, 23,format( par.EfeReceb,','))
				cv.drawRightString(560, 33,format( par.EfeDevol,','))

				saldo = ( ( par.EfeDinhe + par.EfeReceb ) - par.EfeDevol )
				cv.drawRightString(560, 23,format( saldo,','))

				saldo_liquido = format( Decimal( format( ( saldo - Decimal( par.cartao_comissao ) ), '.2f' ) ), ',' )
				cv.drawRightString(700, 33,format( par.cartao_comissao,',') )
				cv.drawRightString(700, 23, saldo_liquido )

			if relator == "16":

				cv.setFillColor(HexColor('0x636363'))
				cv.drawString(255,33,"Frete sem rateio:")
				cv.drawString(255,23,"Frete com rateio:")
				cv.drawString(500,33,"Valor total do frete:")
				cv.setFillColor(HexColor('0x000000'))
				if par.rtickete:	cv.drawRightString(477, 33,format( par.rtickete,','))
				if par.vlrfrete:	cv.drawRightString(477, 23,format( par.vlrfrete,','))
				cv.drawRightString(677, 33,format( ( par.rtickete + par.vlrfrete ),','))

			if relator == "90":

				cv.setFont('Helvetica', 6)
				cv.setFillColor(HexColor('0x000000'))
				cv.drawString(670,33,"1-Emitida     2-NFCes p/Inutilizar 3-Cancelado")
				cv.drawString(670,23,"4-Inutilizada 5-Denegado")

				cv.setFont('Helvetica', 8)
				cv.setFillColor(HexColor('0x636363'))
				cv.drawString(210,33,"Emitidas:")
				cv.drawString(210,23,"Canceladas:")
				cv.drawString(330,33,"p/Inutilizar:")
				cv.drawString(330,23,"Inutilizadas:")
				cv.drawString(450,33,"Denegado:")
				cv.drawString(450,23,"Contigencia:")
				
				cv.setFillColor(HexColor('0x000000'))

				cv.drawRightString(320, 33, par.TTEmi.GetValue() )
				cv.drawRightString(320, 23, par.TTCan.GetValue() )

				cv.drawRightString(440, 33, par.TTpIn.GetValue() )
				cv.drawRightString(440, 23, par.TTInu.GetValue() )

				cv.drawRightString(560, 33, par.TTDen.GetValue() )
				cv.drawRightString(560, 23, par.TTCon.GetValue() )

			if relator == "91":

				cv.setFont('Helvetica', 6)
				cv.setFillColor(HexColor('0x000000'))
				cv.drawString(170,33,(" "*26)+"Valor total do icms: ")
				cv.drawString(370,33,(" "*26)+"Valor total dos produtos: ")
				cv.drawString(170,23,"valor total da substituição tributaria:")

				if par.cfops_totaliza_icms:	cv.drawRightString(330, 33, format( par.cfops_totaliza_icms, ',' ) )
				if par.cfops_totaliza_st:	cv.drawRightString(330, 23, format( par.cfops_totaliza_st, ',' ) )
				if par.cfops_totaliza_produtos:	cv.drawRightString(530, 33, format( par.cfops_totaliza_produtos, ',' ) )

			""" Titulo de Cabecalho """
			cb1= cb2= cb3= cb4= cb5= cb6= cb7= cb8= cb9= cb10= cb11= cb12=''
			
			if   relator == "90":	_Tipo = "Notas fiscais: "+ par.nemitidas.GetValue() +"  "+par.TipoNotas.GetValue()+"  "+par.NFesNFCes.GetValue()
			elif relator == "91":	_Tipo = u"Apuração do CFOF: "+ par.relacacop.GetValue().split('-')[0]+'   Filtro: '+par.nemitidas.GetValue().split('-')[1]+'   '+par.TipoNotas.GetValue().split('-')[1]+'   '+par.NFesNFCes.GetValue().split('-')[1]
			
			else:	_Tipo = par.relator.GetValue()
			
			if relator not in ["90","91"] and par.Todosla.GetValue() == True:	_Tipo += " { Todos }"
			if relator not in ["90","91"] and par.recebid.GetValue() == True:	_Tipo += " { Recebidos }"	
			if relator not in ["90","91"] and par.aberTos.GetValue() == True:	_Tipo += " { Abertos }"
			if relator not in ["90","91"] and par.esTorno.GetValue() == True:	_Tipo += " { Estornados }"
			if relator not in ["90","91"] and par.cancela.GetValue() == True:	_Tipo += " { Cancelados }"

			if relator not in ["90","91"] and par.motivod.GetValue() !='':	_Tipo +="  Motivo: "+str( par.motivod.GetValue() )
			if relator not in ["90","91"] and par.vendedo.GetValue() !='':	_Tipo +="  Vendedor: "+str( par.vendedo.GetValue() )
			if relator not in ["90","91"] and par.caixarc.GetValue() !='':	_Tipo +="  Caixa: "+str( par.caixarc.GetValue() )
			if relator not in ["90","91"] and par.motcanc.GetValue() !='':	_Tipo +="  Motivo do Cancelamento: "+str( par.motcanc.GetValue() )
			if relator not in ["90","91"] and par.fFilial.GetValue() == True:	_Tipo +=(" "*10)+"Filial: "+str( Filiais )
			
			rel = u'Usuário: '+ login.usalogin +u"  PERÌODO: "+cIni+" A "+cFim+(" "*10)+_Tipo
			cb1 = "22|540|Filial|"
			cb2 = "50|540|Nº DAV|#7F7F7F"
				
			if relator == "01":
				
				cb3  =  "110|540|DAV Vinculado|#7F7F7F"
				cb4  =  "170|540|Descrição do Cliente|"
				cb5  =  "420|540|Emissão|"
				cb6  =  "545|540|Recebimento|"
				cb7  =  "670|540|Valor|"
				cb8  =  "720|540|Motivo da Devolução|"

			elif relator == "02" or relator == "03":
				
				cb3  =  "110|540|Emissão|#7F7F7F"
				if par.cancela.GetValue():	cb3  =  "110|540|Emissão-cancelados|#7F7F7F"
				cb4  =  "250|540|Recebimento|"
				cb5  =  "390|540|Descrição do Cliente|"
				
				if relator == "03":

					cb6  =  "650|540|Valor|"
					cb7  =  "700|540|Vlr Recebido|"
					cb8  =  "750|540|Forma Recebimento|"

				if relator == "02":	cb6  =  "650|540|Recebimentos|"

			elif relator in ["08","11"]:
				
				cb1  =   "22|540|Vendas-Recebimentos|#7F7F7F"
				cb2  =  "112|540|Valor vendas||R"
				cb3  =  "202|540|Descontos vendas||R"
				cb4  =  "292|540|Devolução||R"
				cb5  =  "382|540|Descontos devolução||R"
				cb6  =  "472|540|Saldo||R"
				cb7  =  "562|540|Observação|"

				if relator == "11":

					cb7  =  "557|540|Comissão vendas||R"
					cb8  =  "650|540|Comissão devolução||R"
					cb9  =  "754|540|Saldo de comissão|"

			elif relator == "10":
				
				cb1 =  "22|540|Vendas-Recebimentos|"
				cb2 = "100|540|Total de vendas avista|#7F7F7F|R"
				cb3 = "200|540|Total do contas areceber|#7F7F7F|R"
				cb4 = "300|540|Total de devoluções|#7F7F7F|R"
				cb5 = "400|540|S a l d o|#7F7F7F|R"
				cb6 = "500|540|Observação|#7F7F7F"

			elif relator == "12":
				
#				cb1 =  "22|540|Vendas-Recebimentos|"
#				cb2 = "100|540|Total de vendas avista|#7F7F7F|R"
#				cb3 = "200|540|Total do contas areceber|#7F7F7F|R"
#				cb4 = "300|540|Total de devoluções|#7F7F7F|R"
#				cb5 = "400|540|S a l d o|#7F7F7F|R"
#				cb6 = "500|540|Observação|#7F7F7F"

				cb1 =  "22|540|Vendas-Recebimentos|"
				cb2 = "100|540|Total de vendas avista|#7F7F7F|R"
				cb3 = "200|540|Total do contas areceber|#7F7F7F|R"
				cb4 = "300|540|Total de devoluções|#7F7F7F|R"
				cb5 = "400|540|Comissão cartão|#7F7F7F|R"
				cb6 = "500|540|S a l d o|#7F7F7F|R"
				cb7 = "600|540|Observação|#7F7F7F"

			elif relator == "14":

#				cb1 =  "22|540|Login|"
#				cb2 = "110|540|Nome Usuario [ Vendedor ]|"
#				cb3 = "390|540|Recebimentos Avista|"
#				cb4 = "480|540|Recebimentos Contas AReceber|"
#				cb5 = "600|540|Devoluçoes|"
#				cb6 = "710|540|Saldo|"

				cb1 =  "22|540|Login|"
				cb2 =  "90|540|Nome Usuario [ Vendedor ]|"
				cb3 = "270|540|Avista|"
				cb4 = "350|540|Contas AReceber|"
				cb5 = "430|540|Devoluçoes|"
				cb6 = "510|540|Saldo|"
				cb7 = "590|540|ComissaoCartao|"
				cb8 = "670|540|Liquido|"
				cb9 = "750|540|ComissaoVendas|"

			elif relator == "15":

				cb1 =  "22|540|NºDAV|"
				cb2 =  "80|540|Emissão|"
				cb3 = "200|540|Recebimento|"
				cb4 = "340|540|Descrição do Cliente|"
				cb5 = "600|540|R e c e b i m e n t o s|"

			elif relator == "16":

				cb1 =  "22|540|Filial|"
				cb2 =  "54|540|Nº DAV|"
				cb3 = "117|540|Nº NF|"
				cb4 = "165|540|Emissão|"
				cb5 = "213|540|Recebimento|"
				cb6 = "260|540|Descrição dos clientes|"
				cb7 = "600|540|Valor do dav||R"
				cb8 = "665|540|Valor do frete||R"
				cb9 = "720|540|Rateio do frete|"

			elif relator == "90":

				cb1 =  "22|540|Filial|"
				cb2 =  "75|540|Nº DAV|"
				cb3 = "138|540|Emissão-Envio|"
				cb4 = "260|540|Nº NFes|"
				cb5 = "295|540|Retorno SEFAZ|"
				cb6 = "400|540|Descricao do Cliente|"
				cb7 = "700|540|Valor DAV|"
				cb8 = "755|540|Tipo|"

			elif relator == "91":

				cb1 =  "22|540|Filial|"
				cb2 =  "75|540|Nº DAV|"
				cb3 = "138|540|Emissão-Envio|"
				cb4 = "260|540|Nº NFes|"
				cb5 = "295|540|Retorno SEFAZ|"
				cb6 = "400|540|Descricao do Cliente|"
				cb7 = "700|540|Valor DAV|"
				cb8 = "755|540|Tipo|"


			if _separa == False:	mdl.mtitulo(rel,cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12,7,2)
			else:

				cv.line((float(cb2.split('|')[0])-2), float(ccampo), (float(cb2.split('|')[0])-2), float(lcampo))
				cv.line((float(cb3.split('|')[0])-2), float(ccampo), (float(cb3.split('|')[0])-2), float(lcampo))
				cv.line((float(cb4.split('|')[0])-2), float(ccampo), (float(cb4.split('|')[0])-2), float(lcampo))
				cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float(lcampo))
				if relator in ["02","14","12","08","11","90","16"]:	cv.line((float(cb6.split('|')[0])-2), float(ccampo), (float(cb6.split('|')[0])-2), float(lcampo))

				#lsT = ["14","15","02","12","08","10"]
				lsT = ["15","02","12","08","10"]
				if relator not in lsT:	cv.line((float(cb7.split('|')[0])-2), float(ccampo), (float(cb7.split('|')[0])-2), float(lcampo))
				if relator not in lsT:	cv.line((float(cb8.split('|')[0])-2), float(ccampo), (float(cb8.split('|')[0])-2), float(lcampo))
				if relator in ["08"]:	cv.line((float(cb7.split('|')[0])-2), float(ccampo), (float(cb7.split('|')[0])-2), float(lcampo))
				if relator in ["14","11","16"]:	cv.line((float(cb9.split('|')[0])-2), float(ccampo), (float(cb9.split('|')[0])-2), float(lcampo))
				#if relator in ["11","16"]:	cv.line((float(cb9.split('|')[0])-2), float(ccampo), (float(cb9.split('|')[0])-2), float(lcampo))

				#-----: Linha Final
				cv.line(20,float(lcampo),820,float(lcampo))

		#----------------------------: Emissao do Relatorio :-----------------------------:
		self.T  = truncagem()
		if   __id == "90":	relator, registros = "90", par.gerenciaNfe.GetItemCount()
		elif __id == "91":	relator, registros = "91", len( par.listar_compras.split('</>') )
		else:	relator, registros = par.relator.GetValue()[:2], par.DEVconfs.GetItemCount()
		
		if registros !=0:

			""" Selecionar opcao para Resumido """
			passar = True
			if relator not  in ["90","91"] and par.comissao_resumidos.GetValue() == True:	passar = False

			if relator == "11":
				
				if relator == "11":	resum = wx.MessageDialog(par,"Relatorio de Comissão p/Produtos\n\nConfirme para relatorio resumido...\n"+(" "*100),"Caixa: Relatorio de Comissão",wx.YES_NO|wx.YES_DEFAULT)

			_mensagem = mens.showmsg("Caixa: Montando Relatório\nAguarde...")

			cIni = datetime.datetime.strptime(_di.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			cFim = datetime.datetime.strptime(_df.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			
			dh  = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
			pg  = 1
			
			if relator == "01":	nomeArquivo = diretorios.usPasta+"devolucao_"+login.usalogin.lower()+".pdf"
			if relator == "02":	nomeArquivo = diretorios.usPasta+"emissaoDav_"+login.usalogin.lower()+".pdf"
			if relator == "03":	nomeArquivo = diretorios.usPasta+"bandeiras_"+login.usalogin.lower()+".pdf"
			if relator == "08":	nomeArquivo = diretorios.usPasta+"comissaoVendas_"+login.usalogin.lower()+".pdf"
			if relator == "10":	nomeArquivo = diretorios.usPasta+"dof_"+login.usalogin.lower()+".pdf"
			if relator == "11":	nomeArquivo = diretorios.usPasta+"comissaoProdutos_"+login.usalogin.lower()+".pdf"
			if relator == "12":	nomeArquivo = diretorios.usPasta+"comissaoRecebido_"+login.usalogin.lower()+".pdf"
			if relator == "14":	nomeArquivo = diretorios.usPasta+"efetivados_"+login.usalogin.lower()+".pdf"
			if relator == "15":	nomeArquivo = diretorios.usPasta+"geralvendasRecebimentos_"+login.usalogin.lower()+".pdf"
			if relator == "16":	nomeArquivo = diretorios.usPasta+"fretes_"+login.usalogin.lower()+".pdf"
			if relator == "90":	nomeArquivo = diretorios.usPasta+"nfesemitidas_"+login.usalogin.lower()+".pdf"
			if relator == "91":	nomeArquivo = diretorios.usPasta+"apuracaocfop_"+login.usalogin.lower()+".pdf"
			
			cv = canvas.Canvas(nomeArquivo, pagesize=landscape(A4))
			cabccnf(False)
			
			lcampo = 515
			ccampo = 525
			linhas = 1

			if   relator == '90':	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+ "(Relatorio:Notas Fiscais Emitidas)|"
			elif relator == '91':	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+ "(Relatorio:Apuração do ICMS,ST)|"
			else:	rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio:'+str( relator )+')|'
			
			Indice = 0
			
			if relator in ["11","12","08"] and passar == False:


				mediads = mediacm = mediadv = Decimal('0.00')
				mediadd = mediacd = Decimal("0.00")
				if relator == "11" and par.com_vendas_produtos !=0 and par.com_vlr_comissao_vendas !=0:	mediacm = self.T.trunca( 5, ( par.com_vlr_comissao_vendas / par.com_vendas_produtos * 100 ) )
				if relator == "11" and par.com_vendas_produtos !=0 and par.com_vendas_desconto !=0:	mediads = self.T.trunca( 5, ( par.com_vendas_desconto / par.com_vendas_produtos * 100 ) )

				if relator == "11" and par.vendVpro !=0 and par.VToTalCo !=0:	mediacm = self.T.trunca( 5, ( par.VToTalCo / par.vendVpro * 100 ) )
				if relator == "11" and par.com_vendas_produtos !=0 and par.com_devolu !=0:	mediadv = self.T.trunca( 5, ( par.com_devolu / par.com_vendas_produtos * 100 ) )

				if relator == "11" and par.com_devolu_desconto !=0 and par.com_devolu !=0:		mediadd = self.T.trunca( 5, ( par.com_devolu_desconto / par.com_devolu * 100 ) )
				if relator == "11" and par.com_vlr_comissao_devolu !=0 and par.com_devolu !=0:	mediacd = self.T.trunca( 5, ( par.com_vlr_comissao_devolu / par.com_devolu * 100 ) )


				if relator == "11":

					cv.rect(20,375,420,120,  fill=0) #-->[ Quadro do Cabecalho]
					cv.line(20,395,440,395)
				else:	cv.rect(20,375,420,120,  fill=0) #-->[ Quadro do Cabecalho]

				cv.line(20,477,440,478)
				cv.line(20,462,440,462)
				cv.line(20,447,440,447)
				cv.line(20,432,440,432)
				cv.line(20,417,440,417)

				cv.line(280,495,280,417)
				if relator !="08":	cv.line(370,495,370,417)
				
				if relator == "11":
					
					cv.setFont('Helvetica-Bold', 10)
					cv.setFillColor(HexColor('0x1E5182'))
					cv.drawString(30,480,"Produtos: Produtos")
					cv.drawString(30,465,"Produtos: Descontos")
					cv.drawString(30,420,"Comissão: Produtos")

					cv.setFillColor(HexColor('0xB11C1C'))
					cv.drawString(30,450,"Devolução: Produtos")
					cv.drawString(30,435,"Devolução: Descontos")
					cv.drawString(30,405,"Comissão: Devolução")


					cv.setFillColor(HexColor('0x0E0EB1'))
					cv.drawString(30,380,"Saldo de Comissão: ")
					cv.drawRightString(368, 380,format( par.com_saldo_comissao,','))

					cv.setFillColor(HexColor('0x1E5182'))
					cv.drawRightString(368, 480,format( par.com_vendas_produtos,','))
					cv.drawRightString(368, 465,format( par.com_vendas_desconto,','))
					cv.drawRightString(368, 420,format( par.com_vlr_comissao_vendas,','))
					cv.drawRightString(437, 465, str( mediads ) + " %" ) #-: Media de desconto
					cv.drawRightString(437, 420, str( mediacm ) + " %" ) #-: Media de comissao de prodtos

					cv.setFillColor(HexColor('0xB11C1C'))
					cv.drawRightString(368, 450,format( par.com_devolu,','))
					cv.drawRightString(368, 435,format( par.com_devolu_desconto,','))
					cv.drawRightString(368, 405,format( par.com_vlr_comissao_devolu,','))

					cv.drawRightString(437, 450, str( mediadv ) + " %" ) #-: Media de devolucao de produtos
					cv.drawRightString(437, 435, str( mediadd ) + " %" ) #-: Media de desconto de devolucao
					cv.drawRightString(437, 405, str( mediacd ) + " %" ) #-: Media de comissao de devolucao


				if par.relator.GetValue() == "08":
					
					cv.setFont('Helvetica-Bold', 10)
					cv.setFillColor(HexColor('0x1E5182'))
					cv.drawString(30,480,"a - Valor de vendas")
					cv.drawString(30,465,"b - Desconto de vendas")
					cv.drawString(30,450,"c - Valor de Devoluçoess")
					cv.drawString(30,435,"d - Valor de Devoluçoess")
					cv.drawString(30,400,"Saldo Final")

					cv.drawRightString(425,480,format( par.com_vendas_produtos,','))
					cv.drawRightString(425,465,format( par.com_vendas_desconto,','))
					cv.drawRightString(425,450,format( par.com_devolu,','))
					cv.drawRightString(425,435,format( par.com_devolu_desconto,','))
					cv.drawRightString(425,400,format( par.com_saldo,','))
				
				if relator == "12":
					
					cv.setFont('Helvetica-Bold', 10)
					cv.setFillColor(HexColor('0x1E5182'))
					cv.drawString(30,480,"a - Vendas com recebimentos em dinheiro")
					cv.drawString(30,465,"b - Recebimentos do contas areceber")
					cv.drawRightString(368,480,format( par.dinheiro,','))
					cv.drawRightString(368,465,format( par.ToTalReceb,','))

					cv.drawString(30,450,"Total de recebimentos ( a + b )")
					cv.drawRightString(368, 450,format( ( par.dinheiro + par.ToTalReceb ),','))

					cv.drawString(30,405,"Saldo de recebimentos ( a + b - c - d )")
					cv.drawRightString(368, 405,format( par.TotalGeral,','))
					
					cv.setFillColor(HexColor('0xB11C1C'))
					cv.drawString(30,435,"c - Valor total de devoluçoes")
					cv.drawString(30,420,"d - Comissão do cartão")
					if par.ToTalDevol:	cv.drawRightString(368, 435,format( par.ToTalDevol,','))
					if par.cartao_comissao:	cv.drawRightString(368, 420,format( par.cartao_comissao,','))

					cv.setFillColor(HexColor('0x1E5182'))
					cv.drawString(30,385,"Comissão de vendas")
					if par.vendas_comissao:	cv.drawRightString(368, 385,par.vendas_comissao)

					md1 = md2 = md3 = Decimal("0.00")
					if par.ToTalDevol > 0 and par.dinheiro > 0:	md1 = self.T.trunca( 5, ( par.dinheiro / par.TotalGeral * 100 ) )
					if par.ToTalDevol > 0 and par.ToTalReceb > 0:	md2 = self.T.trunca( 5, ( par.ToTalReceb / par.TotalGeral * 100 ) )
					if par.ToTalDevol > 0 and par.ToTalDevol > 0:	md3 = self.T.trunca( 5, ( par.ToTalDevol / par.TotalGeral * 100 ) )

					cv.setFillColor(HexColor('0x158AB0'))
					if md1:	cv.drawRightString(437, 480, str( md1 ) + " %" )
					if md2:	cv.drawRightString(437, 465, str( md2 ) + " %" )
					if md3:	cv.drawRightString(437, 435, str( md3 ) + " %" )

			
			"""   Davs Emitidos p/Forma de Pagamnto   """
			if relator == "02" and par.fpagame.GetValue() !="":

				cv.setFont('Helvetica-Bold', 7)
				cv.drawRightString(730, float(526), par.fpagame.GetValue() )				
				cv.drawRightString(817, float(526), "DAV:Valor Recebido" )
	
			if passar == True:

				lancamentos = 0
				for r in range( registros ):

					lancamentos +=1
					_venc = par.DEVconfs.GetItem(Indice,2).GetText() if relator not in ['90','91'] else ''
					
					_emis = _rece = ''
					_prin = True

					cv.setFont('Helvetica', 7)
					if relator not in ["14","15","12","08","11","90","10","16","91"]:
						
						if relator != "13":

							if par.DEVconfs.GetItem(Indice,2).GetText() !='':	_emis = par.DEVconfs.GetItem(Indice,2).GetText().split(' ')[0]+" "+par.DEVconfs.GetItem(Indice,2).GetText().split(' ')[2]
							if par.DEVconfs.GetItem(Indice,3).GetText() !='':	_rece = par.DEVconfs.GetItem(Indice,3).GetText().split(' ')[0]+" "+par.DEVconfs.GetItem(Indice,3).GetText().split(' ')[2]

							if par.DEVconfs.GetItem(Indice,9).GetText() == '2':	cv.setFillColor(HexColor('0xDCDC02'))
							if par.DEVconfs.GetItem(Indice,9).GetText() == '3':	cv.setFillColor(HexColor('0xA52A2A'))

						cv.setFont('Helvetica', 6.5)

						cv.setFillColor(HexColor('0x000000'))
						cv.drawString(22,  float(lcampo), par.DEVconfs.GetItem(Indice,0).GetText() )

						cv.setFont('Helvetica', 7)
						cv.setFillColor(HexColor('#7F7F7F'))
						cv.drawString(50,  float(lcampo), par.DEVconfs.GetItem(Indice,1).GetText() )
						cv.setFillColor(HexColor('0x000000'))

					if relator == "14":

						cv.setFont('Helvetica', 8)
						cv.drawString(22,  float(lcampo), par.DEVconfs.GetItem(r,0).GetText() )
						cv.drawString(92, float(lcampo), par.DEVconfs.GetItem(r,1).GetText() )
						cv.drawRightString(346, float(lcampo), par.DEVconfs.GetItem(r,2).GetText() )
						cv.drawRightString(426, float(lcampo), par.DEVconfs.GetItem(r,3).GetText() )
						cv.drawRightString(504, float(lcampo), par.DEVconfs.GetItem(r,4).GetText() )
						cv.drawRightString(586, float(lcampo), par.DEVconfs.GetItem(r,5).GetText() )
						if Decimal( par.DEVconfs.GetItem(r,6).GetText().replace(',','') ):	cv.drawRightString(666, float(lcampo), par.DEVconfs.GetItem(r,6).GetText() )
						if Decimal( par.DEVconfs.GetItem(r,7).GetText().replace(',','') ):	cv.drawRightString(746, float(lcampo), par.DEVconfs.GetItem(r,7).GetText() )
						cv.setFont('Helvetica', 6)
						cv.drawRightString(818, float(lcampo), par.DEVconfs.GetItem(r,8).GetText() )
						cv.setFont('Helvetica', 8)

						#						cv.setFont('Helvetica', 8)
						#						cv.drawString(22,  float(lcampo), par.DEVconfs.GetItem(r,0).GetText() )
						#						cv.drawString(112, float(lcampo), par.DEVconfs.GetItem(r,1).GetText() )
						#						cv.drawRightString(476, float(lcampo), par.DEVconfs.GetItem(r,2).GetText() )
						#						cv.drawRightString(596, float(lcampo), par.DEVconfs.GetItem(r,3).GetText() )
						#						cv.drawRightString(706, float(lcampo), par.DEVconfs.GetItem(r,4).GetText() )
						#						cv.drawRightString(817, float(lcampo), par.DEVconfs.GetItem(r,5).GetText() )

					if relator == "15":

						cv.setFont('Helvetica', 7)
						cv.drawString(22,  float(lcampo), par.DEVconfs.GetItem(r,1).GetText() )
						cv.drawString(82,  float(lcampo), par.DEVconfs.GetItem(r,2).GetText() )
						cv.drawString(202, float(lcampo), par.DEVconfs.GetItem(r,3).GetText() )
						cv.drawString(322, float(lcampo), par.DEVconfs.GetItem(r,4).GetText() )

						cv.setFillColor(HexColor('0x6B6666'))
						cv.drawString(322, float(lcampo)-10, "Valor Total do DAV:")
						cv.drawString(322, float(lcampo)-19, "Valor do Recebido:")
						cv.drawString(432, float(lcampo)-10, "Valor Troco:")
						cv.drawString(432, float(lcampo)-19, "Transferencia C/C:")

						TipoDav = "{ Aberto }"
						if par.DEVconfs.GetItem(r,20).GetText() == "1":

							TipoDav = "{ 1-Recebido }"
							cv.setFillColor(HexColor('0x1E4E7C'))

						if par.DEVconfs.GetItem(r,20).GetText() == "2":	TipoDav = "{ 2-Estornado }"
						if par.DEVconfs.GetItem(r,20).GetText() == "3":

							TipoDav = "{ 3-Cancelado }"
							cv.setFillColor(HexColor('0xBB1717'))
							
						cv.drawString(202, float(lcampo)-17, TipoDav )
						cv.setFillColor(HexColor('0x000000'))

						cv.setFont('Helvetica-Bold', 7)
						if Decimal( par.DEVconfs.GetItem(r,16).GetText().replace(',','') ) > 0:	cv.drawRightString(420, float(lcampo)-10, par.DEVconfs.GetItem(r,16).GetText() ) #-: Total DAV
						if Decimal( par.DEVconfs.GetItem(r,17).GetText().replace(',','') ) > 0:	cv.drawRightString(420, float(lcampo)-19, par.DEVconfs.GetItem(r,17).GetText() ) #-: Total Recebimento
						if Decimal( par.DEVconfs.GetItem(r,18).GetText().replace(',','') ) > 0:	cv.drawRightString(550, float(lcampo)-10, par.DEVconfs.GetItem(r,18).GetText() ) #-: Total Troco
						if Decimal( par.DEVconfs.GetItem(r,19).GetText().replace(',','') ) > 0:	cv.drawRightString(550, float(lcampo)-19, par.DEVconfs.GetItem(r,19).GetText() ) #-: Transferencia CC
						cv.setFillColor(HexColor('0x000000'))

						"""   Recebimentos   """
						cv.setFont('Helvetica', 6)
						cv.drawString(599, float(lcampo)+2, "Dinheiro:")
						cv.drawString(654, float(lcampo)+2, "ChAvista:")
						cv.drawString(710, float(lcampo)+2, "Cheq-Pre:" )
						cv.drawString(768, float(lcampo)+2, "C.Dédito:" )

						cv.drawString(599, float(lcampo)-7, "C-Crédito:")
						cv.drawString(654, float(lcampo)-7, "Boleto:")
						cv.drawString(710, float(lcampo)-7, "Carteira:" )
						cv.drawString(768, float(lcampo)-7, "Finaceira:" )

						cv.drawString(599, float(lcampo)-17, "R.Local:")
						cv.drawString(654, float(lcampo)-17, "DepConta:")
						cv.drawString(710, float(lcampo)-17, "Tickete:" )
						cv.drawString(768, float(lcampo)-17, "PCrédito:" )

						cv.line(598,float(lcampo),820,float(lcampo))
						cv.line(598,float(lcampo)-10,820,float(lcampo)-10)

						cv.setFont('Helvetica-Bold', 6)
						if Decimal( par.DEVconfs.GetItem(r,5).GetText().replace(',','') ) > 0:	cv.drawRightString(652, float(lcampo)+2, par.DEVconfs.GetItem(r,5).GetText() ) #-: Dinheiro
						if Decimal( par.DEVconfs.GetItem(r,6).GetText().replace(',','') ) > 0:	cv.drawRightString(709, float(lcampo)+2, par.DEVconfs.GetItem(r,6).GetText() ) #-: Cheque Avista
						if Decimal( par.DEVconfs.GetItem(r,7).GetText().replace(',','') ) > 0:	cv.drawRightString(766, float(lcampo)+2, par.DEVconfs.GetItem(r,7).GetText() ) #-: Cheque Predatado

						if Decimal( par.DEVconfs.GetItem(r, 9).GetText().replace(',','') ) > 0:	cv.drawRightString(652, float(lcampo)-7, par.DEVconfs.GetItem(r, 9).GetText() ) #-: Cartao de Credito
						if Decimal( par.DEVconfs.GetItem(r,10).GetText().replace(',','') ) > 0:	cv.drawRightString(709, float(lcampo)-7, par.DEVconfs.GetItem(r,10).GetText() ) #-: Boleto
						if Decimal( par.DEVconfs.GetItem(r,11).GetText().replace(',','') ) > 0:	cv.drawRightString(766, float(lcampo)-7, par.DEVconfs.GetItem(r,11).GetText() ) #-: Carteira

						if Decimal( par.DEVconfs.GetItem(r,13).GetText().replace(',','') ) > 0:	cv.drawRightString(652, float(lcampo)-17, par.DEVconfs.GetItem(r,13).GetText() ) #-: Receber Local
						if Decimal( par.DEVconfs.GetItem(r,14).GetText().replace(',','') ) > 0:	cv.drawRightString(709, float(lcampo)-17, par.DEVconfs.GetItem(r,14).GetText() ) #-: DepConta
						if Decimal( par.DEVconfs.GetItem(r,15).GetText().replace(',','') ) > 0:	cv.drawRightString(766, float(lcampo)-17, par.DEVconfs.GetItem(r,15).GetText() ) #-: Tickete

						cv.setFont('Helvetica-Bold', 5.2)
						if Decimal( par.DEVconfs.GetItem(r, 8).GetText().replace(',','') ) > 0:	cv.drawRightString(819, float(lcampo)+2,  par.DEVconfs.GetItem(r, 8).GetText() ) #-: Cartao de Debito
						if Decimal( par.DEVconfs.GetItem(r,12).GetText().replace(',','') ) > 0:	cv.drawRightString(819, float(lcampo)-7,  par.DEVconfs.GetItem(r,12).GetText() ) #-: Financeira
						if Decimal( par.DEVconfs.GetItem(r,21).GetText().replace(',','') ) > 0:	cv.drawRightString(819, float(lcampo)-17, par.DEVconfs.GetItem(r,21).GetText() ) #-: PgTo Credito

					if relator == "01":

						cv.drawString(110, float(lcampo), par.DEVconfs.GetItem(Indice,6).GetText() )
						cv.drawString(170, float(lcampo), par.DEVconfs.GetItem(Indice,4).GetText() )
						cv.drawString(420, float(lcampo), _emis )
						cv.drawString(545, float(lcampo), _rece )
						cv.drawRightString(715, float(lcampo), par.DEVconfs.GetItem(Indice,5).GetText() )
						cv.drawString(720, float(lcampo), par.DEVconfs.GetItem(Indice,7).GetText() )

					elif relator == "02" or relator == "03":
						
						if par.DEVconfs.GetItem(Indice,9).GetText() == "3":	cv.setFillColor(HexColor('0xA52A2A'))
						else:	cv.setFillColor(HexColor('0x000000'))

						if par.cancela.GetValue() and relator == "02":	cv.setFont('Helvetica', 5) #-: Cancelados
					
						cv.drawString(110, float(lcampo), _emis )

						if par.cancela.GetValue() and relator == "02":	cv.drawRightString( 248, float(lcampo), par.DEVconfs.GetItem(Indice,8).GetText() ) #-: Data de cancelamento
						if par.cancela.GetValue() and relator == "02":	cv.setFont('Helvetica', 7) #-: Cancelados

						cv.drawString(250, float(lcampo), '{CANCELADO '+par.DEVconfs.GetItem(Indice,8).GetText()[:27]+'}' if par.DEVconfs.GetItem(Indice,9).GetText() == "3" else _rece )
						cv.drawString(390, float(lcampo+1), par.DEVconfs.GetItem(Indice,4).GetText() )

						cv.setFont('Helvetica', 7)

						if par.fpagame.GetValue() == "":

							cv.drawRightString(695, float(lcampo), par.DEVconfs.GetItem(Indice,5).GetText() )
							cv.drawRightString(745, float(lcampo), par.DEVconfs.GetItem(Indice,18).GetText() )

							cv.setFont('Helvetica', 6)
							cv.drawString(750, float(lcampo), par.DEVconfs.GetItem(Indice,13).GetText() )
							cv.setFont('Helvetica', 7)

						if relator == "02" and par.fpagame.GetValue() !="":
							
							cv.setFont('Helvetica', 6)
							vl = "0.00"
							if par.fpagame.GetValue() !="" and par.fpagame.GetValue().split("-")[0] == "01":	vl = par.DEVconfs.GetItem(Indice,17).GetText().split("|")[0]
							if par.fpagame.GetValue() !="" and par.fpagame.GetValue().split("-")[0] == "02":	vl = par.DEVconfs.GetItem(Indice,17).GetText().split("|")[1]
							if par.fpagame.GetValue() !="" and par.fpagame.GetValue().split("-")[0] == "03":	vl = par.DEVconfs.GetItem(Indice,17).GetText().split("|")[2]
							if par.fpagame.GetValue() !="" and par.fpagame.GetValue().split("-")[0] == "04":	vl = par.DEVconfs.GetItem(Indice,17).GetText().split("|")[3]
							if par.fpagame.GetValue() !="" and par.fpagame.GetValue().split("-")[0] == "05":	vl = par.DEVconfs.GetItem(Indice,17).GetText().split("|")[4]
							if par.fpagame.GetValue() !="" and par.fpagame.GetValue().split("-")[0] == "06":	vl = par.DEVconfs.GetItem(Indice,17).GetText().split("|")[5]
							if par.fpagame.GetValue() !="" and par.fpagame.GetValue().split("-")[0] == "07":	vl = par.DEVconfs.GetItem(Indice,17).GetText().split("|")[6]
							if par.fpagame.GetValue() !="" and par.fpagame.GetValue().split("-")[0] == "08":	vl = par.DEVconfs.GetItem(Indice,17).GetText().split("|")[7]
							if par.fpagame.GetValue() !="" and par.fpagame.GetValue().split("-")[0] == "09":	vl = par.DEVconfs.GetItem(Indice,17).GetText().split("|")[8]
							if par.fpagame.GetValue() !="" and par.fpagame.GetValue().split("-")[0] == "10":	vl = par.DEVconfs.GetItem(Indice,17).GetText().split("|")[9]
							if par.fpagame.GetValue() !="" and par.fpagame.GetValue().split("-")[0] == "11":	vl = par.DEVconfs.GetItem(Indice,17).GetText().split("|")[10]
							if par.fpagame.GetValue() !="" and par.fpagame.GetValue().split("-")[0] == "12":	vl = par.DEVconfs.GetItem(Indice,17).GetText().split("|")[11]
							
							cv.setFont('Helvetica', 9)
							cv.drawRightString(730, float(lcampo), format( Decimal( vl ), ',' ) )
							cv.drawRightString(817, float(lcampo), par.DEVconfs.GetItem(Indice,18).GetText() )
							cv.setFont('Helvetica', 7)
							
						if relator == "03" and par.DEVconfs.GetItem(Indice,16).GetText() !='':

							lCartao = par.DEVconfs.GetItem(Indice,16).GetText().split('|')
							qCartao = ( len(lCartao) - 1 )
							if par.DEVconfs.GetItem(Indice,19).GetText() == "2":	cv.setFillColor(HexColor('0xA52A2A'))
							if qCartao != 0:
								
								if linhas !=1:	cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))

								_col = 390
								_lnh = 0

								_prin   = False
								lcampo -= 10
								linhas +=1 

								vlComissao = Decimal( "0.0000" )
								for c in range(qCartao):
									
									cv.setFont('Helvetica', 5)
									bCartao = lCartao[c].split(';')
										
									__crT = bCartao[0]
									__ven = bCartao[1]
									__vlr = bCartao[2]
									__auT = bCartao[3]
									if Decimal( bCartao[4].replace( ",","" ) ) > 0:	vlComissao +=Decimal( bCartao[4] )

									if _lnh == 2:
											
										_col = 390
										_lnh = 0
										lcampo -= 15
										linhas +=1 
									cv.drawString(_col,     float(lcampo+5), u'( Nº Autorização: [ '+__auT+' ] )' )
									cv.drawString(_col,     float(lcampo-1), __crT )
									cv.drawString(_col+65,  float(lcampo-1), __ven )
									cv.drawString(_col+105, float(lcampo-1), __vlr )

									_col   +=130
									_lnh   +=1
									if linhas >= 45:

										lcampo -=5
										cabccnf(True)
										
										mdl.rodape(cv,rd1,'','','','','','','','',6)

										pg +=1
										cv.addPageLabel(pg)
										cv.showPage()						
										linhas = 1
										lcampo = 515
										ccampo = 525

										_col = 390
										_lnh = 0
											
										cabccnf(False)
										
								if vlComissao !=0:
									
									cv.setFillColor(HexColor('0x0B0BA8'))			
									cv.drawString(750, float(lcampo), u"Comissão: "+format( vlComissao,',' ) )
										
							cv.setFillColor(HexColor('0x000000'))			

						cv.setFont('Helvetica', 7)

					elif relator in ["08","11"]:
						
						dvr = par.DEVconfs.GetItem(r,0).GetText() #-: Data vendas,recebimento
						vpd = self.T.trunca( 3, Decimal( par.DEVconfs.GetItem(r,1).GetText().replace(",","" ) ) ) #-: valor vendas produtos
						vds = self.T.trunca( 3, Decimal( par.DEVconfs.GetItem(r,2).GetText().replace(",","" ) ) ) #-: descontos produtos
						dev = self.T.trunca( 3, Decimal( par.DEVconfs.GetItem(r,3).GetText().replace(",","" ) ) ) #-: devolucoes
						dds = self.T.trunca( 3, Decimal( par.DEVconfs.GetItem(r,4).GetText().replace(",","" ) ) ) #-: descontos devolucoes
						sal = self.T.trunca( 3, Decimal( par.DEVconfs.GetItem(r,5).GetText().replace(",","" ) ) ) #-: saldo de vendas

						com_vendas = com_devolu = com_saldo = Decimal("0.00")
						if relator == "11":
						
							com_vendas = Decimal( par.DEVconfs.GetItem(r,8).GetText().replace(",","" ) )
							com_devolu = Decimal( par.DEVconfs.GetItem(r,8).GetText().replace(",","" ) )
							com_saldo  = Decimal( par.DEVconfs.GetItem(r,8).GetText().replace(",","" ) )

						rvd = par.DEVconfs.GetItem(r,6).GetText() + par.DEVconfs.GetItem(r,7).GetText()#-: Relacao das vendas avista,receber,devolucao
						
						if par.comissao_analitico.GetValue() == True:	cv.setFont('Helvetica-Bold', 9)
						else:	cv.setFont('Helvetica', 9)

						cv.drawString(24, float(lcampo), dvr )

						if vpd !=0:	cv.drawRightString(198, float(lcampo), format( vpd,',' ) )
						if vds !=0:	cv.drawRightString(288, float(lcampo), format( vds,',' ) )
						if dev !=0:	cv.drawRightString(378, float(lcampo), format( dev,',' ) )
						if dds !=0:	cv.drawRightString(468, float(lcampo), format( dds,',' ) )
						if sal !=0:	cv.drawRightString(553, float(lcampo), format( sal,',' ) )
						
						if com_vendas !=0:	cv.drawRightString(646, float(lcampo), format( com_vendas,',' ) )
						if com_devolu !=0:	cv.drawRightString(750, float(lcampo), format( com_devolu,',' ) )
						if com_saldo  !=0:	cv.drawRightString(818, float(lcampo), format( com_saldo,',' ) )

						if par.comissao_analitico.GetValue() == True and rvd !="":

							linhas +=1
							lcampo -= 10

							cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ) )
							cv.line(20,( lcampo + 20),820,( lcampo + 20) )
							linhas +=1
							lcampo -= 10
							posicao = 46

							cv.setFillColor(HexColor('0x7F7F7F'))
							cv.setFont('Helvetica-Bold', 7)
							cv.drawString(30,  float(lcampo + 11 ), "Filial" )	
							cv.drawString(100, float(lcampo + 11 ), u"Nº DAV-Pedido" )	
							cv.drawString(180, float(lcampo + 11 ), u"Emisão { vendedor-caixa }" )

							if relator == "08":
								
								cv.drawString(290, float(lcampo + 11 ), "Baixa Recebimento { Caixa }" )	
								cv.drawString(410, float(lcampo + 11 ), "Valor Produto" )	
								cv.drawString(470, float(lcampo + 11 ), "Valor do Desconto" )	
								cv.drawString(565, float(lcampo + 11 ), "Valor Final" )	
								cv.drawString(608, float(lcampo + 11 ), u"Descrição do Cliente" )	

							elif relator == "11":

								cv.drawString(290, float(lcampo + 11 ), u"Descrição dos Produtos" )	
								cv.drawString(450, float(lcampo + 11 ), "Sub-Total do Produto" )	
								cv.drawRightString(710, float(lcampo + 11 ), "Sub-Total" )	
								cv.drawRightString(750, float(lcampo + 11 ), "Desconto" )	
								cv.drawRightString(818, float(lcampo + 11 ), "Comissão [ $ - % ]" )	

							_lancamentos = 0
							numero_lancamentos = 0
							for _rcc in rvd.split("\n"):
								if _rcc !="":	numero_lancamentos +=1	

							for rcc in rvd.split("\n"):

								cv.setFont('Helvetica', 8)
								cv.setFillColor(HexColor('0x000000'))

								if rcc !="":
									
									srcc = rcc.split(";")
									_lancamentos +=1

									if srcc[8].upper() == "DEVOLUCAO":	cv.setFillColor(HexColor('0xA52A2A'))

									cv.drawString(30,  float(lcampo), srcc[0] )
									cv.drawString(100, float(lcampo), srcc[1] )
									cv.setFont('Helvetica', 7)
									cv.drawString(180, float(lcampo), srcc[2] )
									cv.drawString(290, float(lcampo), srcc[3] )
									
									cv.setFont('Helvetica', 8)
									if relator == "08":

										cv.drawRightString(456, float(lcampo), srcc[5] )
										cv.drawRightString(532, float(lcampo), srcc[6] )
										cv.drawRightString(602, float(lcampo), srcc[7] )

										if len(srcc[4]) >= 44:	cv.setFont('Helvetica', 5.5)
										else:	cv.setFont('Helvetica', 7)
										
										cv.drawString(609, float(lcampo), srcc[4] )
										
									elif relator == "11":

										cv.drawRightString(710, float(lcampo), srcc[4] )
										cv.drawRightString(750, float(lcampo), srcc[5] )
										cv.drawRightString(818, float(lcampo), srcc[7] +' - '+ srcc[6]+' %' )
										
									cv.setFillColor(HexColor('0x000000'))

									linhas +=1
									lcampo -= 10
						
								if linhas >= posicao:
									
									cabccnf( False )
									mdl.rodape(cv,rd1,'','','','','','','','',6)

									pg +=1
									cv.addPageLabel(pg)
									cv.showPage()						
									linhas = 1
									lcampo = 515
									ccampo = 525

									cabccnf( False )
									
									if numero_lancamentos > _lancamentos:
										
										linhas +=1
										lcampo -= 10

										cv.setFillColor(HexColor('0x7F7F7F'))
										cv.setFont('Helvetica-Bold', 7)
										cv.drawString(30,  float(lcampo + 11 ), "Filial" )	
										cv.drawString(100, float(lcampo + 11 ), "Nº DAV-Pedido" )	
										cv.drawString(180, float(lcampo + 11 ), "Emisão { vendedor-caixa }" )

										if relator == "08":
											
											cv.drawString(290, float(lcampo + 11 ), "Baixa Recebimento { Caixa }" )	
											cv.drawString(410, float(lcampo + 11 ), "Valor Produto" )	
											cv.drawString(470, float(lcampo + 11 ), "Valor do Desconto" )	
											cv.drawString(565, float(lcampo + 11 ), "Valor Final" )	
											cv.drawString(608, float(lcampo + 11 ), "Descrição do Cliente" )	

										elif relator == "11":

											cv.drawString(290, float(lcampo + 11 ), "Descrição dos Produtos" )	
											cv.drawString(450, float(lcampo + 11 ), "Sub-Total do Produto" )	
											cv.drawRightString(710, float(lcampo + 11 ), "Sub-Total" )	
											cv.drawRightString(750, float(lcampo + 11 ), "Desconto" )	
											cv.drawRightString(818, float(lcampo + 11 ), "Comissão [ $ - % ]" )	

					elif relator == "10":

						if lcampo == 515:	lcampo = 505
						endereco = ast.literal_eval( par.DEVconfs.GetItem(r,5).GetText() ) if par.DEVconfs.GetItem(r,5).GetText() else ""
						
						_end1 = "1 - "+endereco[3]+', '+endereco[8]+' '+endereco[9] if endereco else ""
						_bai1 = endereco[4]+' '+endereco[5]+' CEP: '+endereco[7]+" UF: "+endereco[10]+" IBGE: "+endereco[6] if endereco else ""

						_end2 = "2 - "+endereco[11]+', '+endereco[16]+' '+endereco[17] if endereco and endereco[11] else ""
						_bai2 = endereco[12]+' '+endereco[13]+' CEP: '+endereco[15]+" UF: "+endereco[18]+" IBGE: "+endereco[6] if endereco and endereco[11] else ""

						cv.setFont('Helvetica-Bold', 7)
						cv.drawRightString(75,  float(lcampo), par.DEVconfs.GetItem(r,0).GetText() ) #-: Codigo do cliente
						cv.drawRightString(150, float(lcampo), par.DEVconfs.GetItem(r,1).GetText() ) #-: Documento
						cv.drawString(170, float(lcampo), par.DEVconfs.GetItem(r,2).GetText() ) #------: Descricao

						cv.setFont('Helvetica', 6)
						if _end1:	cv.drawString(22,  float(lcampo+10), _end1+'  >--> '+_bai1 ) #------: Descricao
						if _end2:

							cv.drawString(500, float(lcampo+10), _end2 )
							cv.drawString(500, float(lcampo), _bai2 )

						else:	cv.drawString(500, float(lcampo+10), "{ Endereço_2 }")
						cv.setFont('Helvetica', 6)

						linhas +=1
						lcampo -= 10
						
						if par.DEVconfs.GetItem(r,4).GetText():

							cv.setFillColor(HexColor('0x7F7F7F'))
							
							cv.drawRightString(115,  float(lcampo), "Numero DAV    Filial  Endereço" ) #-: Codigo do cliente
							cv.drawRightString(165, float(lcampo), "Codigo produto" ) #-: Codigo do cliente
							cv.drawString(170, float(lcampo), "Descrição dos produtos" ) #-: Codigo do cliente

							cv.drawRightString(420, float(lcampo), "Quantidade UN" )
							cv.drawRightString(470, float(lcampo), "Valor unitario" )
							cv.drawRightString(520, float(lcampo), "Sub-Total" )

							cv.drawRightString(550, float(lcampo), "No. NF" )

							cv.drawRightString(660, float(lcampo), "Emissao-Protocolo" )
							cv.drawRightString(800, float(lcampo), "Numero Chave CST"  )
							cv.drawRightString(815, float(lcampo), 'Tipo' )
							cv.setFillColor(HexColor('0x000000'))

							linhas +=1
							lcampo -= 10

							if linhas >= 48 and registros != lancamentos:

								cabccnf( False )
								mdl.rodape(cv,rd1,'','','','','','','','',6)

								pg +=1
								cv.addPageLabel(pg)
								cv.showPage()						
								linhas = 1
								lcampo = 515
								ccampo = 525
								cabccnf( False )

							controle_dav = par.DEVconfs.GetItem(r,4).GetText().split("\n")[0].split("|")[0]
							controle_qtd = len( par.DEVconfs.GetItem(r,4).GetText().split("\n") )

							for dof in par.DEVconfs.GetItem(r,4).GetText().split("\n"):

								if dof:

									info10 = dof.split("|")

									dav = info10[0]
									cdp = info10[2]
									dsp = info10[3]
									uni = info10[4]
									vlu = info10[5]
									qtd = info10[6]
									sbt = info10[7]
									if dav[:3] == "DEV":	cv.setFillColor(HexColor('0xA52A2A'))

									nnf, emi, chv, ser, tip, cst, nen, fil, dta, hor = ast.literal_eval( info10[8] ) if info10[8] else ('','','','','','','','','','')
									
									cv.setFont('Helvetica', 5)
									cv.drawRightString(165,  float(lcampo+5), dta+'  '+hor )
									
									cv.setFont('Helvetica', 6)
									cv.drawRightString(90,  float(lcampo), dav+'  '+fil )
									cv.drawRightString(110,  float(lcampo), nen )

									cv.drawRightString(165, float(lcampo), cdp )
									cv.drawString(170, float(lcampo), dsp )
									cv.drawRightString(420, float(lcampo), qtd+'  '+uni )
									cv.drawRightString(470, float(lcampo), format( Decimal( vlu.replace(",","") ),"," ) )
									cv.drawRightString(520, float(lcampo), format( Decimal( sbt.replace(",","") ),"," ) )

									cv.setFont('Helvetica', 6)
									cv.drawRightString(550, float(lcampo), nnf )

									cv.setFont('Helvetica', 5)
									cv.drawRightString(660, float(lcampo), emi )
									cv.drawRightString(787, float(lcampo), chv )
									cv.drawRightString(800, float(lcampo), cst  )

									cv.setFont('Helvetica-Bold', 5)
									if chv and len( chv ) == 44:	cv.drawRightString(815, float(lcampo), 'NFe' if chv[20:22] == '55' else 'NFCe' if chv[20:22] == '65' else '' )
									if cst != "100":	cv.line(395,( lcampo + 2 ),520,( lcampo + 2 ))

									if controle_dav != dav:	cv.line(30,( lcampo + 9 ),800,( lcampo + 9 ))
									controle_dav = dav
									linhas +=1
									lcampo -= 10
									
									cv.setFillColor(HexColor('0x000000'))
									
									if linhas >= 48 and registros != lancamentos:

										cabccnf( False )
										mdl.rodape(cv,rd1,'','','','','','','','',6)

										pg +=1
										cv.addPageLabel(pg)
										cv.showPage()						
										linhas = 1
										lcampo = 515
										ccampo = 525
										cabccnf( False )
								
					elif relator == "12":
						
						dvr = par.DEVconfs.GetItem(r,0).GetText() #-: Data vendas,recebimento
						vav = self.T.trunca( 3, Decimal( par.DEVconfs.GetItem(r,1).GetText().replace(",","" ) ) ) #-: valor avista
						arc = self.T.trunca( 3, Decimal( par.DEVconfs.GetItem(r,2).GetText().replace(",","" ) ) ) #-: valor contas areceber
						dev = self.T.trunca( 3, Decimal( par.DEVconfs.GetItem(r,3).GetText().replace(",","" ) ) ) #-: devolucoes
						com = self.T.trunca( 3, Decimal( par.DEVconfs.GetItem(r,4).GetText().replace(",","" ) ) ) #-: comissao de cartao
						sal = self.T.trunca( 3, Decimal( par.DEVconfs.GetItem(r,5).GetText().replace(",","" ) ) ) #-: saldo

						rvd = par.DEVconfs.GetItem(r,6).GetText() + par.DEVconfs.GetItem(r,7).GetText() + par.DEVconfs.GetItem(r,8).GetText()#-: Relacao das vendas avista,receber,devolucao

						if par.comissao_analitico.GetValue() == True:	cv.setFont('Helvetica-Bold', 9)
						else:	cv.setFont('Helvetica', 9)
						
						cv.drawString(30, float(lcampo), dvr )
						if vav:	cv.drawRightString(196, float(lcampo), format( vav,',' ) )
						if arc:	cv.drawRightString(296, float(lcampo), format( arc,',' ) )
						if dev:	cv.drawRightString(396, float(lcampo), format( dev,',' ) )
						if com:	cv.drawRightString(496, float(lcampo), format( com,',' ) )
						if sal:	cv.drawRightString(596, float(lcampo), format( sal,',' ) )

						if par.comissao_analitico.GetValue() and rvd:

							linhas +=1
							lcampo -= 10

							cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ) )
							cv.line(20,( lcampo + 20),820,( lcampo + 20) )
							linhas +=1
							lcampo -= 10
							posicao = 47

							cv.setFillColor(HexColor('0x7F7F7F'))
							cv.setFont('Helvetica-Bold', 7)
							cv.drawString(30,  float(lcampo + 11 ), "Filial" )	
							cv.drawString(100, float(lcampo + 11 ), "Nº DAV-Pedido" )	
							cv.drawString(180, float(lcampo + 11 ), "Emisão { vendedor-caixa }" )	
							cv.drawString(290, float(lcampo + 11 ), "Baixa Recebimento { Caixa }" )	
							cv.drawString(400, float(lcampo + 11 ), "Valor Recebido" )
							cv.drawString(460, float(lcampo + 11 ), "Comissão cartão" )	
							cv.drawString(520, float(lcampo + 11 ), "Saldo p/comissão" )	
							cv.drawString(580, float(lcampo + 11 ), "Descrição do Cliente" )	
							cv.drawString(755, float(lcampo + 11 ), "Tipo-Recebimento" )	

							_lancamentos = 0
							numero_lancamentos = 0
							for _rcc in rvd.split("\n"):
								
								if  _rcc:	numero_lancamentos +=1	
	
							for rcc in rvd.split("\n"):
								
								cv.setFont('Helvetica', 8)
								cv.setFillColor(HexColor('0x000000'))

								if rcc:
									
									srcc = rcc.split(";")
									_lancamentos +=1

									if srcc[6].upper() == "DEVOLUCAO":	cv.setFillColor(HexColor('0xA52A2A'))
									cv.drawString(30,  float(lcampo), srcc[0] )
									cv.drawString(100, float(lcampo), srcc[1] )
									cv.setFont('Helvetica', 7)
									cv.drawString(180, float(lcampo), srcc[2] )
									cv.drawString(290, float(lcampo), srcc[3] )

									cv.setFont('Helvetica', 8)
									#if len( srcc ) >= 8 and Decimal( srcc[7] ):	cv.setFillColor(HexColor('0x1111A3'))
									#else:	cv.setFillColor(HexColor('0x000000'))

									cv.drawRightString(450, float(lcampo), srcc[4] )
									if srcc[6].upper() == "RECEBER" and len( srcc ) >=8:	cv.drawRightString(510, float(lcampo), srcc[7] )
									if srcc[6].upper() == "RECEBER" and len( srcc ) >=9:	cv.drawRightString(570, float(lcampo), srcc[8] )
									else:	cv.drawRightString(570, float(lcampo), srcc[4] )

									cv.setFont('Helvetica', 7)
									cv.drawString(580, float(lcampo), srcc[5] )
									cv.setFillColor(HexColor('0x7F7F7F'))
									cv.setFont('Helvetica', 8)
									cv.drawString(780, float(lcampo), srcc[6].lower() )
									cv.setFillColor(HexColor('0x000000'))

									linhas +=1
									lcampo -= 10
						
								if linhas >= posicao:
									
									cabccnf( False )
									mdl.rodape(cv,rd1,'','','','','','','','',6)

									pg +=1
									cv.addPageLabel(pg)
									cv.showPage()						
									linhas = 1
									lcampo = 515
									ccampo = 525

									cabccnf( False )
									
									if numero_lancamentos > _lancamentos:
										
										linhas +=1
										lcampo -= 10

										cv.setFillColor(HexColor('0x7F7F7F'))
										cv.setFont('Helvetica-Bold', 7)
										cv.drawString(30,  float(lcampo + 11 ), "Filial" )	
										cv.drawString(100, float(lcampo + 11 ), "Nº DAV-Pedido" )	
										cv.drawString(180, float(lcampo + 11 ), "Emisão { vendedor-caixa }" )	
										cv.drawString(290, float(lcampo + 11 ), "Baixa Recebimento { Caixa }" )	
										cv.drawString(400, float(lcampo + 11 ), "Valor Recebido" )	
										cv.drawString(460, float(lcampo + 11 ), "Descrição do Cliente" )	
										cv.drawString(755, float(lcampo + 11 ), "Tipo-Recebimento" )	

					if relator == "16":

						cv.setFont('Helvetica', 8)
						if par.DEVconfs.GetItem(r,8).GetText() == "2":	cv.setFillColor(HexColor('0x7F1D1D'))
						cv.drawString(22,  float(lcampo), par.DEVconfs.GetItem(r,0).GetText() )
						cv.drawString(55,  float(lcampo), par.DEVconfs.GetItem(r,1).GetText() )
						cv.drawRightString(160, float(lcampo), par.DEVconfs.GetItem(r,2).GetText() )
						cv.drawString(166, float(lcampo), par.DEVconfs.GetItem(r,3).GetText() )
						cv.drawString(215, float(lcampo), par.DEVconfs.GetItem(r,4).GetText() )
						cv.drawString(260, float(lcampo), par.DEVconfs.GetItem(r,5).GetText() )
						cv.drawRightString(660, float(lcampo), par.DEVconfs.GetItem(r,6).GetText() )
						cv.drawRightString(716, float(lcampo), par.DEVconfs.GetItem(r,7).GetText() )
						cv.drawString(720, float(lcampo), "Sem rateio" if par.DEVconfs.GetItem(r,8).GetText() == "2" else "" )
						cv.setFillColor(HexColor('0x000000'))

					elif relator == '90':

						cv.setFont('Helvetica', 7)
						if par.gerenciaNfe.GetItem(r,20).GetText() == "2" or par.gerenciaNfe.GetItem(r,20).GetText() == "4":	cv.setFillColor(HexColor('0x7F7F7F'))
						if par.gerenciaNfe.GetItem(r,20).GetText() == "3" or par.gerenciaNfe.GetItem(r,20).GetText() == "5":	cv.setFillColor(HexColor('0xA52A2A'))
						
						cv.drawString(22,  float(lcampo), par.gerenciaNfe.GetItem(r, 0).GetText().split('[')[0]+'-'+par.gerenciaNfe.GetItem(r, 1).GetText() )
						cv.drawString(80,  float(lcampo), par.gerenciaNfe.GetItem(r, 2).GetText() )
						cv.drawString(140, float(lcampo), par.gerenciaNfe.GetItem(r, 5).GetText() )
						
						cv.drawRightString(290, float(lcampo), par.gerenciaNfe.GetItem(r, 6).GetText() )

						rs = par.gerenciaNfe.GetItem(r, 0).GetText()
						cv.drawString(295, float(lcampo), rs.split('[')[1][:len(rs.split("[")[1])-1] )
						cv.drawString(400, float(lcampo), par.gerenciaNfe.GetItem(r,20).GetText()+'-'+par.gerenciaNfe.GetItem(r, 7).GetText() )
						cv.drawRightString(752, float(lcampo), par.gerenciaNfe.GetItem(r, 3).GetText().split("-")[0] )

						tnfes = 'Vendas'
						if par.gerenciaNfe.GetItem(r, 14).GetText() == '2':	tnfes = "Devolucao"
						if par.gerenciaNfe.GetItem(r, 14).GetText() == '3':	tnfes = "RMA"
						if par.gerenciaNfe.GetItem(r, 14).GetText() == '4':	tnfes = "Transferencia"
						if par.gerenciaNfe.GetItem(r, 14).GetText() == '6':	tnfes = "Simples faturamento"
						if par.gerenciaNfe.GetItem(r, 14).GetText() == '7':	tnfes = "Entrega futura"

						cv.setFont('Helvetica', 5)
						cv.drawString(755, float(lcampo), 'nfe-'+tnfes if par.gerenciaNfe.GetItem(r, 4).GetText() == '1' else 'nfce-'+tnfes )

						cv.setFillColor(HexColor('0x000000'))


					elif relator == '91':

						cv.setFont('Helvetica', 7)
						l = par.listar_compras.split('</>')[r]
						if l:
							
							d = l.split('|')[0]
							p = l.split('|')[1]
							
							if d and p :

								rlt = {1:"Todos",2:"NF vendas",3:"Devolução",4:"RMA",5:"Transferencia",6:"Compras",7:"Simples faturamento",8:"Entrega futura"}

								cv.setFillColor(HexColor('0x7F7F7F'))
								cv.drawString(22, float(lcampo), "     Emitente: "+d.split(';')[2]+' - '+d.split(';')[3] )
								cv.drawString(400, float(lcampo),"Modelo: "+d.split(';')[5]+' Serio: '+d.split(';')[6]+' Numero NF: '+d.split(';')[7]+' Chave: '+d.split(';')[8] )
								if d.split(';')[14]:	cv.drawRightString(816, float(lcampo), "{ "+ rlt[ int( d.split(';')[14] ) ]+" }" )

								linhas +=1
								lcampo -= 10

								cv.drawString(22,float(lcampo), "Destinatario: "+d.split(';')[0]+' - '+d.split(';')[1] )
								cv.setFont('Helvetica-Bold', 6)

								cv.drawString(400, float(lcampo),"Base ICMS:" )
								cv.drawString(480, float(lcampo),"Total ICMS:" )
								cv.drawString(560, float(lcampo),"Base ST:" )
								cv.drawString(640, float(lcampo),"Total ST:" )
								cv.drawString(720, float(lcampo),"Total produtos:" )
								cv.setFont('Helvetica', 7)
								
								if Decimal( d.split(';')[9]  ):	cv.drawRightString(476, float(lcampo), format( Decimal( d.split(';')[9]  ),',' ) ) #//Base Total ICMS
								if Decimal( d.split(';')[10] ):	cv.drawRightString(556, float(lcampo), format( Decimal( d.split(';')[10] ),',' ) ) #//Valor total icms
								if Decimal( d.split(';')[11] ):	cv.drawRightString(636, float(lcampo), format( Decimal( d.split(';')[11] ),',' ) ) #//Base ST
								if Decimal( d.split(';')[12] ):	cv.drawRightString(716, float(lcampo), format( Decimal( d.split(';')[12] ),',' ) ) #//valor total STBase
								if Decimal( d.split(';')[13] ):	cv.drawRightString(816, float(lcampo), format( Decimal( d.split(';')[13] ),',' ) ) #//valor total dos produtos
								cv.line(20, float(lcampo - 2 ), 820, float(lcampo - 2) )

								if linhas >= 47:

									cabccnf( False )
									mdl.rodape(cv,rd1,'','','','','','','','',6)

									pg +=1
									cv.addPageLabel(pg)
									cv.showPage()						
									linhas = 1
									lcampo = 527 # if not relator == "10" else 505
									ccampo = 525
												
									cabccnf( False )

								cv.setFont('Helvetica-Bold', 5)
								linhas +=1
								lcampo -= 10

								cv.setFillColor(HexColor('0x7F7F7F'))
								cv.drawRightString(80, float(lcampo), "Codigo" ) #//Codigo
								cv.drawString(84, float(lcampo), u"Descrição dos produtos" ) #//Descricao dos produtos

								cv.drawRightString(400, float(lcampo), "Codigo NCM" ) #//NCM
								cv.drawRightString(430, float(lcampo), "C F O P" ) #//CFOP
								cv.drawRightString(460, float(lcampo), "CST" ) #//CST
								cv.drawRightString(490, float(lcampo), "CSOSN" ) #//CSOSN
								cv.drawRightString(530, float(lcampo), "Base ICMS" ) #//Base ICMS
								cv.drawRightString(580, float(lcampo), "Valor ICMS" )  #//Valor ICMS
								cv.drawRightString(630, float(lcampo), "Base ST" ) #//Base ST
								cv.drawRightString(680, float(lcampo), "Valor ST" ) #//Valor ST
								cv.drawRightString(730, float(lcampo), "Valo produto" ) #//Valor total produto

								cv.drawRightString(760, float(lcampo), "% ICMS" ) #//% ICMS
								cv.drawRightString(790, float(lcampo), "% ST" ) #//% ST
								cv.drawRightString(816, float(lcampo), "% MVAST" ) #//ST-MVAST
								
								cv.setFillColor(HexColor('0x000000'))
								cv.setFont('Helvetica', 7)
								
								for pd in p.split('\n'):
									
									if pd:
										
										linhas +=1
										lcampo -= 10

										cv.drawRightString(80, float(lcampo), pd.split(';')[0] ) #//Codigo
										cv.setFont('Helvetica', 6)
										cv.drawString(84, float(lcampo), pd.split(';')[1][:80] ) #//Descricao dos produtos
										cv.setFont('Helvetica', 7)

										cv.drawRightString(400, float(lcampo), pd.split(';')[2] ) #//NCM
										cv.drawRightString(430, float(lcampo), pd.split(';')[3] ) #//CFOP
										cv.drawRightString(460, float(lcampo), pd.split(';')[5] ) #//CST
										cv.drawRightString(490, float(lcampo), pd.split(';')[6] ) #//CSOSN
										if Decimal( pd.split(';')[7] ):	cv.drawRightString(530, float(lcampo), format( Decimal( pd.split(';')[7] ),',' ) ) #//Base ICMS
										if Decimal( pd.split(';')[8] ):	cv.drawRightString(580, float(lcampo), format( Decimal( pd.split(';')[8] ),',' ) )  #//Valor ICMS
										if Decimal( pd.split(';')[9] ):	cv.drawRightString(630, float(lcampo), format( Decimal( pd.split(';')[9] ),',' ) ) #//Base ST
										if Decimal( pd.split(';')[10]):	cv.drawRightString(680, float(lcampo), format( Decimal( pd.split(';')[10]),',' ) ) #//Valor ST
										if Decimal( pd.split(';')[14]):	cv.drawRightString(730, float(lcampo), format( Decimal( pd.split(';')[14]),',' ) ) #//Valor total produto

										cv.setFont('Helvetica', 5)
										if Decimal( pd.split(';')[11]):	cv.drawRightString(760, float(lcampo), format( Decimal( pd.split(';')[11]),',' ) ) #//Percentual icms
										if Decimal( pd.split(';')[12]):	cv.drawRightString(790, float(lcampo), format( Decimal( pd.split(';')[12]),',' ) ) #//Percentual ST
										if Decimal( pd.split(';')[13]):	cv.drawRightString(816, float(lcampo), format( Decimal( pd.split(';')[13]),',' ) ) #//Percentual ST MVAST
										cv.setFont('Helvetica', 7)

										if linhas >= 47:

											cabccnf( False )
											mdl.rodape(cv,rd1,'','','','','','','','',6)

											pg +=1
											cv.addPageLabel(pg)
											cv.showPage()						
											linhas = 1
											lcampo = 527 # if not relator == "10" else 505
											ccampo = 525
												
											cabccnf( False )

								cv.line(20, float(lcampo - 2 ), 820, float(lcampo - 2) )
						
					intercalar_linhas = True
					if relator in ["11","12","08"] and par.comissao_analitico.GetValue():	intercalar_linhas = False
					
					if linhas !=1 and _prin and intercalar_linhas and relator !="91":
						
						cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))

					Indice +=1

					linhas +=1
					lcampo -= 10
					posicao = 48
					if relator == "15":
						
						lcampo -= 20
						posicao = 16
						
					if relator == "03":	posicao = 45
					if relator == "10":	posicao = 48
					if relator == "10" and registros == lancamentos:	linhas = 1

					if linhas >= posicao:

						if relator == "03":	lcampo -=5

						if relator in ["11","12","08","10"] and par.comissao_analitico.GetValue() == True:	cabccnf( False )
						else:	cabccnf( False if relator in ['91'] else True )
						mdl.rodape(cv,rd1,'','','','','','','','',6)

						pg +=1
						cv.addPageLabel(pg)
						cv.showPage()						
						linhas = 1
						lcampo = 515 if not relator == "10" else 505
						ccampo = 525
							
						cabccnf( False )
			
						"""   Davs Emitidos p/Forma de Pagamnto   """
						if relator == "02" and par.fpagame.GetValue() !="":

							cv.setFont('Helvetica-Bold', 7)
							cv.drawRightString(730, float(526), par.fpagame.GetValue() )				
							cv.drawRightString(817, float(526), "DAV:Valor Recebido" )
						
				if relator in ["11","12","08","10"] and par.comissao_analitico.GetValue() == True:

					cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))
					cabccnf( False )

				else:	cabccnf( False if relator in ['91'] else True)

				mdl.rodape(cv,rd1,'','','','','','','','',6)
				
			cv.save()

			del _mensagem

			gerenciador.TIPORL = ''	
			gerenciador.Anexar = nomeArquivo
			gerenciador.imprimir = True
			gerenciador.Filial   = Filiais
				
			ger_frame=gerenciador(parent=par,id=-1)
			ger_frame.Centre()
			ger_frame.Show()

class RelatoriosCliente:
	
	def cldiversos(self,mdl,par,_di,_df,__id, Filial = "" ):

		def cabccnf( _separa ):

			""" Cabecalho """
			pag = str(pg).zfill(3)
			if par.relator.GetValue().split("-")[0] == "01":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,login.identifi,"CLIENTE: Compras",2)
			if par.relator.GetValue().split("-")[0] == "02":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,login.identifi,"CLIENTE: Compras",2)
			if par.relator.GetValue().split("-")[0] == "03":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,login.identifi,"CLIENTE: Parceiros",2)
			if par.relator.GetValue().split("-")[0] == "05":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,login.identifi,"CLIENTE: Cadastro",2)
			if par.relator.GetValue().split("-")[0] == "06":	rls.cabecalhopadrao(cv,ImageReader,dh,pag,login.identifi,"CLIENTE: Conciliado",2)

			if par.relator.GetValue().split("-")[0] == "01":

				cv.setFillColor(HexColor('0x636363'))
				cv.drawString(200,33,"Valor Total Recebido:")
				cv.drawString(350,33,"Valor ToTal Aberto:")
				cv.drawString(200,23,"Nº DAVs Emitidos:")
				cv.drawRightString(340, 33,par.TTL.split('|')[0])
				cv.drawRightString(480, 33,par.TTL.split('|')[1])
				cv.drawRightString(340, 23,par.TTL.split('|')[2])

			elif par.relator.GetValue().split("-")[0] == "02":

				cv.setFillColor(HexColor('0x636363'))
				cv.drawString(200,33,"Valor Total Recebido:")
				cv.drawString(200,23,"Nº DAVs Emitidos:")
				cv.drawRightString(340, 33,par.TTL.split('|')[0])
				cv.drawRightString(340, 23,par.TTL.split('|')[1])

			elif par.relator.GetValue().split("-")[0] == "06":

				cv.setFillColor(HexColor('0x636363'))
				cv.drawString(260,33,"Compras:")
				cv.drawString(260,23,"Devolução:")

				cv.drawString(400,33,"Compras-Canceladas:")
				cv.drawString(400,23,"Devolução-Canceladas:")

				cv.drawRightString(380, 33, format( par.con_vendas ,',' ) )
				cv.drawRightString(380, 23, format( par.con_devolu ,',' ) )

				cv.drawRightString(550, 33, format( par.con_vcance ,',' ) )
				cv.drawRightString(550, 23, format( par.con_dcance ,',' ) )

			cv.setFillColor(HexColor('0x000000'))
			
			""" Titulo de Cabecalho """
			cb1= cb2= cb3= cb4= cb5= cb6= cb7= cb8= cb9= cb10= cb11= cb12=''
			
			_Tipo = par.relator.GetValue().split("-")[0]
			if par.relator.GetValue().split("-")[0] == "01":	_Tipo += (" "*10)+par.cli.GetLabel()
			if par.relator.GetValue().split("-")[0] == "03":	_Tipo += (" "*10)+par.cli.GetLabel()
			if par.relator.GetValue().split("-")[0] == "05":	_Tipo += (" "*10)+par.relator.GetLabel()
			if par.relator.GetValue().split("-")[0] == "06":	_Tipo = par.relator.GetValue()+(" "*10)+"Cliente: "+str( par.cli.GetLabel() )

			if par.cmpGrup.GetValue().strip() !="":

				if par.ajfabri.GetValue() == True:	_Tipo +=(" "*5)+"Fabricante: "+par.cmpGrup.GetValue()
				if par.ajgrupo.GetValue() == True:	_Tipo +=(" "*5)+"Grupo: "+par.cmpGrup.GetValue()
				if par.ajsubg1.GetValue() == True:	_Tipo +=(" "*5)+"Sub-Grupo_1: "+par.cmpGrup.GetValue()
				if par.ajsubg2.GetValue() == True:	_Tipo +=(" "*5)+"Sub-Grupo_2: "+par.cmpGrup.GetValue()

			if par.relator.GetValue().split("-")[0] == "05":	rel = u'Usuário: '+str(login.usalogin)+(" "*10)+_Tipo
			else:	rel = u'Usuário: '+str(login.usalogin)+u"  PERÌODO: "+cIni+" A "+cFim+(" "*10)+_Tipo
			
			if par.relator.GetValue().split("-")[0] == "01":

				cb1 =  "22|540|Filial|"
				cb2 =  "50|540|Nº DAV|#7F7F7F"
				cb3 = "110|540|Nº NFs|#7F7F7F"
				cb4 = "140|540|Nº Cupom|#7F7F7F"
				cb5 = "180|540|Emissão|"
				cb6 = "340|540|Recebimento|"
				cb7 = "500|540|Valor|"
				cb8 = "555|540|Forma de Pagamento|"
				cb9 = "650|540|Receber Local|"

			elif par.relator.GetValue().split("-")[0] == "02":
				cb1  =  "22|540|Nome Fantasia|#7F7F7F"
				cb2  =  "150|540|Descrição do Cliente|"
				cb3  =  "580|540|Nº DAVs [QT-MT Vendas]|"
				cb4  =  "700|540|Valor Total|"

			elif par.relator.GetValue().split("-")[0] == "03":
				cb1  =  "22|540|Código|#7F7F7F"
				cb2  =  "150|540|Fantasia|"
				cb3  =  "380|540|Descrição do Parceiro [ Cliente ]|"

			elif par.relator.GetValue().split("-")[0] == "05":
				cb1  =  "22|540|[ Cadastros de Clientes ]|#7F7F7F"

			elif par.relator.GetValue().split("-")[0] == "06":
				cb1  =   "22|540|Nº DAV|#7F7F7F"
				cb2  =   "80|540|DAV-Devolução|#7F7F7F"
				cb3  =  "140|540|Emissão|"
				cb4  =  "260|540|Recebimento|"
				cb5  =  "380|540|Cancelamento|"
				cb6  =  "500|540|Valor||R"
				cb7  =  "560|540|Motivo|#7F7F7F"

			if _separa == False:	mdl.mtitulo(rel,cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12,7,2)
			else:

				if par.relator.GetValue().split("-")[0] in ["01","06"]:

					cv.line((float(cb2.split('|')[0])-2), float(ccampo), (float(cb2.split('|')[0])-2), float(lcampo))
					cv.line((float(cb3.split('|')[0])-2), float(ccampo), (float(cb3.split('|')[0])-2), float(lcampo))
					cv.line((float(cb4.split('|')[0])-2), float(ccampo), (float(cb4.split('|')[0])-2), float(lcampo))
					cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float(lcampo))
					cv.line((float(cb6.split('|')[0])-2), float(ccampo), (float(cb6.split('|')[0])-2), float(lcampo))
					cv.line((float(cb7.split('|')[0])-2), float(ccampo), (float(cb7.split('|')[0])-2), float(lcampo))
					if par.relator.GetValue().split("-")[0] == "01":	cv.line((float(cb8.split('|')[0])-2), float(ccampo), (float(cb8.split('|')[0])-2), float(lcampo))
					if par.relator.GetValue().split("-")[0] == "01":	cv.line((float(cb9.split('|')[0])-2), float(ccampo), (float(cb9.split('|')[0])-2), float(lcampo))

				if par.relator.GetValue().split("-")[0] == "02":

					cv.line((float(cb2.split('|')[0])-2), float(ccampo), (float(cb2.split('|')[0])-2), float(lcampo))
					cv.line((float(cb3.split('|')[0])-2), float(ccampo), (float(cb3.split('|')[0])-2), float(lcampo))
					cv.line((float(cb4.split('|')[0])-2), float(ccampo), (float(cb4.split('|')[0])-2), float(lcampo))

				if par.relator.GetValue().split("-")[0] == "03":

					cv.line((float(cb2.split('|')[0])-2), float(ccampo), (float(cb2.split('|')[0])-2), float(lcampo))
					cv.line((float(cb3.split('|')[0])-2), float(ccampo), (float(cb3.split('|')[0])-2), float(lcampo))

				#-----: Linha Final
				cv.line(20,float(lcampo),820,float(lcampo))

		#----------------------------: Emissao do Relatorio :-----------------------------:
		self.T = truncagem()
		if par.CLTContas.GetItemCount() !=0:

			_mensagem = mens.showmsg("Clientes: Montando Relatório\nAguarde...")

			cIni = datetime.datetime.strptime(_di.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			cFim = datetime.datetime.strptime(_df.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			
			dh  = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
			pg  = 1

			if par.relator.GetValue().split("-")[0] == "01":	nomeArquivo = diretorios.usPasta+"clSelecionado_"+login.usalogin.lower()+".pdf"
			if par.relator.GetValue().split("-")[0] == "02":	nomeArquivo = diretorios.usPasta+"clTodos_"+login.usalogin.lower()+".pdf"
			if par.relator.GetValue().split("-")[0] == "03":	nomeArquivo = diretorios.usPasta+"clParceiro_"+login.usalogin.lower()+".pdf"
			if par.relator.GetValue().split("-")[0] == "05":	nomeArquivo = diretorios.usPasta+"cadastroClientes_"+login.usalogin.lower()+".pdf"
			if par.relator.GetValue().split("-")[0] == "06":	nomeArquivo = diretorios.usPasta+"conciliacaocompras_"+login.usalogin.lower()+".pdf"
			
			cv = canvas.Canvas(nomeArquivo, pagesize=landscape(A4))
			cabccnf(False)
			
			lcampo = 515
			ccampo = 525
			linhas = 1

			rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio:'+str( par.relator.GetValue()[2:] )+')|'
			
			__nReg = par.CLTContas.GetItemCount()
			Indice = 0

			if par.relator.GetValue().split("-")[0] == "06":	numero_dav_concilia = par.CLTContas.GetItem( 0, 0 ).GetText()
			
			for r in range(__nReg):

				_cli = par.CLTContas.GetItem(Indice,9).GetText().split('|')

				_emis = _rece = ''
				cv.setFont('Helvetica', 7)
				if par.relator.GetValue().split("-")[0] == "01" and _cli[0] !=0:
		
					_emis = _cli[4]
					_rece = _cli[5]
					cv.drawString(22,  float(lcampo), _cli[0] )
					cv.drawString(50,  float(lcampo), _cli[1] )
					cv.drawString(110, float(lcampo), _cli[2] )
					cv.drawString(140, float(lcampo), _cli[3] )
					cv.drawString(180, float(lcampo), _cli[4] )
					cv.drawString(340, float(lcampo), _cli[5] )
					cv.drawRightString(550, float(lcampo), _cli[6] )
					cv.drawString(555, float(lcampo), _cli[7] )
					cv.drawString(650, float(lcampo), _cli[8] )

				elif par.relator.GetValue().split("-")[0] == "02" and _cli[0] !=0:

					cv.drawString(22,  float(lcampo), _cli[0] )
					cv.drawString(150,  float(lcampo), _cli[1] )
					cv.drawRightString(693, float(lcampo), _cli[2] )
					cv.drawRightString(815, float(lcampo), _cli[3] )

				elif par.relator.GetValue().split("-")[0] == "03" and _cli[0] !=0:

					cv.drawString(22,  float(lcampo), _cli[0] )
					cv.drawString(150, float(lcampo), _cli[1] )
					cv.drawString(380, float(lcampo), _cli[2] )

				elif par.relator.GetValue().split("-")[0] == "05" and _cli[0] !=0:

					cv.setFillColor(HexColor('0x636363'))
					cv.drawString(22,  float(lcampo), "Nome do Cliente: ")
					cv.drawString(400, float(lcampo), "Nome Fantasia: ")
					cv.drawString(600, float(lcampo), "Data do Cadastro: ")
					cv.setFillColor(HexColor('0x000000'))
					cv.drawString(80,  float(lcampo), _cli[0] )
					cv.drawString(452, float(lcampo), _cli[13] )
					cv.drawString(660, float(lcampo), _cli[14] )

					linhas +=1
					lcampo -= 10
					cv.setFillColor(HexColor('0x636363'))
					cv.drawString(22,  float(lcampo), "Endereço:" )
					cv.drawString(400, float(lcampo), "Bairro: ")
					cv.drawString(600, float(lcampo), "Cidade: ")
					cv.setFillColor(HexColor('0x000000'))
					cv.drawString(80,  float(lcampo), _cli[1]+(" "*5)+u"Nº "+_cli[2]+(" "*5)+"Complemento: "+_cli[3] )
					cv.drawString(452, float(lcampo), _cli[4] )
					cv.drawString(660, float(lcampo), _cli[5] )

					linhas +=1
					lcampo -= 10
					cv.setFillColor(HexColor('0x636363'))
					cv.drawString(22,  float(lcampo), "Modalidade:" )
					cv.drawString(400, float(lcampo), "Seguimento: ")
					cv.drawString(600, float(lcampo), "Telefone: ")
					cv.setFillColor(HexColor('0x000000'))
					cv.drawString(80,  float(lcampo), _cli[10]+(" "*5)+u"Limite de Crédito: "+format(Decimal(_cli[11]),',') )
					cv.drawString(452, float(lcampo), _cli[9] )
					cv.drawString(660, float(lcampo), _cli[12] )

					linhas +=1
					lcampo -= 10
					
				elif par.relator.GetValue().split("-")[0] == "06": # and _cli[0] !=0:

					cv.drawString(22,  float(lcampo),  str( par.CLTContas.GetItem( r, 0 ).GetText() ) )
					cv.drawString(80,  float(lcampo), str( par.CLTContas.GetItem( r, 1 ).GetText() ) )
					cv.drawString(140, float(lcampo), str( par.CLTContas.GetItem( r, 2 ).GetText() ) )
					cv.drawString(260, float(lcampo), str( par.CLTContas.GetItem( r, 3 ).GetText() ) )
					cv.drawString(380, float(lcampo), str( par.CLTContas.GetItem( r, 4 ).GetText() ) )
					
					cv.drawRightString(555, float(lcampo), str( par.CLTContas.GetItem( r, 5 ).GetText() ) )
					cv.drawString(560, float(lcampo), str( par.CLTContas.GetItem( r, 6 ).GetText() ) )
	
					if linhas !=1 and numero_dav_concilia != par.CLTContas.GetItem( r, 0 ).GetText():	cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))
					numero_dav_concilia = par.CLTContas.GetItem( r, 0 ).GetText()

				if linhas !=1 and par.relator.GetValue().split("-")[0] != "06":	cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))
				if par.relator.GetValue().split("-")[0] == "05":

					linhas -=1
					lcampo += 10

				Indice +=1
				linhas +=1
				lcampo -= 10
							
				if linhas >=48:

					if par.relator.GetValue().split("-")[0] == "05":	cabccnf(False)
					else:	cabccnf(True)
					mdl.rodape(cv,rd1,'','','','','','','','',6)

					pg +=1
					cv.addPageLabel(pg)
					cv.showPage()						
					linhas = 1
					lcampo = 515
					ccampo = 525
						
					cabccnf(False)
			
			if par.relator.GetValue().split("-")[0] == "05":	cabccnf(False)
			else:	cabccnf(True)
			mdl.rodape(cv,rd1,'','','','','','','','',6)
			cv.save()

			del _mensagem
			gerenciador.TIPORL = ''
			gerenciador.Anexar = nomeArquivo
			gerenciador.imprimir = True
			gerenciador.Filial   = Filial
				
			ger_frame=gerenciador(parent=par,id=-1)
			ger_frame.Centre()
			ger_frame.Show()

""" Contas Apagar """
class RelatoriosOutros:
	
	def rlOutros(self,mdl,par,_di,_df, Filial = "" ):


		def cabccnf(_separa):


			""" Cabecalho """
			pag = str(pg).zfill(3)
			rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filial,"FRETES ENTREGAS",2)
			cv.setFillColor(HexColor('0x636363'))
			
			
			""" Titulo de Cabecalho """
			cb1= cb2= cb3= cb4= cb5= cb6= cb7= cb8= cb9= cb10= cb11= cb12=''
			rel =  'Usuário: '+str(login.usalogin)+"  PERÌODO: "+cIni+" A "+cFim+(" "*10)+Filial
					
			cb1  =   "22|540|  QTD - Descrição do Transportador [ Filial - Nº DAV-Comanda - Descrição do Cliente ]|"
			cb2  =  "400|540|Nº Romaneio|"
			cb3  =  "500|540|DATA Abertura|"
			cb4  =  "610|540|DATA Fechamento|"
			cb5  =  "710|540|Previsão de Entrega|"
				
				
			if _separa == False:	mdl.mtitulo(rel,cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12,7,2)
			else:
					
				cv.line((float(cb2.split('|')[0])-2), float(ccampo), (float(cb2.split('|')[0])-2), float(lcampo))
				cv.line((float(cb3.split('|')[0])-2), float(ccampo), (float(cb3.split('|')[0])-2), float(lcampo))
				cv.line((float(cb4.split('|')[0])-2), float(ccampo), (float(cb4.split('|')[0])-2), float(lcampo))
				cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float(lcampo))

				#-----: Linha Final
				cv.line(20,float(lcampo),820,float(lcampo))


		cIni = datetime.datetime.strptime(_di.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
		cFim = datetime.datetime.strptime(_df.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			
		dh  = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
		pg  = 1

		nomeArquivo = diretorios.usPasta+"rmentregas_"+login.usalogin.lower()+".pdf"
			
		cv = canvas.Canvas(nomeArquivo, pagesize=landscape(A4))
		cabccnf(False)
			
		lcampo = 515
		ccampo = 525
		linhas = 1

		rd1 = '22|35|110|'+login.identifi+'-'+login.emfantas+' (Relatorio: Romaneio de Entregas - Fretes)|'

		_mensagem = mens.showmsg("Relatótiro de Romaneio-Fretes Entregas!!\n.\nAguarde...")

		nTrans = ""
		romane = ""
		
				
		for r in par.lsT:
				
			lisTa = r.split('<p>')

			cv.setFont('Helvetica', 9)

			if romane != lisTa[0] or nTrans != lisTa[5]:	cv.setFont('Helvetica-Bold', 9)
			if nTrans != lisTa[5]:

				"""  Totaliza QT Entregas   """
				TotalE = 0
				for p1 in par.lsT:
					
					l1 = p1.split('<p>')
					if l1[5] == lisTa[5] and l1[3] !="":
						
						for l2 in l1[3].split('\n'):

								if l2 !="":	TotalE +=1
				
				cv.setFillGray(0.1,0.1) 
				cv.rect(20,( lcampo - 2 ),800,12, fill=1) #--: Fundo do cabecalho
				
				cv.setFillColor(HexColor('0x000000'))
				cv.drawString(25,  float(lcampo),str( TotalE ).zfill(3)+' - '+str( lisTa[5] ) )

			else:

				
				cv.setFont('Helvetica-Bold', 7)
				cv.setFillColor(HexColor('0x4D4D4D'))
				cv.drawString(25,  float(lcampo), "Filial" )
				cv.drawString(60,  float(lcampo), "NºDAV-Comanda" )
				cv.drawString(130, float(lcampo), "Descrição do Cliente" )
				cv.setFillColor(HexColor('0x000000'))
							
			cv.setFont('Helvetica-Bold', 9)
			cv.drawString(400, float(lcampo), str( lisTa[0] ) )
			cv.drawString(500, float(lcampo), str( lisTa[1] ) )
			cv.drawString(610, float(lcampo), str( lisTa[2] ) )
			cv.drawString(710, float(lcampo), str( lisTa[4] ) )
			cv.setFont('Helvetica', 9)
			cv.line(20,float(lcampo-2), 820,float(lcampo-2))
			cv.line(20,float(lcampo+10),820,float(lcampo+10))


			nTrans = lisTa[5]
			romane = lisTa[0]
					
			cv.setFillColor(HexColor('0x000000'))

			linhas +=1
			lcampo -= 10


			if linhas >= 48:

				cabccnf(True)
				mdl.rodape(cv,rd1,'','','','','','','','',6)

				pg +=1
				cv.addPageLabel(pg)
				cv.showPage()						
				linhas = 1
				lcampo = 515
				ccampo = 525
							
				cabccnf(False)

			
			if lisTa[3] !="":

				cv.setFont('Helvetica', 8)
				indice = 0
				for nlp in lisTa[3].split('\n'):
					
					rl = nlp.split("|")
					if rl[0] !="":
						
						emi = rl[2].split(' ')
						cv.drawString(25, float(lcampo),rl[0] )
						cv.drawString(60, float(lcampo),rl[1] )
						cv.drawString(130,float(lcampo),rl[4] )
						if indice == 0:

							cv.setFont('Helvetica-Bold', 6)
							cv.setFillColor(HexColor('0x4D4D4D'))
							cv.drawString(400, float(lcampo), "Emissão do DAV-Comanda" )
							cv.setFont('Helvetica', 8)
							cv.setFillColor(HexColor('0x000000'))

	
						if emi !='':

							cv.drawString(500, float(lcampo), emi[0] )
							cv.drawString(610, float(lcampo), emi[1] )
							cv.drawString(710, float(lcampo), emi[2] )
					
					indice +=1
					linhas +=1
					lcampo -= 10


					if linhas >= 48:

						cabccnf(True)
						mdl.rodape(cv,rd1,'','','','','','','','',6)

						pg +=1
						cv.addPageLabel(pg)
						cv.showPage()						
						linhas = 1
						lcampo = 515
						ccampo = 525
									
						cabccnf(False)
					
				cv.setFont('Helvetica', 9)

		
		cabccnf(True)
		mdl.rodape(cv,rd1,'','','','','','','','',6)
		cv.save()

		del _mensagem

		gerenciador.TIPORL = ''
		gerenciador.Anexar = nomeArquivo
		gerenciador.imprimir = True
		gerenciador.Filial   = Filial
				
		ger_frame=gerenciador(parent=par,id=-1)
		ger_frame.Centre()
		ger_frame.Show()

class RelatoriosAdministrativo:
	
	def rlAdministrativo(self,mdl,par,_di,_df, Filial = "", dados = "" ):

		def cabccnf(_separa):


			""" Cabecalho """
			pag = str(pg).zfill(3)
			rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filial,"ATUALIZADAS",2)
			cv.setFillColor(HexColor('0x636363'))
			
			
			""" Titulo de Cabecalho """
			cb1= cb2= cb3= cb4= cb5= cb6= cb7= cb8= cb9= cb10= cb11= cb12=''
			rel =  'Usuário: '+str(login.usalogin)+"  PERÌODO: "+_di+" A "+_df+(" "*10)+Filial+"  { RELATORIO DE LOJAS ATUALIZADAS PELO DIRETO }"
					
			cb1  =   "22|540|Descrição do cliente|"
			cb2  =  "600|540|Atualização|"
				
				
			if _separa == False:	mdl.mtitulo(rel,cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12,7,2)
			else:
					
				cv.line((float(cb2.split('|')[0])-2), float(ccampo), (float(cb2.split('|')[0])-2), float(lcampo))

				#-----: Linha Final
				cv.line(20,float(lcampo),820,float(lcampo))

			
		dh  = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
		pg  = 1

		nomeArquivo = diretorios.usPasta+"atualizadas_"+login.usalogin.lower()+".pdf"
			
		cv = canvas.Canvas(nomeArquivo, pagesize=landscape(A4))
		cabccnf(False)
			
		lcampo = 515
		ccampo = 525
		linhas = 1

		rd1 = '22|35|110|(Relatorio: Lojas atualizadas)|'

		_mensagem = mens.showmsg("Relatótiro de lojas atualizadas!!\n.\nAguarde...")
		for r in dados.split('\n'):

			if r:
				
				cv.setFont('Helvetica', 9)
				cv.drawString(22,  float(lcampo), str( r.split('|')[0] ) )
				cv.drawString(122, float(lcampo), str( r.split('|')[1] ) )
				cv.drawString(222, float(lcampo), str( r.split('|')[2] ) )
				cv.setFont('Helvetica-Bold', 11)
				cv.drawString(600, float(lcampo), str( r.split('|')[3] ) )
						
				cv.setFillColor(HexColor('0x000000'))

				linhas +=1
				lcampo -= 10

			if linhas >= 48:

				cabccnf(True)
				mdl.rodape(cv,rd1,'','','','','','','','',6)

				pg +=1
				cv.addPageLabel(pg)
				cv.showPage()						
				linhas = 1
				lcampo = 515
				ccampo = 525
							
				cabccnf(False)

		cabccnf(True)
		mdl.rodape(cv,rd1,'','','','','','','','',6)
		cv.save()

		del _mensagem

		gerenciador.TIPORL = ''
		gerenciador.Anexar = nomeArquivo
		gerenciador.imprimir = True
		gerenciador.Filial   = Filial
				
		ger_frame=gerenciador(parent=par,id=-1)
		ger_frame.Centre()
		ger_frame.Show()

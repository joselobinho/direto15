#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import datetime
import StringIO
import commands

from conectar import *
from reportlab.lib.pagesizes import letter,A4,inch,landscape

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.graphics import shapes
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import PCMYKColor, PCMYKColorSep,Color, black, blue, red, green, yellow, orange, magenta, violet, pink, brown,HexColor
from reportlab.graphics.barcode.qr import QrCodeWidget 
from reportlab.graphics import renderPDF

from reportlab.graphics.barcode import code128
from reportlab.platypus import Frame
from reportlab.lib.units import mm

from prndireta import DavTermicas

alertas = dialogos()
acs     = acesso()
nF      = numeracao()
termica = DavTermicas()
formata = truncagem()
mens    = menssagem()

class impressao:
	
	def impressaoDav(self,_numeroDav,_frame,_imre,_emai,_devo,_custo, servidor="", expedicao = "", codigoModulo = "", enviarEmail = ""):

		self.flid  = 1
		self.fili  = login.identifi
		self.fram  = _frame
		self.expe  = expedicao
		
		self.numero_parcelas_lista = []
		self.numero_parcelas_pagina = False
		
		if expedicao.strip() == "":	self.expe = "F"

		if servidor !="":	self.fili = servidor
	
		self.conn  = sqldb()
		self.sql   = self.conn.dbc("Impressao do DAV", fil = self.fili, janela = self.fram )
		self.saida = False

		if self.sql[0] == True:
			
			self.NumeroDav = _numeroDav
			self.relatorio = relatorios()
			self.formatar  = truncagem()
			self.cabpadrao = relatorios()
			self.dh        = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
			self.cdEmpresa = login.emcodigo
			self.pg        = 1
			self.reimp     = _imre
			self.email     = _emai
			self.devolucao = _devo
			self.custodav  = _custo
			lemails        = listaemails()
			
			self.moTDev    = ''
			self.LevarCL   = ''
			self._clientes = ''
			finaliza       = True
			
			login.reimpre  = _imre
			self.__nd = 0

			_mensagem = mens.showmsg("Selecionando davs de vendas, devoluções!!\n\nAguarde...")
			
			_buscar = "SELECT * FROM cdavs WHERE cr_ndav='"+_numeroDav+"'"
			_bitems = "SELECT * FROM idavs WHERE it_ndav='"+_numeroDav+"'"

			"""  Sair codigo interno no dav """
			codigo_interno = True if len( login.filialLT[ self.fili ][35].split(";") ) >= 69 and login.filialLT[ self.fili ][35].split(";")[68] == "T" else False
			self.cliente_vai_retirar = "<< "+login.filialLT[ self.fili ][35].split(";")[84].upper()+" >>" if len( login.filialLT[ self.fili ][35].split(";") ) >= 85 and login.filialLT[ self.fili ][35].split(";")[84] else "<< CLIENTE VAI RETIRAR >>"
			
			if len( login.filialLT[ self.fili ][35].split(";") ) >= 3:	self.dav_modelo = login.filialLT[ self.fili ][35].split(";")[2]
			else:	self.dav_modelo = "1"
	
			if self.custodav == "CUS":	self.dav_modelo = "1"
			if self.dav_modelo.strip() == "":	self.dav_modelo = "1"
			
			""" Devolucao de Vendas - Troca as Tabelas """
			if _devo == "DEV":
				
				_buscar = _buscar.replace('cdavs','dcdavs')
				_bitems = _bitems.replace('idavs','didavs')
			
			if self.sql[2].execute(_buscar) !=0:

				self._controle = self.sql[2].fetchall()
				
				self.ct_cdclie = self._controle[0][3]  #-: Codigo do Cliente
				self.moTdev    = self._controle[0][79] #-: Motivo da Devolucao

				_mensagem = mens.showmsg("Selecionando cliente do dav!!\n\nAguarde...")
				self.cliente = 0 if not self.ct_cdclie.strip() else self.sql[2].execute("SELECT * FROM clientes WHERE cl_codigo='"+self.ct_cdclie+"'")
				if self.cliente !=0:	self._clientes = self.sql[2].fetchall()
				
				emailsc = lemails.listar(1,self.ct_cdclie,self.sql[2])
				
				ItemsPro =  self.sql[2].execute(_bitems)
				if ItemsPro !=0:

					_result = self.sql[2].fetchall()
				
					"""  Cria os dois modelos de pedidos em Impressoras Termicas   """
					_mensagem = mens.showmsg("Montando dav termica BEMATECH-Modelo1\n\nAguarde...")
					Termica1 = termica.bematech1(  self, Filial = self.fili, ii=_result, dd=self._controle, cc=self._clientes, rr=_imre  )

					_mensagem = mens.showmsg("Montando dav termica BEMATECH-Modelo2\n\nAguarde...")
					Termica2 = termica.bematech2(  self, Filial = self.fili, ii=_result, dd=self._controle, cc=self._clientes, rr=_imre  )

					_mensagem = mens.showmsg("Montando dav termica EPSON!!\n\nAguarde...")
					Termica3 = termica.davEpsonTMT20( self, Filial = self.fili, ii=_result, dd=self._controle, cc=self._clientes, rr=_imre )

					termicas = {'bematech1':Termica1,'bematech2':Termica2,'epsonTMT20':Termica3}

					for nd in range( 2 ):
						
						rPg = str( Decimal( ItemsPro / Decimal('23') ) ).split('.')
						Pgn = int( rPg[0] )
						if len( rPg ) == 2 and rPg[1] !="00":	Pgn +=1	
									
						_nomeArq = diretorios.usPasta+login.usalogin.lower()+_numeroDav+"_dav.pdf"
						_emaiArq = diretorios.usPasta+login.usalogin.lower()+_numeroDav+"_dav_e.pdf"
						pagina = str(self.pg).zfill(3)+' ['+str(Pgn).zfill(3)+']'

						self.td = format(self._controle[0][37],',')	#->[ Total do DAV ]
						
						if nd == 0:	self.cv = canvas.Canvas( _nomeArq, pagesize=landscape(A4) )
						if nd == 1:	self.cv = canvas.Canvas( _emaiArq, pagesize=landscape(A4) )
						self.__nd = nd

						"""
							Cabeçalho padrão do sistema
							Timbrado
						"""

						self.rlTipo = "D A V"
						if self.devolucao == "DEV":	self.rlTipo = "DEVOLUÇÃO"
						self.cidade = self.cabpadrao.cabecalhopadrao(self.cv,ImageReader,self.dh,str(pagina).zfill(3),self.fili,self.rlTipo,2) #->[ Cabecalhos ]

						#-----[ Totalizadores ]
						self.Tributos  = format( ( self._controle[0][28] + self._controle[0][29] + self._controle[0][30] + self._controle[0][70] + self._controle[0][71] ),',')
						self.cabecalho( nd )
				
						nItems = 1
						linhas = 0
						pItems = 0
						lcampo = 480
						kiTVnd = ""

						_mensagem = mens.showmsg("Montando layout do dav!!\n\nAguarde...")
						for i in _result:

							"""     Controla o Conteudo do KIT, Mostrar apenas o produto principal    """
							passar = True
							kiTAlT = False
							numkiT = i[91]

							if i[91] !="" and kiTVnd != i[91]:	kiTAlT = True
							if i[91] !="" and kiTVnd == i[91]:	passar = False
							kiTVnd = i[91]
							
							quantidade_devolucao = Decimal("0.0000")
							quantidade_entregada = Decimal("0.0000")
							devolucao_ocorrencias= 0

							if passar == True:
								
								_codigoProd    = i[5]
								_desProduTo    = i[7]
								_quantidade    = self.formatar.intquantidade(i[12])
								_ValorUnita    = format(i[11],'.2f') if len( login.filialLT[ self.fili ][35].split(";") ) >=66 and login.filialLT[ self.fili ][35].split(";")[65] == "T" else format(i[11],',')
								_UnidadePro    = i[8]
								_ValorTotal    = format(i[13],',')
								self.ValorTDav = format(i[13],',')
								_referencia    = i[88]
								_endereco      = i[10]

								"""  Sair codigo interno na coluna codigo  { MAD-CIA SPA 07-12-2016 }  """
								if codigo_interno and self.sql[2].execute("SELECT pd_intc FROM produtos WHERE pd_codi='"+str( i[5] )+"'"):

									__codigo_interno = self.sql[2].fetchone()[0]
									if __codigo_interno.strip():	_codigoProd = __codigo_interno.strip()
									
								if ( i[15] + i[16] + i[17] ) > 0: #->[Medidas do Cliente COM X LAR X EXP]

									_ValorUnita = format(i[14],',')
									_quantidade = self.formatar.intquantidade(i[23])
									_UnidadePro = "PÇ"

								"""   Alerar os dados se o produto for KIT   """
								if kiTAlT == True:
									
									if len( i[91].split('|') ) >= 2:	_codigoProd, _desProduTo = i[91].split('|')[0],i[91].split('|')[1]
									_ValorUnita, _ValorTotal = self.reTKiTvlr( _result, numkiT, i[92] ) #-: Retorna o valor unitario e Total do KIT

									_quantidade = self.formatar.intquantidade(i[92])
									_UnidadePro = "KT"
									_referencia = ""

								_ValorUnita = nF.eliminaZeros( str( _ValorUnita ) )	

								"""   Venda com estoque negativo   """
								if i[90] !=None and i[90] !='':

									self.cv.setFont('Helvetica', 7)
									self.cv.setFillGray(0.1,0.1) 
									self.cv.rect(20,lcampo-3,70,15, fill=1) #--: Fundo do cabecalho
									self.cv.setFont('Helvetica', 6)

									self.cv.setFillColor(HexColor('0xA52A2A'))
									self.cv.drawRightString(88,lcampo+7,"Autorizado")
									self.cv.setFont('Helvetica', 7)
									self.cv.setFillColor(HexColor('0x000000'))

								if self.dav_modelo in ["1","6"]:
									
									qq = Decimal("0.0000")
									self.cv.setFont('Helvetica', 7)
									self.cv.drawString(23,( lcampo - 2 ),  i[0]) #-------->[ Item ]
									self.cv.setFont('Helvetica-Bold', 7)
									self.cv.drawString(40, lcampo, _codigoProd) #-------->[ Codigo ]
									self.cv.setFont('Helvetica', 5 )
									self.cv.drawString(21,( lcampo+6 ),  i[48] ) #--: Filial
									self.cv.setFont('Helvetica-Bold', 7.5)
									if i[25] !='':	self.cv.drawString(100,lcampo+2, _desProduTo[:80]) #-------->[ Descricao dos Produtos ]
									else:	self.cv.drawString(100,lcampo+2, _desProduTo[:80]) #-------->[ Descricao dos Produtos ]

									if i[91] !="":

										self.cv.setFillColor(HexColor('0x4D4D4D'))
										self.cv.setFont('Helvetica', 4)
										self.cv.drawString(40,lcampo+7, "KIT Nº: "+str( i[91].split("|")[0] ) )
												
									self.cv.setFillColor(HexColor('0x000000'))
									self.cv.setFont('Helvetica', 7.5)
									
									self.cv.drawString(377,lcampo,_UnidadePro) #->[ Unidade ]
									self.cv.setFont('Helvetica-Bold', 9)
									self.cv.drawRightString(440,lcampo, _quantidade )
									self.cv.drawRightString(500,lcampo, _ValorUnita )
									self.cv.drawRightString(560,lcampo, _ValorTotal )

									self.cv.setFont('Helvetica-Bold', 8)
									self.cv.drawString(565,lcampo-2,i[9]) #-->[ Fabricante]
									self.cv.setFont('Helvetica', 7)
									
									self.cv.drawString(565,lcampo+5.5,_referencia) #-->[ Referencia ]

								elif self.dav_modelo in ["2","4"]:

									self.cv.setFont('Helvetica-Bold', 7.5)
									self.cv.drawString(23,( lcampo ),   _codigoProd) #--: Codigo
									self.cv.setFont('Helvetica', 6 )
									self.cv.drawString(23,lcampo+6,  i[48] ) #--: Filial
									self.cv.setFont('Helvetica-Bold', 7.5)
									self.cv.drawRightString(148,lcampo,_quantidade)
									self.cv.drawString(152,lcampo,_UnidadePro) #---: Unidade
									if i[25] !='':	self.cv.drawString(172,lcampo+2, _desProduTo[:80]) #-: Descricao dos Produtos 
									else:	self.cv.drawString(172,lcampo+2, _desProduTo[:80]) #-----------: Descricao dos Produtos 

									if i[91] !="":

										self.cv.setFont('Helvetica', 4)
										self.cv.setFillColor(HexColor('0x1A1A1A'))
										self.cv.drawString(92,lcampo+7, "KIT Nº: "+str( i[91].split("|")[0] ) )
									self.cv.setFillColor(HexColor('0x000000'))
									self.cv.setFont('Helvetica', 7.5)

									self.cv.drawString(602,lcampo-2,i[9]) #----------: Fabricante
									if self.dav_modelo == "4":	self.cv.drawString(602,lcampo+5.5,_endereco) #-: endereco
									else:	self.cv.drawString(602,lcampo+5.5,_referencia) #-: Referencia
									self.cv.drawRightString(698,lcampo,i[75]) #------: Tabela
									self.cv.drawRightString(758,lcampo,_ValorUnita)
									self.cv.drawRightString(822,lcampo,_ValorTotal)

								elif self.dav_modelo in ["3","5"]:

									self.cv.setFont('Helvetica', 7)
									self.cv.drawString(23,( lcampo - 2 ),  i[0]) #-------->[ Item ]
									self.cv.setFont('Helvetica-Bold', 7)
									self.cv.drawString(40, lcampo, _codigoProd) #-------->[ Codigo ]
									self.cv.setFont('Helvetica', 5 )
									self.cv.drawString(21,( lcampo+6 ),  i[48] ) #--: Filial
									self.cv.setFont('Helvetica-Bold', 7.5)
									if i[25] !='':	self.cv.drawString(100,lcampo+2, _desProduTo[:80]) #-------->[ Descricao dos Produtos ]
									else:	self.cv.drawString(100,lcampo+2, _desProduTo[:80]) #-------->[ Descricao dos Produtos ]

									if i[91] !="":

										self.cv.setFillColor(HexColor('0x4D4D4D'))
										self.cv.setFont('Helvetica', 4)
										self.cv.drawString(40,lcampo+7, "KIT Nº: "+str( i[91].split("|")[0] ) )
										
									self.cv.setFillColor(HexColor('0x000000'))
									self.cv.setFont('Helvetica', 7.5)
									
									self.cv.drawString(377,lcampo,_UnidadePro) #->[ Unidade ]

									self.cv.setFont('Helvetica-Bold', 9)
									self.cv.drawRightString(430,lcampo, _quantidade )
									self.cv.drawRightString(440,lcampo,i[75]) #------: Tabela
									self.cv.drawRightString(500,lcampo, _ValorUnita )
									self.cv.drawRightString(560,lcampo, _ValorTotal )
									
								if self.custodav == "CUS":

									_ToTalPD = Decimal( _ValorTotal.replace(',','') )
									_ToTalCU = Decimal( i[78] )
									_margem  = _Percen = Decimal("0.00")
									
									if _ToTalPD !=0 and _ToTalCU !=0:
										_margem = ( _ToTalPD - _ToTalCU )
										_Percen = self.formatar.trunca(3, ( _margem / _ToTalPD * 100 ) )
										
									self.cv.setFont('Helvetica', 8)
									self.cv.setFillColor(HexColor('0x1C1CD5'))
									self.cv.drawRightString(693,lcampo,format(i[77],',') )
									self.cv.drawRightString(740,lcampo,format(i[78],',') )
									self.cv.drawRightString(790,lcampo,format(_margem,',') )
									self.cv.drawRightString(824,lcampo,str( _Percen )+"%")
									self.cv.setFillColor(HexColor('0x000000'))

								self.cv.setFont('Helvetica-Bold', 8)
								if self.custodav != "CUS" and self.dav_modelo in ["1","6"]:	self.cv.drawString(653,lcampo,i[10]) #->[ Endereco]
								if self.custodav != "CUS" and self.dav_modelo in ["1","6"]:	self.cv.drawString(703,lcampo,i[75]) #->[ Tabela ]

								self.cv.setFont('Helvetica-Bold', 6)
								if self.custodav != "CUS" and  self.dav_modelo == "1" and ( i[15] + i[16] + i[17] ) > 0: #->[Medidas do Cliente COM X LAR X EXP]

									_medidas = self.formatar.intquantidade(i[23])+" PÇ "+  str(i[15])+'CM'
									if i[16] > 0:	_medidas += " "+ str(i[16])+'LG'
									if i[17] > 0:	_medidas += " "+ str(i[17])+'EX'
									
									self.cv.drawString(713, lcampo,_medidas)

								if self.custodav != "CUS" and  self.dav_modelo == "6": #-: Quantidade - Quantidade entregue

									self.cv.setFont('Helvetica-Bold', 8)
									__s = self.formatar.intquantidade( Decimal( _quantidade.replace(',','') ) - i[64] )
									if Decimal( __s ):	self.cv.drawRightString(760, lcampo, str( __s ) )
									self.cv.setFont('Helvetica-Bold', 6)

								elif self.custodav != "CUS" and self.dav_modelo in ["2","4"] and ( i[15] + i[16] + i[17] ) > 0 and kiTAlT == False: #->[Medidas do Cliente COM X LAR X EXP]

									_medidas = self.formatar.intquantidade(i[23])+" PÇ "+  str(i[15])+'CM'
									if i[16] > 0:	_medidas += " "+ str(i[16])+'LG'
									if i[17] > 0:	_medidas += " "+ str(i[17])+'EX'
									
									self.cv.drawString(492, lcampo,_medidas)

								elif self.custodav != "CUS" and self.dav_modelo in ["3","5"] and ( i[15] + i[16] + i[17] ) > 0: #->[Medidas do Cliente COM X LAR X EXP]
									
									_medidas = self.formatar.intquantidade(i[23])+" PÇ "+  str(i[15])+'CM'
									if i[16] > 0:	_medidas += " "+ str(i[16])+'LG'
									if i[17] > 0:	_medidas += " "+ str(i[17])+'EX'
									
									self.cv.setFont('Helvetica-Bold', 9)
									self.cv.drawString(565, lcampo, _medidas)

								"""   Cliente vai retirar  """
								self.cv.setFont('Helvetica', 6)
								if ( i[62] ) != '' and self._controle[0][41] == "1": #->[ Cliente Vai Levar ]
									
									""" Cor de fundo no cabecalho de Titulos """
									lcampo -= 15
									linhas +=1
									
									self.cv.setFillColor(HexColor('0x851F1F'))
									if self.dav_modelo in ["2","4"]:	self.cv.drawString(172, lcampo,self.cliente_vai_retirar)
									else:	self.cv.drawString(100, lcampo,self.cliente_vai_retirar)
									self.cv.setFillColor(HexColor('0x000000'))
								
									if linhas >= 22:
										nItems,lcampo = self.mudaPagina(Pgn)
										linhas = 0

								"""  Mostra dados de expedicao e devolucao  """
								if self.dav_modelo in ["1","2","3","4","5","6"]:
	
									if self.sql[2].execute("SELECT cr_ndav FROM dcdavs WHERE cr_cdev='"+ i[2]+"'"):
	
										lista_devolucao = self.sql[2].fetchall()
										for ndev in lista_devolucao:

											if self.sql[2].execute("SELECT it_quan FROM didavs WHERE it_ndav='"+ ndev[0] +"' and it_codi='"+ _codigoProd +"'"):

												for nqt in self.sql[2].fetchall():
													quantidade_devolucao +=nqt[0]
													devolucao_ocorrencias +=1

									if quantidade_devolucao or i[64]: 

										""" Cor de fundo no cabecalho de Titulos """
										lcampo -= 15
										linhas +=1

										__oc = "  Ocorrencias: " + nF.eliminaZeros( str( formata.intquantidade( devolucao_ocorrencias ) ) ) if devolucao_ocorrencias else ""
										__dv = "Devolução: " + nF.eliminaZeros( str( formata.intquantidade( quantidade_devolucao ) ) ) if quantidade_devolucao else ""
										__ex = "  Expedição avulso: " + nF.eliminaZeros( str( formata.intquantidade( i[64] ) ) ) if i[64] else ""
										
										self.cv.setFillColor(HexColor('0x851F1F'))
										self.cv.setFont('Helvetica-Bold', 8)
										if self.dav_modelo in ["2","4"]:	self.cv.drawString(172, lcampo, __dv + __oc + __ex )
										else:	self.cv.drawString(100, lcampo, __dv + __oc + __ex )
										self.cv.setFont('Helvetica', 6)
										self.cv.setFillColor(HexColor('0x000000'))
									
										if linhas >= 22:
											nItems,lcampo = self.mudaPagina(Pgn)
											linhas = 0

								""" Impressao do corte """
								if i[25] and i[25].split('\n')[0]:
								
									self.cv.setFont('Helvetica', 6)
									for x in i[25].split('\n'):
								
										if x:
								
											lcampo -= 15
											linhas +=1
											if self.dav_modelo in ["2","4"]:	self.cv.drawString(172,lcampo,x)
											else:	self.cv.drawString(100,lcampo,x)

											if linhas >= 22:
												nItems,lcampo = self.mudaPagina(Pgn)
												linhas = 0
								
								"""  Codigo de identificacao   """
								if  str( i[95] ).split("|")[0] and ":" in str( i[95] ):

									lcampo -= 15
									linhas +=1

									if self.dav_modelo == "1":	self.cv.drawString(100,lcampo, str( i[95].split("|")[0].strip().title() ) ) #-->[ Codigo de Identificacao do Produto Tinta ]
									else:	self.cv.drawString(172,lcampo, str( i[95].split("|")[0].strip().title() ) ) #-->[ Codigo de Identificacao do Produto Tinta ]

								"""  Numero de series """
								if i[98]:
									
									lcampo -= 15
									linhas +=1
									
									self.cv.setFont('Helvetica', 6)

									if self.dav_modelo == "1":	self.cv.drawString(100,lcampo, "Seires: [ "+i[98]+ " ]" )
									else:	self.cv.drawString(172,lcampo, "Seires: [ "+i[98]+ " ]" )

								"""  Embalagens - Caixas """
								if i[99]:
									
									lcampo -= 15
									linhas +=1
									
									self.cv.setFont('Helvetica', 8)

									if self.dav_modelo in ["1","6"]:	self.cv.drawString(100,lcampo, i[99] )
									else:	self.cv.drawString(172,lcampo, i[99] )
									self.cv.setFont('Helvetica', 6)

								self.separa(lcampo,nItems)
								if nItems !=25:	self.cv.line(20, ( lcampo - 3 ), 825, ( lcampo - 3 ) ) #-->[ Linha  de divisao TOTALIZACAO ]

								""" Muda de Pagina """
								lcampo -= 15
								pItems +=1

								linhas +=1
								
								if linhas >= 22 and pItems < ItemsPro:
									nItems,lcampo = self.mudaPagina(Pgn)
									linhas = 0

						""" Mostra a Totalizacao so no ultimo """
						self.cv.setFont('Helvetica-Bold', 8)

						self.cv.drawRightString(823,140,format(self._controle[0][36],','))				
						self.cv.drawRightString(823,130, format(self._controle[0][24],','))				
						self.cv.drawRightString(823,120, format(self._controle[0][23],','))				
						self.cv.drawRightString(823,110, format(self._controle[0][25],','))				
						self.cv.drawRightString(823,100,self.Tributos)				
						self.cv.drawRightString(823,90, format(self._controle[0][37],','))

						if self.custodav == "CUS":
							
							TCusto = Decimal( self._controle[0][93] )
							TVlrTo = Decimal( ( self._controle[0][36] + self._controle[0][24] ) - self._controle[0][25]  )
							__marg = Decimal("0.00")
							
							self.cv.setFillColor(HexColor('0x1C1CD5'))
							self.cv.drawString(540,130,"{ Totalização do Custo }")
							if TCusto !=0 and TVlrTo !=0:	__marg = self.formatar.trunca(3, ( ( TVlrTo - TCusto ) / TVlrTo * 100 ) )
							
							self.cv.drawString(540,110, "Total Custo: ")
							self.cv.drawString(540,100, "Lucro: ")
							self.cv.drawString(540, 90, "Margem: ")
							self.cv.drawRightString(630,110, format(TCusto,','))				
							self.cv.drawRightString(630,100, format(( TVlrTo - TCusto ),','))				
							self.cv.drawRightString(630, 90, str( __marg )+"%")				
							self.cv.setFillColor(HexColor('0x000000'))

						if self.numero_parcelas_pagina and self.numero_parcelas_lista and len( login.filialLT[ self.fili ][35].split(";") ) >= 110 and login.filialLT[ self.fili ][35].split(";")[109] == "T":
							
							self.cv.setFillColor(HexColor('0xB72020'))
							self.cv.setFont('Helvetica-Bold', 13)
							self.cv.drawString(554, 62, "{ Lista de parcelamento na proxima pagina }")
							self.cv.setFillColor(HexColor('0x000000'))
							
							self.mudaPagina(Pgn)
							numero_parcelas = 1
							lcampo = 450

							self.cv.setFont('Helvetica-Bold', 20)

							self.cv.drawString(100,470, u"{ Parcelamento }" )
							self.cv.setFont('Helvetica', 10)
							
							for np in self.numero_parcelas_lista:
								
								valor = np.split('|')[2].replace(',','')
								self.cv.drawString(100,lcampo, str( numero_parcelas ).zfill(2)+"  "+ np.split('|')[0]+"   "+np.split('|')[1] )
								self.cv.drawRightString(300,lcampo, format( Decimal( valor ),',') )

								self.cv.line(100, lcampo-5, 825, lcampo-5)
								numero_parcelas +=1
								lcampo -=15
							
						self.cv.showPage()
						self.cv.save()
						
					tipo_dav = 'P'
					if self.devolucao:	tipo_dav = 'D'
					if self._controle[0][41] == '2':	tipo_dav = 'O'

					del _mensagem
					
					if codigoModulo != "EXPD":

						gerenciador.imprimir = acs.acsm(codigoModulo,True)
						gerenciador.enviarem = acs.acsm(enviarEmail,True) 
						gerenciador.Anexar   = _nomeArq
						gerenciador.arqEma   = _emaiArq
						gerenciador.emails   = emailsc
						gerenciador.TIPORL   = "DAV-"+tipo_dav
						gerenciador.cdclie   = self.ct_cdclie
						gerenciador.numdav   = _numeroDav
						gerenciador.parente  = self
						gerenciador.Filial   = self.fili
						gerenciador.Termica1 = Termica1
						gerenciador.Termica2 = Termica2
						gerenciador.impressoras_termicas = termicas

						ger_frame=gerenciador(parent=_frame,id=-1)
						ger_frame.Centre()
						ger_frame.Show()
			
			else:	finaliza = True

			self.conn.cls(self.sql[1])
			if finaliza == False:	alertas.dia(_frame,"Dav Nº "+str(_numeroDav)+', não localizado!!\n'+(' '*100),'Consulta e Impressão/Reimpressão de DAVs')
			if codigoModulo == "EXPD":	return _nomeArq

	def reTKiTvlr( self, _rs, nkiT, qT ):

		vlu = Decimal("0.000")
		vlT = Decimal("0.000")

		for i in _rs:

			if i[91] == nkiT:

				vlT+= i[13]
				vlu = ( vlT / qT )
				
		return format(vlu,','), format(vlT,',')
			
	def gravaImpressao(self):

		_conn  = sqldb()
		_sql   = _conn.dbc("Caixa: Recebimento de Devolução", fil = self.fili, janela = self.fram )
	
		if _sql[0] == True:
		 
			__imp = self._controle[0][85]
			if __imp == "None" or __imp==None:	__imp = ''
			impresso = str(__imp)+"\n"+str(datetime.datetime.now().strftime("%d/%m/%Y %T"))+' '+str(login.usalogin)+"|"+str( self.expe )
			try:
				imp = "UPDATE cdavs SET cr_impr=%s WHERE cr_ndav=%s"
				_sql[2].execute( imp, ( impresso, self.NumeroDav ) )
				_sql[1].commit()
					
			except Exception, _reTornos:
				_sql[1].rollback()

			_conn.cls(_sql[1])
			
	def mudaPagina(self,_pg):

		self.pg +=1
		pagina = str(self.pg).zfill(3)+' ['+str(_pg).zfill(3)+']'

		self.cv.addPageLabel(self.pg)
		self.cv.showPage()						
		self.cidade = self.cabpadrao.cabecalhopadrao(self.cv,ImageReader,self.dh,pagina.zfill(3),self.fili,self.rlTipo,2) #->[ Cabecalhos ]
		self.cabecalho(self.__nd)

		return 1,480
				
	def separa(self,coluna,items):

		if items == 25:	adiciona = 2
		else:	adiciona = 3
		
		if self.dav_modelo in ["1","6"]:
	
			self.cv.line(39, 502, 39, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(100,502,100, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(375,502,375, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(390,502,390, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(442,502,442, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(502,502,502, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(562,502,562, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(652,502,652, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]

		elif self.dav_modelo in ["2","4"]:

			self.cv.line(90, 502, 90, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(150,502,150, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(170,502,170, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(490,502,490, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(600,502,600, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(690,502,690, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(700,502,700, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]->Tabela
			self.cv.line(760,502,760, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]

		if self.dav_modelo in ["3","5"]:
	
			self.cv.line(39, 502, 39, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(100,502,100, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(375,502,375, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(390,502,390, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			if self.dav_modelo == "3":	self.cv.line(432,502,432, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(442,502,442, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(502,502,502, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(562,502,562, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]

		if self.custodav == "CUS":	
				
			self.cv.line(695,502,695, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
			self.cv.line(742,502,742, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]

		else:
			
			if self.dav_modelo in ["1","6"]:
				
				self.cv.line(700,502,700, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
				self.cv.line(711,502,711, ( coluna - adiciona ) ) #-->[ Linhas p/Divisao dos campos ]
		
	def cabecalho( self, _nd ):

		self.numero_parcelas_lista = []
		self.numero_parcelas_pagina = False

		rclocal = False
		if self._controle[0][95] !=None and self._controle[0][95] !='':
			
			for rcl in self._controle[0][95].split('|'):
				if rcl !='' and rcl[:2] == "12":	rclocal = True

		vem_buscar = True if len( self._controle[0][67].split('|') ) >= 1 and self._controle[0][67].split('|')[0] == "T" else False
		if self._controle[0][41] == "2" or self.reimp or self.email or self._controle[0][40][:2] =='12' or self.devolucao == "DEV" or rclocal or vem_buscar:

			_orcamento = self._controle[0][41]
			self.cv.saveState()
			self.cv.setFont("Courier", 70) 
			self.cv.setFillGray(0.2,0.2) 
			self.cv.translate(300,50) 
			self.cv.rotate(45) 
			if self.devolucao == '' and _orcamento == "2":	self.cv.drawCentredString (250, 100, "Orçamento!!!")
			if vem_buscar:	self.cv.drawCentredString (250, 100, "VEM BUSCAR")
			if self.devolucao == 'DEV':	self.cv.drawCentredString (250, 160, "Devolução!!!")

			if self.reimp and self._controle[0][85]:	self.cv.drawCentredString (250, 200, "Reimpressão")
			if _nd == 1:	self.cv.drawCentredString (250, 40,  "E m a i l")
			self.cv.setFillColor(HexColor('0xFFC0CB'))
			if self._controle[0][74] == '3':	self.cv.drawCentredString (320, -50, "DAV Cancelado")
			self.cv.setFillColor(HexColor('0x000000'))
			self.cv.setFont("Courier", 20) 

			self.cv.setFillGray(0,0.5) 
			self.cv.translate(-330,50) 
			self.cv.rotate(-45)

			if rclocal == True:	self.cv.drawString(390,708,"{Receber Local} ")
			self.cv.restoreState()

		self.cv.setFont('Helvetica-Bold', 20)
		if self._controle[0][41] == "2":	self.cv.setFont('Helvetica-Bold', 17)
		if self.devolucao == "DEV":	self.cv.setFont('Helvetica-Bold', 14.5)
		
		if self._controle[0][41] == "1" and self.devolucao != "DEV":	self.cv.drawString(720,504,"P E D I D O")
		if self._controle[0][41] == "1" and self.devolucao == "DEV":	self.cv.drawString(700,505.8,"D E V O L U Ç Ã O")
		if self._controle[0][41] == "2":	self.cv.drawString(675,506.5,"O R Ç A M E N T O")

		self.cv.line(20, 520,825,520) #-->[ Linha  do Nome do Cliente CPF-CNPJ Pedido-Orcamento]
		self.cv.line(20, 148,825,148) #-->[ Linha  de divisao TOTALIZACAO ]
		self.cv.line(20, 85,825,85) #-->[ Linha  de divisao TOTALIZACAO ]
		self.cv.line(535,148,535, 85) #-->[ Linha  de divisao TOTALIZACAO ]
		self.cv.line(730,20,730, 60) #-->[ Linha  de divisao TOTALIZACAO ]

		self.cv.rect(20, 73, 805,478, fill=0) #-->[ Quadro Principal ]
			
		self.cv.setFont('Helvetica-Bold', 8)
		self.cv.drawString(23, 151,"Emissão: ["+self._controle[0][43]+'-'+self._controle[0][44]+' '+\
		format(self._controle[0][11],'%d/%m/%Y')+" "+str(self._controle[0][12])+"] Usuário: {"+self._controle[0][9].strip()+"}")

		b128 = code128.Code128(str( self.NumeroDav ), barHeight=22, barWidth=0.7,stop=1)
		b128.drawOn(self.cv, 590, 555)
			
		self.cv.setFont('Helvetica', 8)
		self.cv.drawString(720,140,"Produtos:")
		self.cv.drawString(720,130,"Acréscimo:")
		self.cv.drawString(720,120,"Frete:")
		self.cv.drawString(720,110,"Desconto:")
		self.cv.drawString(720,100,"Tributos:")
		self.cv.drawString(720,90,"Total do DAV:")

		#-------------[ Cabecalho do DAV ]
		self.cv.setFont('Helvetica-Bold', 9)
		if self.devolucao == 'DEV':	self.cv.drawString(717,540,"Nº DAV: "+str(self.NumeroDav))
		else:	self.cv.drawString(720,540,"Nº DAV: "+str(self.NumeroDav))
			
		self.cv.setFont('Helvetica-Bold', 10)	
		if self.devolucao == '':	self.cv.drawString(340,540,"DOCUMENTO AUXILIAR DE VENDA")

		if self.devolucao == 'DEV':

			self.cv.drawString(360,530,"DEVOLUÇÂO DE VENDAS")
			self.cv.drawString(345,75,"DEVOLUÇAO DE MERCADORIAS")

		if self.devolucao == '':

			self.cv.drawString(100,525,"NÂO É DOCUMENTO FISCAL, NÂO É VALIDO COMO RECIBO E COMO GARANTIA DE MERCADORIA, NÂO COMPROVA PAGAMENTO")
			self.cv.drawString(290,75,"É VEDADA A AUTENTICAÇÃO DESTE DOCUMENTO")

		self.cv.setFont('Helvetica', 9)
		if self._controle[0][78] !='' and self.custodav != "CUS":

			self.cv.drawString(746,532,"{ Vinculado }")
			self.cv.drawString(746,522,"{ "+str(self._controle[0][78])+" }")

		self.cv.setFont('Helvetica-Bold', 8)
		self.cv.drawString(25, 512,"NOME DO CLIENTE: "+ self._controle[0][4])
		self.cv.drawString(400,512,"CPF-CNPJ: "+self.formatar.formata(1,self._controle[0][39]))
		self.cv.setFont('Helvetica', 8)
		if self._controle[0][102] !=None and self._controle[0][102] !='':	self.cv.drawString(25,503,"Comprador/Portador:  "+ str( self._controle[0][102] ).upper() )
		
		if self._controle[0][90]:

			fechamento = "em aberto"
			if self.sql[2].execute("SELECT rm_dtent FROM romaneio WHERE rm_roman='"+ self._controle[0][90] +"'"):
				
				__data = self.sql[2].fetchone()[0]
				if __data:	fechamento = format( __data,"%d/%m/%Y" )
				
			self.cv.setFont('Helvetica-Bold', 8)
			self.cv.setFillColor(HexColor('0xA52A2A'))
			self.cv.drawString(520,513,"{ Expedição de entrega } " )
			
			self.cv.drawString(520,504,"Romaneio: "+ self._controle[0][90] + u"  Previsão: "+ fechamento )
			self.cv.setFont('Helvetica', 8)
			self.cv.setFillColor(HexColor('0x000000'))
			 
		if self.dav_modelo in ["1","6"]:
			
			self.cv.setFont('Helvetica-Bold', 7)
			self.cv.drawString(22, 495, "Item")
			self.cv.drawString(41, 495, "Código")
			self.cv.drawString(101,495,"Descrição dos Produtos")
			self.cv.drawString(377,495,"UN")
			self.cv.drawString(391,495,"Quantidade")
			self.cv.drawString(443,495,"Vl.Unitário")
			self.cv.drawString(503,495,"Valor Total")
			self.cv.drawString(564,495,"Referência/Fabricante")

		if self.dav_modelo in ["2","4"]:
			
			self.cv.setFont('Helvetica-Bold', 7)
			self.cv.drawString(22, 495, "Código")
			self.cv.drawString(110,495, "Quantidade")
			self.cv.drawString(152,495, "UN")
			self.cv.drawString(172,495, "Descrição dos Produtos")
			self.cv.drawString(492,495, "Médidas de Corte")
			if self.dav_modelo == "4":	self.cv.drawString(602,495, "Endereço/Fabricante")
			else:	self.cv.drawString(602,495, "Referência/Fabricante")
			self.cv.drawString(690,495, "TB")
			self.cv.drawString(723,495, "Vl.Unitário")
			self.cv.drawString(785,495, "Valor Total")

		if self.dav_modelo in ["3","5"]:

			self.cv.setFont('Helvetica-Bold', 7)
			self.cv.drawString(22, 495, "Item")
			self.cv.drawString(41, 495, "Código")
			self.cv.drawString(101,495,"Descrição dos Produtos")
			self.cv.drawString(377,495,"UN")
			self.cv.drawString(391,495,"Quantidade")
			if self.dav_modelo == "3":	self.cv.drawString(432,495,"TB")
			self.cv.drawString(443,495,"Vl.Unitário")
			self.cv.drawString(503,495,"Valor Total")
			self.cv.drawString(653,495,"Medidas de corte >--> Observação")

		if self.custodav == "CUS":		

			self.cv.setFillColor(HexColor('0x1C1CD5'))
			self.cv.drawString(653,495,"Custo UNT")
			self.cv.drawString(696,495,"Custo TOTAL")
			self.cv.drawString(744,495,"Margem de Lucro")
			self.cv.setFillColor(HexColor('0x000000'))
			
		else:
			
			if self.dav_modelo in ["1","6"]:
				
				self.cv.drawString(653,495,"Endereço")
				if self.dav_modelo == "1":	self.cv.drawString(712,495,"Medidas de Corte")
				self.cv.drawString(701,495,"TB")

				if self.dav_modelo == "6":	self.cv.drawString(712,495,"Saldo a retirar")

		""" Linhas do Totalizador """
		lh = 138
		for l in range(5):

			self.cv.line(715,lh,825,lh)
			lh -=10

		self.cv.setFillGray(0.1,0.1) 
		self.cv.rect(20,492,805,10, fill=1) #--: Fundo do cabecalho
		self.cv.rect(715,85,110,63, fill=1) #-: Fundo do totalizador
		self.cv.setFillColor(HexColor('0x000000'))

		self.cv.setFont('Helvetica', 7)
		self.cv.drawString(25,50,self.cidade[0]+", "+self.dh)
		
		""" Endereco """
		eEntrega = eBairro = eCidade = ''		
		if self.cliente !=0:
		
			""" Selecao do Endereco """
			if self._controle[0][76] == "1": #->[ Endereco ]

				eEntrega = self._clientes[0][8]+" "+self._clientes[0][13]+" "+self._clientes[0][14]
				eBairro  = self._clientes[0][9]+" [ Telefone(s): "+str( self._clientes[0][17] )+"  "+str( self._clientes[0][18] )+' ]'
				eCidade  = self._clientes[0][10]+" CEP: "+str(self._clientes[0][12])+" ESTADO: "+str(self._clientes[0][15])

			else: #->[ Endereco de Entrega ]

				eEntrega = self._clientes[0][20]+" "+self._clientes[0][25]+" "+self._clientes[0][26]
				eBairro  = self._clientes[0][21]+" [ Telefone(s): "+str( self._clientes[0][17] )+"  "+str( self._clientes[0][18] )+' ]'
				eCidade  = self._clientes[0][22]+" CEP: "+str(self._clientes[0][24])+" ESTADO: "+str(self._clientes[0][27])

			if eEntrega.strip() == '': #-->[ Endereço de Cliente, Não Tiver Entrega ]

				eEntrega = self._clientes[0][8]+" "+self._clientes[0][13]+" "+self._clientes[0][14]
				eBairro  = self._clientes[0][9]+" [ Telefone(s): "+str( self._clientes[0][17] )+"  "+str( self._clientes[0][18] )+' ]'
				eCidade  = self._clientes[0][10]+" CEP: "+str(self._clientes[0][12])+" ESTADO: "+str(self._clientes[0][15])

		self.cv.setFont('Helvetica-Bold', 10)
		if self._controle[0][21] != None:	self.cv.drawString(716,151,"ENTREGA: "+format(self._controle[0][21],"%d-%m-%Y"))

		self.cv.setFont('Helvetica-Bold', 7)
		self.cv.drawString(280,140,"[ ENDEREÇO ] ")
		
		self.cv.drawString(280,133,eEntrega)
		self.cv.drawString(280,125,eBairro)
		self.cv.drawString(280,118,eCidade)

		""" Mostrar as Formas de Pagamentos """
		self.cv.rect(20, 20, 805,40, fill=0) #-->[ Quadro de Formas de Pagamentos ]
		
		if self._controle[0][95] != None and self.custodav != "CUS":

			self.cv.setFont('Helvetica-Bold', 7)
			self.cv.drawString(540,150,"{ Formas de Pagamentos, Parcelas }")
			self.cv.setFont('Helvetica', 8)

			b = 139
			qT = 0
			
			#-:Pre-Recebimento do Vendedor
			
			if self._controle[0][97] == None or self._controle[0][97] == "":
				
				for lP in self._controle[0][95].split('|'):

					if lP !='':
						
						etc = ""
						if qT == 5:	etc = "..."
						if qT <= 5:
		
							__valor = ""
							self.cv.drawString( 537,b,lP.split(";")[0]+etc )
							self.cv.setFont('Helvetica', 7)
							if lP.split(";")[0].split("-")[0] == "12":self.cv.drawString( 617,b,lP.split(";")[3].split("-")[1] )
							else:	self.cv.drawString( 617,b,lP.split(";")[1] )
						
							self.cv.setFont('Helvetica', 8)
							self.cv.drawRightString(714,b, lP.split(';')[2])
							b -= 10
							
						if lP.split(";")[0].split("-")[0] == "12":	__valor = lP.split(";")[3].split("-")[1]
						else:	__valor = lP.split(";")[1]
						self.numero_parcelas_lista.append( lP.split(";")[0]+"|"+__valor+"|"+lP.split(';')[2] )
							
						qT +=1
						if qT == 6:	self.numero_parcelas_pagina = True

			#---:Recebimento do Caixa
			elif self._controle[0][97] != None and self._controle[0][97] != "":
				
				for lP in self._controle[0][97].split('|'):
					
					if lP != None and lP != "":
						
						etc = ""
						if qT == 5:	etc = "..."
						if qT <= 5:

							self.cv.drawString( 537,b,lP.split(";")[2]+etc )
							self.cv.drawString( 617,b,lP.split(";")[1] )
							self.cv.drawRightString(714,b, lP.split(';')[3])
							b -= 10

						#if lP.split(";")[0].split("-")[0] == "12":	__valor = lP.split(";")[3].split("-")[1]
						#else:	__valor = lP.split(";")[1]
						self.numero_parcelas_lista.append( lP.split(";")[2]+"|"+lP.split(";")[1]+"|"+lP.split(';')[3])
						qT +=1
						if qT == 6:	self.numero_parcelas_pagina = True
						#if qT == 6:	break
				
		self.cv.setFont('Helvetica', 7)

		""" Ponto Referencia """
		if self._controle[0][38].strip() !='' and self.custodav != "CUS":

			self.cv.setFont('Helvetica-Bold', 7)
			self.cv.drawString(280,109,"[ REFERÊNCIA ]")

			referencia = self._controle[0][38].split('\n')
			posicao = 102

			self.cv.setFont('Helvetica', 6)

			lin = 0
			for i in referencia:
				
				_TexTo = i.decode("UTF-8")
	
				self.cv.drawString(280,posicao,_TexTo[:60])
				posicao -=7
				lin +=1
				
				if lin == 3:	break
		
		""" Rodape """
		rodape_dav = login.rdpdavs
		if "<"+self.fili.upper()+">" in rodape_dav.upper() and "</"+self.fili.upper()+">" in rodape_dav.upper():	rodape_dav = rodape_dav.split( "<"+self.fili.upper()+">" )[1].split( "</"+self.fili.upper()+">" )[0]

		linha  = 140
		if rodape_dav:
			
			for r in rodape_dav.split('\n'):

				_roda = r.decode("UTF-8")
				self.cv.drawString(25,linha,_roda)
				linha -=10
			
		""" Motivo da Devolucao """
		self.cv.setFont('Helvetica-Bold', 9)
		if self.moTdev !="":
			
			if self._controle[0][77] !=None and self._controle[0][77].strip() !="":

				lindv = 0
				for mTv in self._controle[0][77].split('\n'):
					
					if lindv > 1:	self.moTdev +=" "+mTv
					lindv +=1
					
			self.cv.drawString(20,63, "Motivo da DEVOLUÇAO: "+str( self.moTdev ) )
	
		""" Recebimento-Canhoto """
		if self._controle[0][41] == "1" and self.devolucao == '':
			
			self.cv.setFont('Helvetica', 8)
			self.cv.drawString(25,40,"RECEBEMOS DE")
			self.cv.drawString(25,30,"OS PRODUTOS E/OU SERVIÇOS CONSTANTES DO DAV INDICADA AO LADO")

			self.cv.drawString(450,50,"DATA_______________/_________________________/___________")
			self.cv.drawString(450,30,"Assinatura:________________________________________________")
	
		self.cv.setFont('Helvetica-Bold', 8)
		if self._controle[0][41] == "1" and self.devolucao == '':	self.cv.drawString(740,45, "Nº DAV" )
		if self._controle[0][41] == "2":	self.cv.drawString(740,45, "Nº ORÇAMENTO" )
		if self.devolucao == 'DEV':	self.cv.drawString(740,45, "Nº DEVOLUÇÃO" )
		self.cv.drawString(740,35, self.NumeroDav )
		
		if self._controle[0][41] == "1" and self.devolucao == '':	self.cv.drawString(95, 40, login.filialLT[ self.fili ][1] )
		if self._controle[0][41] == "2":	self.cv.drawString(740,45, "Nº ORÇAMENTO" )
		if self.devolucao == 'DEV':	self.cv.drawString(25,40,"D E V O L U Ç Ã O")
		if self._controle[0][41] == "2":	self.cv.drawString(25,40,"O R Ç A M E N T O")

class ExpedicaoDepartamentos:
	
	def expedicionarProdutos( self, dav, filial, lista_items, nome_cliente, vendedor, parent ):

		conn = sqldb()
		sql  = conn.dbc("Expedicao: Departamentos", fil = filial, janela = parent )
		
		lista_impressao = ""
		lista_impressora = {}

		if sql[0]:
			
			for i in lista_items:

				dados = i.split('|')

				if dados[3]:

					if sql[2].execute("SELECT fg_fila FROM grupofab WHERE fg_desc='"+ dados[3] +"' and fg_cdpd='G'"):
						
						fila_impressao = sql[2].fetchone()[0]

						if fila_impressao:
							
							""" Adicona as filas de impressao em dicionario, pq o dicionario ja elimina repeticao da fila pq a chave e a propria fila """
							lista_impressora[fila_impressao]  = ''
							lista_impressao +=fila_impressao +'|'+ dados[4] +'|'+ dados[2] +'|'+ dados[1] +'|'+ dados[3] +'|'+ dados[5] +'|'+ dados[6] +'|'+ dados[7] + '\n'
			
			conn.cls( sql[1] )

			"""   Relacionar impressoras e filas de impressao para validar se a fila q estar no grupo existe no cadastro  """
			relacao_filas_impressao = []

			if os.path.exists(diretorios.aTualPsT+"/srv/impressoras.cmd"):
				
				ardp = open(diretorios.aTualPsT+"/srv/impressoras.cmd","r").read()
				for i in ardp.split("\n"):
					
					if len( i.split("|") ) >=8:	relacao_filas_impressao.append( i.split("|")[2] )

			if lista_impressora:
				
				for i in lista_impressora:

					if i and i in relacao_filas_impressao:
						
						self.impressaoDepartamentos( i, lista_impressao, filial, dav, nome_cliente, vendedor )

	def impressaoDepartamentos(self, fila, lista, filial, dav, cliente, vendedor ):
		
		informe ="\n"+("-"*48)+"\n"
		for i in lista.split('\n'):
			
			if i and i.split('|')[0] == fila:
				
				p = i.split('|')
				g = i.split('|')[4]
				
				fisico = p[7].split('.')[0] if int( p[7].split('.')[1] ) == 0 else p[7]
				t1 = ( 14 - len( p[5] ) )
				t2 = ( 24 - ( len( p[6]+p[7] ) ) )
				informe += p[1] + '\n'
				informe += (" "* ( 10 - len(p[2]) ) )+p[2] +' '+ p[3] +'  '+p[5]+ (' '*t1) + p[6]+ (' '*t2) + fisico+'\n'

		datahoj = "Pedido.: "+dav +'  '+ str( datetime.datetime.now().strftime("%d/%m/%Y %T") )
		empresa = login.filialLT[ filial ][14]
		cabeca  = "Impressao de expedicao IMPRESSORA { "+ fila +" }"
		cliente = "Cliente: "+cliente
		celulas = "Descricao dos produtos\nQuantidade UN  Fabricante    Endereco      SALDO"

		informe = empresa + '\n' + cabeca + '\n\n'+ datahoj +'\n'+ cliente +'\n\n'+ celulas + informe
		informe +=("-"*48)+"\n"
		informe +="Vendedor: "+vendedor
		
		arquivo = diretorios.usPasta+login.usalogin.lower()+'_'+ fila +".txt"
		for c in range( 10 ):
			
			informe +="\n"
		
		__arquivo = open(arquivo,"w")
		__arquivo.write( informe.encode("UTF-8") )
		__arquivo.close()

		saida = commands.getstatusoutput("lpr -P'"+ fila +"' '"+arquivo+"'")

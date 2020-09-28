#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import os

from conectar import sqldb,login,dialogos,relatorios,gerenciador,formasPagamentos,truncagem,listaemails,diretorios,numeracao,menssagem
from relatorio1 import *

from reportlab.lib.pagesizes import letter,A4,landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.graphics import shapes
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import PCMYKColor, PCMYKColorSep,Color, black, blue, red, green, yellow, orange, magenta, violet, pink, brown,HexColor
from reportlab.lib.units import inch
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart

from reportlab.graphics.barcode.qr import QrCodeWidget 
from reportlab.graphics import renderPDF



#from reportlab.lib.colors import PCMYKColor
from reportlab.graphics.shapes import Drawing
#from reportlab.graphics.charts.barcharts import VerticalBarChart



from decimal import *

alertas = dialogos()
rls     = relatorios()
nF      = numeracao()
mens    = menssagem()

class modelo:
	
	def mtitulo(self,titulo,_cv,c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,Tamanho,_TipoP):

		_cv.setFont('Helvetica-Bold', Tamanho)
		if _TipoP == 1: #-: Retrato A4

			_cv.drawString(20,753,titulo)
			_cv.rect(20,760,550,15,  fill=0) #-->[ Quadro do Cabecalho]
			_cv.rect(20,20,550,730, fill=0) #-->[ Quadro Principal ]
			_cv.line(20,50,570,50)

		elif _TipoP == 2: #-: Paissagem A4

			_cv.setFillColor(HexColor('#217DD7'))
			_cv.drawString(20,528,titulo)
			_cv.setFillColor(HexColor('#000000'))

			_cv.rect(20,535,800,15,  fill=0) #-->[ Quadro do Cabecalho]
			_cv.rect(20,20,800,505, fill=0) #-->[ Quadro Principal ]
			_cv.line(20,42,820,42)

		if c1  !='':

			
			if c1.split('|')[3] !='':	_cv.setFillColor(HexColor(c1.split('|')[3]))

			if len( c1.split('|') ) == 5 and c1.split('|')[4]=="R" and c2 !="":

				if len( c1.split('|')[2].split('+') ) == 2:

					_cv.drawRightString(float(c2.split('|')[0])-4, ( float(c1.split('|')[1]) +4 ), c1.split('|')[2].split("+")[0])
					_cv.drawRightString(float(c2.split('|')[0])-4, ( float(c1.split('|')[1]) -2 ), c1.split('|')[2].split("+")[1])
					
				else:	_cv.drawRightString(float(c2.split('|')[0])-4,float(c1.split('|')[1]), c1.split('|')[2])

			else:

				if len( c1.split('|')[2].split('+') ) == 2:

					_cv.drawString(float(c1.split('|')[0]),( float(c1.split('|')[1]) +4 ), c1.split('|')[2].split("+")[0] )
					_cv.drawString(float(c1.split('|')[0]),( float(c1.split('|')[1]) -2 ), c1.split('|')[2].split("+")[1] )

				else: _cv.drawString(float(c1.split('|')[0]),float(c1.split('|')[1]), c1.split('|')[2])

			_cv.setFillColor(HexColor('#000000'))
	
			
		if c2  !='':
			if c2.split('|')[3] !='':	_cv.setFillColor(HexColor(c2.split('|')[3]))
			
			if len( c2.split('|') ) ==5 and c2.split('|')[4]=="R" and c3 !="":

				if len( c2.split('|')[2].split('+') ) == 2:

					_cv.drawRightString(float(c3.split('|')[0])-4, ( float(c2.split('|')[1]) +4 ), c2.split('|')[2].split("+")[0] )
					_cv.drawRightString(float(c3.split('|')[0])-4, ( float(c2.split('|')[1]) -2 ), c2.split('|')[2].split("+")[1] )
					
				else:	_cv.drawRightString(float(c3.split('|')[0])-4,float(c2.split('|')[1]), c2.split('|')[2])

			else:

				if len( c2.split('|')[2].split('+') ) == 2:

					_cv.drawString(float(c2.split('|')[0]),( float(c2.split('|')[1]) +4 ), c2.split('|')[2].split("+")[0] )
					_cv.drawString(float(c2.split('|')[0]),( float(c2.split('|')[1]) -2 ), c2.split('|')[2].split("+")[1] )

				else:	_cv.drawString(float(c2.split('|')[0]),float(c2.split('|')[1]), c2.split('|')[2])
			
			_cv.setFillColor(HexColor('#000000'))

		if c3  !='':

			if c3.split('|')[3] !='':	_cv.setFillColor(HexColor(c3.split('|')[3]))
			
			if len( c3.split('|') ) == 5 and c3.split('|')[4]=="R" and c4 !="":

				if len( c3.split('|')[2].split('+') ) == 2:

					_cv.drawRightString(float(c4.split('|')[0])-4, ( float(c3.split('|')[1]) +4 ), c3.split('|')[2].split("+")[0] )
					_cv.drawRightString(float(c4.split('|')[0])-4, ( float(c3.split('|')[1]) -2 ), c3.split('|')[2].split("+")[1] )
					
				else:	_cv.drawRightString(float(c4.split('|')[0])-4,float(c3.split('|')[1]), c3.split('|')[2])

			else:

				if len( c3.split('|')[2].split('+') ) == 2:

					_cv.drawString(float(c4.split('|')[0]), ( float(c3.split('|')[1]) +4 ), c3.split('|')[2].split("+")[0] )
					_cv.drawString(float(c4.split('|')[0]), ( float(c3.split('|')[1]) -2 ), c3.split('|')[2].split("+")[1] )

				else:

					if len( c3.split('|')[2].split('+') ) == 2:

						_cv.drawString(float(c3.split('|')[0]),( float(c3.split('|')[1]) +4 ), c3.split('|')[2].split("+")[0] )
						_cv.drawString(float(c3.split('|')[0]),( float(c3.split('|')[1]) -2 ), c3.split('|')[2].split("+")[1] )


					else:	_cv.drawString(float(c3.split('|')[0]),float(c3.split('|')[1]), c3.split('|')[2])
			
			_cv.setFillColor(HexColor('#000000'))

		if c4  !='':
			
			if c4.split('|')[3] !='':	_cv.setFillColor(HexColor(c4.split('|')[3]))
			
			if len( c4.split('|') ) == 5 and c4.split('|')[4]=="R" and c5 !="":

				if len( c4.split('|')[2].split('+') ) == 2:
					
					_cv.drawRightString(float(c5.split('|')[0])-4,( float(c4.split('|')[1]) +4 ), c4.split('|')[2].split("+")[0] )
					_cv.drawRightString(float(c5.split('|')[0])-4,( float(c4.split('|')[1]) -2 ), c4.split('|')[2].split("+")[1] )
				
				else:	_cv.drawRightString(float(c5.split('|')[0])-4,float(c4.split('|')[1]), c4.split('|')[2])
				
			else:

				if len( c4.split('|')[2].split('+') ) == 2:

					_cv.drawString(float(c4.split('|')[0]),( float(c4.split('|')[1]) +4 ), c4.split('|')[2].split("+")[0] )
					_cv.drawString(float(c4.split('|')[0]),( float(c4.split('|')[1]) -2 ), c4.split('|')[2].split("+")[1] )

				else:	_cv.drawString(float(c4.split('|')[0]),float(c4.split('|')[1]), c4.split('|')[2])
			
			_cv.setFillColor(HexColor('#000000'))
			
		if c5  !='':

			if c5.split('|')[3] !='':	_cv.setFillColor(HexColor(c5.split('|')[3]))
			
			if len( c5.split('|') ) == 5 and c5.split('|')[4]=="R" and c6 !="":

				if len( c5.split('|')[2].split('+') ) == 2:

					_cv.drawRightString(float(c6.split('|')[0])-4,( float(c5.split('|')[1]) +4 ), c5.split('|')[2].split("+")[0] )
					_cv.drawRightString(float(c6.split('|')[0])-4,( float(c5.split('|')[1]) -2 ), c5.split('|')[2].split("+")[1] )

				else:	_cv.drawRightString(float(c6.split('|')[0])-4,float(c5.split('|')[1]), c5.split('|')[2])

			else:

				if len( c5.split('|')[2].split('+') ) == 2:

					_cv.drawString(float(c5.split('|')[0]),( float(c5.split('|')[1]) +4 ), c5.split('|')[2].split("+")[0] )
					_cv.drawString(float(c5.split('|')[0]),( float(c5.split('|')[1]) -2 ), c5.split('|')[2].split("+")[1] )

				else:	_cv.drawString(float(c5.split('|')[0]),float(c5.split('|')[1]), c5.split('|')[2])

			_cv.setFillColor(HexColor('#000000'))
			
		if c6  !='':
			
			if c6.split('|')[3] !='':	_cv.setFillColor(HexColor(c6.split('|')[3]))
			
			if len( c6.split('|') ) == 5 and c6.split('|')[4]=="R" and c7 !="":

				if len( c6.split('|')[2].split('+') ) == 2:

					_cv.drawRightString(float(c7.split('|')[0])-4, ( float(c6.split('|')[1]) +4 ), c6.split('|')[2].split("+")[0] )
					_cv.drawRightString(float(c7.split('|')[0])-4, ( float(c6.split('|')[1]) -2 ), c6.split('|')[2].split("+")[1] )
					
				else:_cv.drawRightString(float(c7.split('|')[0])-4,float(c6.split('|')[1]), c6.split('|')[2])
				
			else:

				if len( c6.split('|')[2].split('+') ) == 2:

					_cv.drawString(float(c6.split('|')[0]),( float(c6.split('|')[1]) +4 ), c6.split('|')[2].split("+")[0] )
					_cv.drawString(float(c6.split('|')[0]),( float(c6.split('|')[1]) -2 ), c6.split('|')[2].split("+")[1] )

				else:	_cv.drawString(float(c6.split('|')[0]),float(c6.split('|')[1]), c6.split('|')[2])

			_cv.setFillColor(HexColor('#000000'))

		if c7  !='':
			
			if c7.split('|')[3] !='':	_cv.setFillColor(HexColor(c7.split('|')[3]))
			
			if len( c7.split('|') ) == 5 and c7.split('|')[4]=="R" and c8 !="":

				if len( c7.split('|')[2].split('+') ) == 2:

					_cv.drawRightString(float(c8.split('|')[0])-4, ( float(c7.split('|')[1]) +4 ),  c7.split('|')[2].split("+")[0] )
					_cv.drawRightString(float(c8.split('|')[0])-4, ( float(c7.split('|')[1]) -2 ),  c7.split('|')[2].split("+")[1] )

				else:	_cv.drawRightString(float(c8.split('|')[0])-4, float(c7.split('|')[1]),  c7.split('|')[2])
				
			else:

				if len( c7.split('|')[2].split('+') ) == 2:

					_cv.drawString(float(c7.split('|')[0]),( float(c7.split('|')[1]) +4 ), c7.split('|')[2].split("+")[0] )
					_cv.drawString(float(c7.split('|')[0]),( float(c7.split('|')[1]) -2 ), c7.split('|')[2].split("+")[1] )

				else:	_cv.drawString(float(c7.split('|')[0]), float(c7.split('|')[1]),  c7.split('|')[2])
			
			_cv.setFillColor(HexColor('#000000'))

		if c8  !='':
			
			if c8.split('|')[3] !='':	_cv.setFillColor(HexColor(c8.split('|')[3]))
			
			if len( c8.split('|') ) == 5 and c8.split('|')[4]=="R" and c9 !="":

				if len( c8.split('|')[2].split('+') ) == 2:

					_cv.drawRightString(float(c9.split('|')[0])-4, ( float(c8.split('|')[1]) + 4 ),  c8.split('|')[2].split("+")[0] )
					_cv.drawRightString(float(c9.split('|')[0])-4, ( float(c8.split('|')[1]) - 2 ),  c8.split('|')[2].split("+")[1] )

				else:	_cv.drawRightString(float(c9.split('|')[0])-4, float(c8.split('|')[1]),  c8.split('|')[2])
				
			else:

				if len( c8.split('|')[2].split('+') ) == 2:

					_cv.drawString(float(c8.split('|')[0]),( float(c8.split('|')[1]) +4 ), c8.split('|')[2].split("+")[0] )
					_cv.drawString(float(c8.split('|')[0]),( float(c8.split('|')[1]) -2 ), c8.split('|')[2].split("+")[1] )

				else:	_cv.drawString(float(c8.split('|')[0]), float(c8.split('|')[1]),  c8.split('|')[2])
			_cv.setFillColor(HexColor('#000000'))

		if c9  !='':
			
			if c9.split('|')[3] !='':	_cv.setFillColor(HexColor(c9.split('|')[3]))
			
			if len( c9.split('|') ) == 5 and c9.split('|')[4]=="R" and c10 !="":

				if len( c9.split('|')[2].split('+') ) == 2:

					_cv.drawRightString(float(c10.split('|')[0])-4, ( float(c9.split('|')[1]) + 4 ),  c9.split('|')[2].split("+")[0] )
					_cv.drawRightString(float(c10.split('|')[0])-4, ( float(c9.split('|')[1]) - 2 ),  c9.split('|')[2].split("+")[1] )
					
				else:	_cv.drawRightString(float(c10.split('|')[0])-4, float(c9.split('|')[1]),  c9.split('|')[2])

			else:

				if len( c9.split('|')[2].split('+') ) == 2:

					_cv.drawString(float(c9.split('|')[0]),( float(c9.split('|')[1]) +4 ), c9.split('|')[2].split("+")[0] )
					_cv.drawString(float(c9.split('|')[0]),( float(c9.split('|')[1]) -2 ), c9.split('|')[2].split("+")[1] )

				else:	_cv.drawString(float(c9.split('|')[0]), float(c9.split('|')[1]),  c9.split('|')[2])
			
			_cv.setFillColor(HexColor('#000000'))
			
		if c10 !='':
			
			if c10.split('|')[3] !='':	_cv.setFillColor(HexColor(c10.split('|')[3]))
			
			if len( c10.split('|') ) == 5 and c10.split('|')[4]=="R" and c11 !="":

				if len( c10.split('|')[2].split('+') ) == 2:
					
					_cv.drawRightString(float(c11.split('|')[0])-4, ( float(c10.split('|')[1]) + 4 ), c10.split('|')[2].split("+")[0] )
					_cv.drawRightString(float(c11.split('|')[0])-4, ( float(c10.split('|')[1]) - 2 ), c10.split('|')[2].split("+")[1] )
					
				else:	_cv.drawRightString(float(c11.split('|')[0])-4,float(c10.split('|')[1]),c10.split('|')[2])
				
			else:

				if len( c10.split('|')[2].split('+') ) == 2:

					_cv.drawString(float(c10.split('|')[0]),( float(c10.split('|')[1]) +4 ), c10.split('|')[2].split("+")[0] )
					_cv.drawString(float(c10.split('|')[0]),( float(c10.split('|')[1]) -2 ), c10.split('|')[2].split("+")[1] )

				else:	_cv.drawString(float(c10.split('|')[0]),float(c10.split('|')[1]),c10.split('|')[2])
			
			_cv.setFillColor(HexColor('#000000'))
			
		if c11 !='':
			
			if c11.split('|')[3] !='':	_cv.setFillColor(HexColor(c11.split('|')[3]))
			
			if len( c11.split('|') ) == 5 and c11.split('|')[4]=="R" and c12 !="":

				if len( c11.split('|')[2].split('+') ) == 2:

					_cv.drawRightString(float(c12.split('|')[0])-4, ( float(c11.split('|')[1]) + 4 ),c11.split('|')[2].split("+")[0] )
					_cv.drawRightString(float(c12.split('|')[0])-4, ( float(c11.split('|')[1]) - 2 ),c11.split('|')[2].split("+")[1] )

				else:	_cv.drawRightString(float(c12.split('|')[0])-4,float(c11.split('|')[1]),c11.split('|')[2])
				
			else:

				if len( c11.split('|')[2].split('+') ) == 2:

					_cv.drawString(float(c11.split('|')[0]),( float(c11.split('|')[1]) +4 ), c11.split('|')[2].split("+")[0] )
					_cv.drawString(float(c11.split('|')[0]),( float(c11.split('|')[1]) -2 ), c11.split('|')[2].split("+")[1] )

				else:	_cv.drawString(float(c11.split('|')[0]),float(c11.split('|')[1]),c11.split('|')[2])
			
			_cv.setFillColor(HexColor('#000000'))
			
		if c12 !='':
			
			if c12.split('|')[3] !='':	_cv.setFillColor(HexColor(c12.split('|')[3]))

			if len( c12.split('|')[2].split('+') ) == 2:

				_cv.drawString(float(c12.split('|')[0]),( float(c12.split('|')[1]) +4 ), c12.split('|')[2].split("+")[0] )
				_cv.drawString(float(c12.split('|')[0]),( float(c12.split('|')[1]) -2 ), c12.split('|')[2].split("+")[1] )

			else:	_cv.drawString(float(c12.split('|')[0]),float(c12.split('|')[1]),c12.split('|')[2])
			_cv.setFillColor(HexColor('#000000'))

	def separa(self,_cv,s1,s2,s3,s4,s5,s6):
		
		if s1 !='':	_cv.line(float(s1.split('|')[0]), float(s1.split('|')[1]),float(s1.split('|')[2]), float(s1.split('|')[3]))
		if s2 !='':	_cv.line(float(s2.split('|')[0]), float(s2.split('|')[1]),float(s2.split('|')[2]), float(s2.split('|')[3]))
		if s3 !='':	_cv.line(float(s3.split('|')[0]), float(s3.split('|')[1]),float(s3.split('|')[2]), float(s3.split('|')[3]))
		if s4 !='':	_cv.line(float(s4.split('|')[0]), float(s4.split('|')[1]),float(s4.split('|')[2]), float(s4.split('|')[3]))
		if s5 !='':	_cv.line(float(s5.split('|')[0]), float(s5.split('|')[1]),float(s5.split('|')[2]), float(s5.split('|')[3]))
		if s6 !='':	_cv.line(float(s6.split('|')[0]), float(s6.split('|')[1]),float(s6.split('|')[2]), float(s6.split('|')[3]))
			
	def mcab(self,_cv,t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,lnh,lsn,Tipo,esTC):

		_cv.setFont('Helvetica', 6)
		if Tipo == '1':	_cv.setFillColor(blue) #---: Primeiro dia do periodo e/ou dia atual
		if Tipo == '2':	_cv.setFillColor(orange) #-: Dia anterior
		if Tipo == '3':	_cv.setFillColor(green)
		
		#-----: PgTo do credito, Devolucao em dinheiro
		if Tipo == '4' or Tipo == '5':	_cv.setFillColor(violet) 
		
		if esTC == '2':	_cv.setFillColor(orange)
		if esTC == '3':	_cv.setFillColor(red)

		if t1  != '' and t1.split('|')[0].upper() == 'C':	_cv.drawString(float(t1.split('|')[1]),float(t1.split('|')[2]), str(t1.split('|')[3]))
		if t1  != '' and t1.split('|')[0].upper() == 'V':	_cv.drawRightString(float(t1.split('|')[1]),float(t1.split('|')[2]), str(t1.split('|')[3]))

		if t2  != '' and t2.split('|')[0].upper() == 'C':	_cv.drawString(float(t2.split('|')[1]),float(t2.split('|')[2]), str(t2.split('|')[3]))
		if t2  != '' and t2.split('|')[0].upper() == 'V':	_cv.drawRightString(float(t2.split('|')[1]),float(t2.split('|')[2]), str(t2.split('|')[3]))

		if t3  != '' and t3.split('|')[0].upper() == 'C':	_cv.drawString(float(t3.split('|')[1]),float(t3.split('|')[2]), str(t3.split('|')[3]))
		if t3  != '' and t3.split('|')[0].upper() == 'V':	_cv.drawRightString(float(t3.split('|')[1]),float(t3.split('|')[2]), str(t3.split('|')[3]))

		if t4  != '' and t4.split('|')[0].upper() == 'C':	_cv.drawString(float(t4.split('|')[1]),float(t4.split('|')[2]), str(t4.split('|')[3]))
		if t4  != '' and t4.split('|')[0].upper() == 'V':	_cv.drawRightString(float(t4.split('|')[1]),float(t4.split('|')[2]), str(t4.split('|')[3]))

		if t5  != '' and t5.split('|')[0].upper() == 'C':	_cv.drawString(float(t5.split('|')[1]),float(t5.split('|')[2]), str(t5.split('|')[3]))
		if t5  != '' and t5.split('|')[0].upper() == 'V':	_cv.drawRightString(float(t5.split('|')[1]),float(t5.split('|')[2]), str(t5.split('|')[3]))

		if t6  != '' and t6.split('|')[0].upper() == 'C':	_cv.drawString(float(t6.split('|')[1]),float(t6.split('|')[2]), str(t6.split('|')[3]))
		if t6  != '' and t6.split('|')[0].upper() == 'V':	_cv.drawRightString(float(t6.split('|')[1]),float(t6.split('|')[2]), str(t6.split('|')[3]))

		if t7  != '' and t7.split('|')[0].upper() == 'C':	_cv.drawString(float(t7.split('|')[1]),float(t7.split('|')[2]), str(t7.split('|')[3]))
		if t7  != '' and t7.split('|')[0].upper() == 'V':	_cv.drawRightString(float(t7.split('|')[1]),float(t7.split('|')[2]), str(t7.split('|')[3]))

		if t8  != '' and t8.split('|')[0].upper() == 'C':	_cv.drawString(float(t8.split('|')[1]),float(t8.split('|')[2]), str(t8.split('|')[3]))
		if t8  != '' and t8.split('|')[0].upper() == 'V':	_cv.drawRightString(float(t8.split('|')[1]),float(t8.split('|')[2]), str(t8.split('|')[3]))

		if t9  != '' and t9.split('|')[0].upper() == 'C':	_cv.drawString(float(t9.split('|')[1]),float(t9.split('|')[2]), str(t9.split('|')[3]))
		if t9  != '' and t9.split('|')[0].upper() == 'V':	_cv.drawRightString(float(t9.split('|')[1]),float(t9.split('|')[2]), str(t9.split('|')[3]))

		if t10 != '' and t10.split('|')[0].upper() == 'C':	_cv.drawString(float(t10.split('|')[1]),float(t10.split('|')[2]), str(t10.split('|')[3]))
		if t10 != '' and t10.split('|')[0].upper() == 'V':	_cv.drawRightString(float(t10.split('|')[1]),float(t10.split('|')[2]), str(t10.split('|')[3]))

		if t11 != '' and t11.split('|')[0].upper() == 'C':	_cv.drawString(float(t11.split('|')[1]),float(t11.split('|')[2]), str(t11.split('|')[3]))
		if t11 != '' and t11.split('|')[0].upper() == 'V':	_cv.drawRightString(float(t11.split('|')[1]),float(t11.split('|')[2]), str(t11.split('|')[3]))

		if t12 != '' and t12.split('|')[0].upper() == 'C':	_cv.drawString(float(t12.split('|')[1]),float(t12.split('|')[2]), str(t12.split('|')[3]))
		if t12 != '' and t12.split('|')[0].upper() == 'V':	_cv.drawRightString(float(t12.split('|')[1]),float(t12.split('|')[2]), str(t12.split('|')[3]))

		_cv.setFillColor(black)		

		if lsn == True:	_cv.line(20,lnh,570,lnh)

	def rodape(self,_cv,r1,r2,r3,r4,r5,r6,r7,r8,r9,Tamanho):

		_cv.setFont('Helvetica', Tamanho)
		if r1  !='':
			
			if len( r1.split('|')[3].split("%") ) == 2:

				_cv.drawString(float(r1.split('|')[0]),float(r1.split('|')[1]), r1.split('|')[3].split("%")[0])
				_cv.drawString(float(r1.split('|')[0]),float(r1.split('|')[1])-7, r1.split('|')[3].split("%")[1])

			else:	_cv.drawString(float(r1.split('|')[0]),float(r1.split('|')[1]), r1.split('|')[3])

			if r1.split('|')[4] !='':	_cv.drawRightString(float(r1.split('|')[2]),float(r1.split('|')[1]), r1.split('|')[4])

		if r2  !='':
	
			_cv.drawString(float(r2.split('|')[0]),float(r2.split('|')[1]), r2.split('|')[3])
			if r2.split('|')[4] !='':	_cv.drawRightString(float(r2.split('|')[2]),float(r2.split('|')[1]), r2.split('|')[4])

		if r3  !='':
	
			_cv.drawString(float(r3.split('|')[0]),float(r3.split('|')[1]), r3.split('|')[3])
			if r3.split('|')[4] !='':	_cv.drawRightString(float(r3.split('|')[2]),float(r3.split('|')[1]), r3.split('|')[4])
		
		if r4  !='':
	
			_cv.drawString(float(r4.split('|')[0]),float(r4.split('|')[1]), r4.split('|')[3])
			if r4.split('|')[4] !='':	_cv.drawRightString(float(r4.split('|')[2]),float(r4.split('|')[1]), r4.split('|')[4])

class vendas:
	
	
	def psv(self,dI,dF,vd,cx,separ,lnhsn,par,Trl, rFiliais = False, Filial = "", cancelado = "F" ):

		def cabvendas(separa):
			

			""" Cabecalho """
			pag = str(pg).zfill(3)+' ['+str(nPg).zfill(3)+']'
			rls.cabecalhopadrao( cv, ImageReader, dh, pag, Filial, "Posição de Vendas",2)
		
			""" Titulo de Cabecalho """
			cb1= cb2= cb3= cb4= cb5= cb6= cb7= cb8= cb9= cb10= cb11= cb12='' 
			rel =  "Posição de Vendas: "+str(cIni)+' A '+str(cFim)+' '+str( Filial )+'  '+str(relTipo)

			if pg == 1:

				cb1 =  "22|765|"+rel+"|"
				mdl.mtitulo("R e s u m o",cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12,7,2)

			else:

				cb1 =  "22|540|QTD|"
				cb2 =  "42|540|Nº DAV|"
				cb3 = "110|540|Emissão|"
				cb4 = "260|540|Total DAV|"
				cb5 = "320|540|Recebimento|"
				cb6 = "510|540|Valor Recebido|"
				cb7 = "570|540|C L I E N T E|"
				if separa == False:	mdl.mtitulo(rel,cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12,8,2)
				else:
					cv.line((float(cb2.split('|')[0])-2), float(ccampo), (float(cb2.split('|')[0])-2), float((lcampo+8)) )
					cv.line((float(cb3.split('|')[0])-2), float(ccampo), (float(cb3.split('|')[0])-2), float((lcampo+8)) )

					cv.line((float(cb4.split('|')[0])-2), float(ccampo), (float(cb4.split('|')[0])-2), float((lcampo+8)) )
					cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float((lcampo+8)) )
					cv.line((float(cb6.split('|')[0])-2), float(ccampo), (float(cb6.split('|')[0])-2), float((lcampo+8)) )
					cv.line((float(cb7.split('|')[0])-2), float(ccampo), (float(cb7.split('|')[0])-2), float((lcampo+8)) )
					
		""" Emissao do Relatorio [ Relatorio por Caixa e/ou Vendedor ]"""
		vdcx = cd = ''
		if vd != '':	vdcx = "V"
		if cx != '':	vdcx = "C"

		conn = sqldb()
		sql  = conn.dbc("Relatórios: Posição de Vendas", fil = Filial, janela = par )
		mdl  = modelo()
		T    = truncagem()
		
		vend = vd.split('-')
		caix = cx.split('-')
		if vd !='':	vd = vend[1] #-: Login  do usuario
		if vd !='':	cd = vend[0] #-: Codigo do usuario
		if cx !='':	vd = caix[1]
		vReTorno = 0

		_mensagem = mens.showmsg("Montando relatorio de vendas!!\n\nAguarde...")
		if sql[0]:

			Inicial = datetime.datetime.strptime(dI.FormatDate(),'%d-%m-%Y').date()

			dIni = datetime.datetime.strptime(dI.FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			dFim = datetime.datetime.strptime(dF.FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			hoje = format(datetime.datetime.now(),'%Y/%m/%d')

			cIni = datetime.datetime.strptime(dI.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			cFim = datetime.datetime.strptime(dF.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			dh   = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
			
			pg   = 1
			
			#--> Se Datas Iniciais e Finais forem iguais iguala ao dia para pegar recebimentos feito no dia com DAV de dias anteriores
			if dIni == dFim:	hoje = dIni
			
			if vdcx == '': #--> Relatorio Geral

				condicao = "SELECT * FROM cdavs   WHERE cr_edav   >='"+dIni+"' and cr_edav   <='"+dFim+"' and cr_tfat!='2'"
				anterior = "SELECT * FROM cdavs   WHERE cr_erec   >='"+dIni+"' and cr_erec   <='"+dFim+"' and cr_edav < '"+hoje+"' and cr_tfat!='2'"
				creceber = "SELECT * FROM receber WHERE rc_dtlanc >='"+dIni+"' and rc_dtlanc <='"+dFim+"'"
				devoluca = "SELECT * FROM dcdavs  WHERE cr_erec   >='"+dIni+"' and cr_erec   <='"+dFim+"' and cr_tfat!='2'"
				creditoc = "SELECT * FROM conta   WHERE cc_lancam >='"+dIni+"' and cc_lancam <='"+dFim+"' and cc_origem='PC'"
				sangrias = "SELECT * FROM sansu   WHERE ss_lancam >='"+dIni+"' and ss_lancam <='"+dFim+"'"
				
				relTipo  = "[ Relatorio Geral ]"

				if rFiliais:	condicao = condicao.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")
				if rFiliais:	anterior = anterior.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")
				if rFiliais:	creceber = creceber.replace("WHERE","WHERE rc_indefi='"+str( Filial )+"' and ")
				if rFiliais:	devoluca = devoluca.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")
				if rFiliais:	sangrias = sangrias.replace("WHERE","WHERE ss_idfila='"+str( Filial )+"' and ")
				if rFiliais:	creditoc = creditoc.replace("WHERE","WHERE cc_idfila='"+str( Filial )+"' and")

				"""   Totalizar no caixa apenas recebimentos feitos no caixa   """
				if len( login.filialLT[ Filial ][35].split(";") ) >=44 and login.filialLT[ Filial ][35].split(";")[43] == "T":
					
					creceber = creceber.replace("WHERE","WHERE rc_modulo='CAIXA' and")
					
				if cancelado == "T":	condicao = condicao.replace("WHERE","WHERE cr_reca!='3' and ")
				if cancelado == "T":	anterior = anterior.replace("WHERE","WHERE cr_reca!='3' and ")

			if   vdcx == "C": #--> Relatorio por caixa

				condicao = "SELECT * FROM cdavs   WHERE cr_edav   >='"+dIni+"' and cr_edav   <='"+dFim+"' and cr_urec  = '"+vd+"' and cr_tfat!='2'"
				anterior = "SELECT * FROM cdavs   WHERE cr_erec   >='"+dIni+"' and cr_erec   <='"+dFim+"' and cr_edav  < '"+hoje+"' and cr_urec = '"+vd+"' and cr_tfat!='2'"
				creceber = "SELECT * FROM receber WHERE rc_dtlanc >='"+dIni+"' and rc_dtlanc <='"+dFim+"' and rc_loginc = '"+vd+"'"
				devoluca = "SELECT * FROM dcdavs  WHERE cr_erec   >='"+dIni+"' and cr_erec   <='"+dFim+"' and cr_urec   = '"+vd+"' and cr_tfat!='2'"
				creditoc = "SELECT * FROM conta   WHERE cc_lancam >='"+dIni+"' and cc_lancam <='"+dFim+"' and cc_origem ='PC' and cc_usnome='"+vd+"'"
				sangrias = "SELECT * FROM sansu   WHERE ss_lancam >='"+dIni+"' and ss_lancam <='"+dFim+"' and ss_usnome ='"+vd+"'"

				"""   Totalizar no caixa apenas recebimentos feitos no caixa   """
				if len( login.filialLT[ Filial ][35].split(";") ) >=44 and login.filialLT[ Filial ][35].split(";")[43] == "T":
					
					creceber = creceber.replace("WHERE","WHERE rc_modulo='CAIXA' and")


				relTipo  = "[ Relatorio por caixa: %s ]" %(vd)

				if rFiliais:	condicao = condicao.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")
				if rFiliais:	anterior = anterior.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")
				if rFiliais:	creceber = creceber.replace("WHERE","WHERE rc_indefi='"+str( Filial )+"' and ")
				if rFiliais:	devoluca = devoluca.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")
				if rFiliais:	sangrias = sangrias.replace("WHERE","WHERE ss_idfila='"+str( Filial )+"' and ")

				if cancelado == "T":	condicao = condicao.replace("WHERE","WHERE cr_reca!='3' and ")
				if cancelado == "T":	anterior = anterior.replace("WHERE","WHERE cr_reca!='3' and ")

			elif vdcx == "V": #--> Relatorio por Vendedor

				condicao = "SELECT * FROM cdavs  WHERE cr_edav >='"+dIni+"' and cr_edav <='"+dFim+"' and cr_vdcd = '"+cd+"' and cr_tfat!='2'"
				anterior = "SELECT * FROM cdavs  WHERE cr_erec >='"+dIni+"' and cr_erec <='"+dFim+"' and cr_edav < '"+hoje+"' and cr_vdcd = '"+cd+"' and cr_tfat!='2'"
 				devoluca = "SELECT * FROM dcdavs WHERE cr_erec >='"+dIni+"' and cr_erec <='"+dFim+"' and cr_vdcd = '"+cd+"' and cr_tfat!='2'"

				relTipo  = "[ Relatorio por vendedor: %s ]" %(vd)

				if rFiliais == True:	condicao = condicao.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")
				if rFiliais == True:	anterior = anterior.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")
				if rFiliais == True:	devoluca = devoluca.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")

				if cancelado == "T":	condicao = condicao.replace("WHERE","WHERE cr_reca!='3' and ")
				if cancelado == "T":	anterior = anterior.replace("WHERE","WHERE cr_reca!='3' and ")

				
			AntReto = rcbReto = CreReto = 0

			_mensagem = mens.showmsg("Montando relatorio { Adiconando dados de vendas }!!\n\nAguarde...")
			vReTorno = sql[2].execute( condicao )
			rvendas  = sql[2].fetchall()

			#---:[ Adicionando dados de vendas ]
			rl = {}
			rg = 0
			
			if vReTorno !=0:

				for i in rvendas:
					rl[rg] = i[2],i[4],i[10],i[11],i[12],i[13],i[14],i[37],i[44],i[48],i[74],"1","0.00"
					rg +=1

			#---:[ Adicionando dados de recebimentos de dias anteriores ]
			_mensagem = mens.showmsg("Montando relatorio { Adiconando dados de vendas de dias anteriores }!!\n\nAguarde...")
			if hoje == dIni:
				
				AntReto = sql[2].execute(anterior)
				AntVend = sql[2].fetchall()

				if AntReto !=0:

					for i in AntVend:
						rl[rg] = i[2],i[4],i[10],i[11],i[12],i[13],i[14],i[37],i[44],i[48],i[74],"2","0.00"
						rg +=1
			
					vReTorno +=AntReto


			#---:[ Adicionando dados de recebimentos de devolucao ]
			_mensagem = mens.showmsg("Montando relatorio { Adiconando dados de recebimento de devoluções }!!\n\nAguarde...")
			if hoje == dIni:
				
				DevReto = sql[2].execute(devoluca)
				DevVend = sql[2].fetchall()

				if DevReto !=0:

					for i in DevVend:

						rl[rg] = i[2],i[4],i[10],i[11],i[12],i[13],i[14],i[37],i[44],i[48],i[74],"4",i[53]
						rg +=1
			
					vReTorno +=DevReto

			#---:[ Adicionando dados de pagamento de credito ]
			_mensagem = mens.showmsg("Montando relatorio { Adiconando dados de pagamentos de credito }!!\n\nAguarde...")
			if hoje == dIni and vdcx !='V':
				
				CreReto = sql[2].execute(creditoc)
				CreVend = sql[2].fetchall()

				if CreReto !=0:

					for i in CreVend:

						rl[rg] = "PgTo Crédito",i[9],i[4],i[1],i[2],i[1],i[2],i[15],i[4],i[15],'1',"5",'0.00'
						rg +=1
			
					vReTorno +=CreReto

			
			#---: Adicionando dados de contas recebidas [ Contas ARECEBER ]
			"""  Não Incluir o contas areceber em relatorio de vendas  """
			_mensagem = mens.showmsg("Montando relatorio { Adiconando dados de contas areceber }!!\n\nAguarde...")
			_rc = False
			if len( login.filialLT[ Filial ][35].split(";") ) >=32 and login.filialLT[ Filial ][35].split(";")[31] == "T":	_rc = True
			
			if hoje == dIni and vdcx != "V" and _rc == False:

				rcbReto = sql[2].execute(creceber)
				rcbBaix = sql[2].fetchall()

				if rcbReto !=0:
					
					for i in rcbBaix:

						_fb = "[RC] "
						if i[55] !='':	_fb = "[CX] "
						if i[35] == "1":	rl[rg] = i[1],_fb+i[12],i[17],i[7],i[8],i[19],i[20],i[18],i[56],i[5],'',"3","0.00"
						if i[35] == "" and i[2] == "R":	rl[rg] = i[1],_fb+i[12],i[17],i[7],i[8],i[19],i[20],i[18],i[56],i[5],'',"8","0.00"
						
						""" Adiciona a Lista as Entradas Manuais """
						if i[35] == "" and i[2] == "A":	rl[rg] = i[1],'[RA]'+i[12],i[17],i[7],i[8],i[19],i[20],i[18],i[56],i[5],'',"8","0.00"
						rg +=1
			
					vReTorno +=rcbReto

			#---:[ Adicionando dados de contas recebidas ]
			_mensagem = mens.showmsg("Montando relatorio { Adiconando dados de contas recebidas }!!\n\nAguarde...")

			saDin = saCha = saChp = saCcr = saCdb = sasup = Decimal('0.00')
			seDin = seCha = seChp = seCcr = seCdb = Decimal('0.00')
			if vdcx == '' or vdcx == 'C':

				sanReto = sql[2].execute(sangrias)
				sanBaix = sql[2].fetchall()

				if sanReto !=0:
						
					for i in sanBaix:
						
						if i[11] == 'S':
							
							saDin += Decimal(i[6])
							saCha += Decimal(i[7])
							saChp += Decimal(i[8])
							saCcr += Decimal(i[9])
							saCdb += Decimal(i[10])

							
						if i[11] == 'E':

							seDin += Decimal(i[6])
							seCha += Decimal(i[7])
							seChp += Decimal(i[8])
							seCcr += Decimal(i[9])
							seCdb += Decimal(i[10])
						
						if i[11] == 'C':	sasup += Decimal(i[6])
						rg +=1
				
					vReTorno +=sanReto

			""" Totalizacao """
			"""
				Total Vendas,DAVS,Recebimento,RateioTroco,Transferencia CC,Abertos
				Cancelados,Pagamento cc,Estorno
			"""

			vTven= vTdav= vTrec= vTroc= vTran = Decimal('0.00')
			vTabe= vTcan= vTpcc= vTest= vTrcl = vTdes = Decimal('0.00')

			TTdav = TTrec = TTroc= TTran= TTpcc = Decimal('0.00')
			vAdav = vArec = vAroc= vAran= vApcc = Decimal('0.00')
			vRdav = vRrec = vRroc= vRran= vRpcc = Decimal('0.00')
			TTdes = Decimal('0.00')

			"""
				Total Dinheiro,Ch.Avista,Ch.Pre,CartaoCredito,CartaoDebito
				Faturado-Boleto,Faturado-Carteira,Financeira,Tickete,PGTO Credito, DEP.Conta
			"""

			Tdinh= Tchav= Tchpr= Tccre= Tcdeb= Tfabo= Tfaca= Tfina= TTick= Tpgcr= Tdepo= Trclo = Decimal('0.00')
			Adinh= Achav= Achpr= Accre= Acdeb= Afabo= Afaca= Afina= ATick= Apgcr= Adepo= Arclo = Decimal('0.00')
			Rdinh= Rchav= Rchpr= Rccre= Rcdeb= Rfabo= Rfaca= Rfina= RTick= Rpgcr= Rdepo= Decimal('0.00')
			TDevd= TCont= TDCvd= CusVd= CusDv= TTdev= Adesc= Decimal('0.00')

			""" Contas Arecebe """
			if rcbReto != 0:
				
				for rc in rcbBaix:

					if rc[35] == "1":
						
						if rc[21][:2] == "01":	Rdinh += rc[05]
						if rc[21][:2] == "02":	Rchav += rc[05]
						if rc[21][:2] == "03":	Rchpr += rc[05]
						if rc[21][:2] == "04":	Rccre += rc[05]
						if rc[21][:2] == "05":	Rcdeb += rc[05]

						if rc[21][:2] == "08":	Rfina += rc[05]
						if rc[21][:2] == "09":	RTick += rc[05]
						if rc[21][:2] == "10":	Rpgcr += rc[05]
						if rc[21][:2] == "11":	Rdepo += rc[05]

						""" Troco, Transferencia CC """
						if rc[41] != 0:	vRroc += rc[41]
						if rc[42] != 0:	vRran += rc[42]
						
						""" Totalizando Recebimento """
						vRdav += ( rc[05] - rc[41] - rc[42] )
						vRrec += rc[05]

					if rc[35] == "":
						
						if rc[2] == "R" or rc[2] == "A":

							if rc[6][:2] == "01":	Rdinh += rc[05]
							if rc[6][:2] == "02":	Rchav += rc[05]
							if rc[6][:2] == "03":	Rchpr += rc[05]
							if rc[6][:2] == "04":	Rccre += rc[05]
							if rc[6][:2] == "05":	Rcdeb += rc[05]
								  
							if rc[6][:2] == "08":	Rfina += rc[05]
							if rc[6][:2] == "09":	RTick += rc[05]
							if rc[6][:2] == "10":	Rpgcr += rc[05]
							if rc[6][:2] == "11":	Rdepo += rc[05]

							""" Troco, Transferencia CC """
							if rc[41] != 0:	vRroc += rc[41]
							if rc[42] != 0:	vRran += rc[42]
							
							""" Totalizando Recebimento """
							vRdav += ( rc[05] - rc[41] - rc[42] )
							vRrec += rc[05]

			if vdcx == '': #->Geral

				if dIni == dFim:

					condicao = "SELECT  SUM(cr_tnot), SUM(cr_vlrc), SUM(cr_tror), SUM(cr_ccre), SUM(cr_cdeb),\
										SUM(cr_dinh), SUM(cr_chav), SUM(cr_chpr), SUM(cr_ctcr), SUM(cr_ctde),\
										SUM(cr_fatb), SUM(cr_fatc), SUM(cr_fina), SUM(cr_tike), SUM(cr_pgcr),\
										SUM(cr_depc), SUM(cr_rcbl), SUM(cr_cust), SUM(cr_vdes) FROM cdavs WHERE cr_edav >='"+dIni+"' and cr_edav <='"+dFim+"' and cr_edav=cr_erec and cr_reca='1' and cr_tfat!='2'"
					
					if rFiliais == True:	condicao = condicao.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")

				else:

					condicao = "SELECT  SUM(cr_tnot), SUM(cr_vlrc), SUM(cr_tror), SUM(cr_ccre), SUM(cr_cdeb),\
										SUM(cr_dinh), SUM(cr_chav), SUM(cr_chpr), SUM(cr_ctcr), SUM(cr_ctde),\
										SUM(cr_fatb), SUM(cr_fatc), SUM(cr_fina), SUM(cr_tike), SUM(cr_pgcr),\
										SUM(cr_depc), SUM(cr_rcbl), SUM(cr_cust), SUM(cr_vdes) FROM cdavs WHERE cr_edav >='"+dIni+"' and cr_edav <='"+dFim+"' and cr_reca='1' and cr_tfat!='2'"

					if rFiliais == True:	condicao = condicao.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")
					
					
				anterior = "SELECT  SUM(cr_tnot), SUM(cr_vlrc), SUM(cr_tror), SUM(cr_ccre), SUM(cr_cdeb),\
									SUM(cr_dinh), SUM(cr_chav), SUM(cr_chpr), SUM(cr_ctcr), SUM(cr_ctde),\
									SUM(cr_fatb), SUM(cr_fatc), SUM(cr_fina), SUM(cr_tike), SUM(cr_pgcr),\
									SUM(cr_depc), SUM(cr_rcbl), SUM(cr_vdes) FROM cdavs WHERE cr_erec >='"+dIni+"' and cr_erec <='"+dFim+"' and cr_edav < '"+hoje+"' and cr_reca='1' and cr_tfat!='2'"

				devoluca = "SELECT  SUM(cr_tnot), SUM(cr_vlrc), SUM(cr_tror), SUM(cr_ccre), SUM(cr_cdeb),\
									SUM(cr_dinh), SUM(cr_chav), SUM(cr_chpr), SUM(cr_ctcr), SUM(cr_ctde),\
									SUM(cr_fatb), SUM(cr_fatc), SUM(cr_fina), SUM(cr_tike), SUM(cr_pgcr),\
									SUM(cr_depc), SUM(cr_rcbl) FROM dcdavs WHERE cr_erec >='"+dIni+"' and cr_erec <='"+dFim+"' and cr_reca='1' and cr_tfat!='2'"

				contacor = "SELECT  SUM(cc_debito) FROM conta WHERE cc_lancam >='"+dIni+"' and cc_lancam <='"+dFim+"' and cc_origem='PC'"

				if rFiliais:	anterior = anterior.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and")
				if rFiliais:	devoluca = devoluca.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and")
				if rFiliais:	contacor = contacor.replace("WHERE","WHERE cc_idfila='"+str( Filial )+"' and")

				
			elif vdcx == 'C': #->Por Caixa

				if dIni == dFim:

					condicao = "SELECT  SUM(cr_tnot), SUM(cr_vlrc), SUM(cr_tror), SUM(cr_ccre), SUM(cr_cdeb),\
										SUM(cr_dinh), SUM(cr_chav), SUM(cr_chpr), SUM(cr_ctcr), SUM(cr_ctde),\
										SUM(cr_fatb), SUM(cr_fatc), SUM(cr_fina), SUM(cr_tike), SUM(cr_pgcr),\
										SUM(cr_depc), SUM(cr_rcbl), SUM(cr_cust), SUM(cr_vdes) FROM cdavs WHERE cr_edav >='"+dIni+"' and cr_edav <='"+dFim+"' and cr_edav=cr_erec and cr_reca='1' and cr_urec='"+vd+"' and cr_tfat!='2'"

					if rFiliais == True:	condicao = condicao.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")

				else:

					condicao = "SELECT  SUM(cr_tnot), SUM(cr_vlrc), SUM(cr_tror), SUM(cr_ccre), SUM(cr_cdeb),\
										SUM(cr_dinh), SUM(cr_chav), SUM(cr_chpr), SUM(cr_ctcr), SUM(cr_ctde),\
										SUM(cr_fatb), SUM(cr_fatc), SUM(cr_fina), SUM(cr_tike), SUM(cr_pgcr),\
										SUM(cr_depc), SUM(cr_rcbl), SUM(cr_cust), SUM(cr_vdes) FROM cdavs WHERE cr_edav >='"+dIni+"' and cr_edav <='"+dFim+"' and cr_reca='1' and cr_urec='"+vd+"' and cr_tfat!='2'"

					if rFiliais == True:	condicao = condicao.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")
					

				anterior = "SELECT  SUM(cr_tnot), SUM(cr_vlrc), SUM(cr_tror), SUM(cr_ccre), SUM(cr_cdeb),\
									SUM(cr_dinh), SUM(cr_chav), SUM(cr_chpr), SUM(cr_ctcr), SUM(cr_ctde),\
									SUM(cr_fatb), SUM(cr_fatc), SUM(cr_fina), SUM(cr_tike), SUM(cr_pgcr),\
									SUM(cr_depc), SUM(cr_rcbl), SUM(cr_vdes) FROM cdavs WHERE cr_erec >='"+dIni+"' and cr_erec <='"+dFim+"' and cr_edav < '"+hoje+"' and cr_reca='1' and cr_urec='"+vd+"' and cr_tfat!='2'"

				devoluca = "SELECT  SUM(cr_tnot), SUM(cr_vlrc), SUM(cr_tror), SUM(cr_ccre), SUM(cr_cdeb),\
									SUM(cr_dinh), SUM(cr_chav), SUM(cr_chpr), SUM(cr_ctcr), SUM(cr_ctde),\
									SUM(cr_fatb), SUM(cr_fatc), SUM(cr_fina), SUM(cr_tike), SUM(cr_pgcr),\
									SUM(cr_depc),SUM(cr_rcbl) FROM dcdavs WHERE cr_erec >='"+dIni+"' and cr_erec <='"+dFim+"' and cr_reca='1' and cr_urec='"+vd+"' and cr_tfat!='2'"

				contacor = "SELECT  SUM(cc_debito) FROM conta WHERE cc_lancam >='"+dIni+"' and cc_lancam <='"+dFim+"' and cc_origem='PC' and cc_usnome='"+vd+"'"

				if rFiliais == True:	anterior = anterior.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")
				if rFiliais == True:	devoluca = devoluca.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")


			elif vdcx == 'V': #->Por Vendedor
				
				if dIni == dFim:

					condicao = "SELECT  SUM(cr_tnot), SUM(cr_vlrc), SUM(cr_tror), SUM(cr_ccre), SUM(cr_cdeb),\
										SUM(cr_dinh), SUM(cr_chav), SUM(cr_chpr), SUM(cr_ctcr), SUM(cr_ctde),\
										SUM(cr_fatb), SUM(cr_fatc), SUM(cr_fina), SUM(cr_tike), SUM(cr_pgcr),\
										SUM(cr_depc), SUM(cr_rcbl), SUM(cr_cust), SUM(cr_vdes) FROM cdavs WHERE cr_edav >='"+dIni+"' and cr_edav <='"+dFim+"' and cr_edav=cr_erec and cr_reca='1' and cr_vdcd='"+cd+"' and cr_tfat!='2'"

					if rFiliais == True:	condicao = condicao.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")

				else:

					condicao = "SELECT  SUM(cr_tnot), SUM(cr_vlrc), SUM(cr_tror), SUM(cr_ccre), SUM(cr_cdeb),\
										SUM(cr_dinh), SUM(cr_chav), SUM(cr_chpr), SUM(cr_ctcr), SUM(cr_ctde),\
										SUM(cr_fatb), SUM(cr_fatc), SUM(cr_fina), SUM(cr_tike), SUM(cr_pgcr),\
										SUM(cr_depc), SUM(cr_rcbl), SUM(cr_cust), SUM(cr_vdes) FROM cdavs WHERE cr_edav >='"+dIni+"' and cr_edav <='"+dFim+"' and cr_reca='1' and cr_vdcd='"+cd+"' and cr_tfat!='2'"

					if rFiliais == True:	condicao = condicao.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")

				anterior = "SELECT  SUM(cr_tnot), SUM(cr_vlrc), SUM(cr_tror), SUM(cr_ccre), SUM(cr_cdeb),\
									SUM(cr_dinh), SUM(cr_chav), SUM(cr_chpr), SUM(cr_ctcr), SUM(cr_ctde),\
									SUM(cr_fatb), SUM(cr_fatc), SUM(cr_fina), SUM(cr_tike), SUM(cr_pgcr),\
									SUM(cr_depc), SUM(cr_rcbl), SUM(cr_vdes) FROM cdavs WHERE cr_erec >='"+dIni+"' and cr_erec <='"+dFim+"' and cr_edav < '"+hoje+"' and cr_reca='1' and cr_vdcd='"+cd+"' and cr_tfat!='2'"

				devoluca = "SELECT  SUM(cr_tnot), SUM(cr_vlrc), SUM(cr_tror), SUM(cr_ccre), SUM(cr_cdeb),\
									SUM(cr_dinh), SUM(cr_chav), SUM(cr_chpr), SUM(cr_ctcr), SUM(cr_ctde),\
									SUM(cr_fatb), SUM(cr_fatc), SUM(cr_fina), SUM(cr_tike), SUM(cr_pgcr),\
									SUM(cr_depc), SUM(cr_rcbl) FROM dcdavs WHERE cr_erec >='"+dIni+"' and cr_erec <='"+dFim+"' and cr_reca='1' and cr_vdcd='"+cd+"' and cr_tfat!='2'"

				if rFiliais == True:	anterior = anterior.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")
				if rFiliais == True:	devoluca = devoluca.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")

			""" Totaliza DAVs em Aberto Todos e o Movimento da Conta Corrente de Dia Atual """
			dvAberto = "SELECT  SUM(cr_tnot) FROM cdavs WHERE cr_edav<='"+hoje+"' and ( cr_reca='' or cr_reca='2' ) and cr_urec='' and cr_tipo='1' and cr_tfat!='2'"
			ccMovime = "SELECT  SUM(cc_credit),SUM(cc_debito) FROM conta WHERE cc_lancam='"+hoje+"'"
			dlAberto = "SELECT  SUM(cr_tnot) FROM dcdavs WHERE cr_edav<='"+hoje+"' and ( cr_reca='' or cr_reca='2' ) and cr_urec='' and cr_tipo='1' and cr_tfat!='2'"

			if rFiliais == True:	dvAberto = dvAberto.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")
			if rFiliais == True:	dlAberto = dlAberto.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")

			_mensagem = mens.showmsg("Montando relatorio { Totalizando davs abertos }!!\n\nAguarde...")
			TTAberto = sql[2].execute(dvAberto)
			TRAberto = sql[2].fetchall()

			_mensagem = mens.showmsg("Montando relatorio { Totalizando devoluções abertos }!!\n\nAguarde...")
			TDVAbert = sql[2].execute(dlAberto)
			TDRAbert = sql[2].fetchall()

			_mensagem = mens.showmsg("Montando relatorio { Totalizando movimento do conta corrente }!!\n\nAguarde...")
			TTConTES = sql[2].execute(ccMovime)
			TRConTES = sql[2].fetchall()

			""" FIM """
			_mensagem = mens.showmsg("Montando relatorio { Totalizando dias anteriores }!!\n\nAguarde...")
			cRetorno = sql[2].execute(condicao)
			ToTaliza = sql[2].fetchall()

			reTorAnt = reTorDev = reTorCon = 0
			if hoje == dIni:

				reTorAnt = sql[2].execute(anterior)
				TotalAnt = sql[2].fetchall()
				
				reTorDev = sql[2].execute(devoluca)
				TotalDev = sql[2].fetchall()

				if vdcx != "V":
					
					reTorCon = sql[2].execute(contacor)
					TotalCon = sql[2].fetchall()

			if cRetorno !=0:
				
				if ToTaliza[0][0]  != None:	TTdav = ToTaliza[0][0]
				if ToTaliza[0][1]  != None:	TTrec = ToTaliza[0][1]
				if ToTaliza[0][2]  != None:	TTroc = ToTaliza[0][2]
				if ToTaliza[0][3]  != None:	TTran = ToTaliza[0][3]
				if ToTaliza[0][5]  != None:	Tdinh = ToTaliza[0][5]
				if ToTaliza[0][6]  != None:	Tchav = ToTaliza[0][6]
				if ToTaliza[0][7]  != None:	Tchpr = ToTaliza[0][7]
				if ToTaliza[0][8]  != None:	Tccre = ToTaliza[0][8]
				if ToTaliza[0][9]  != None:	Tcdeb = ToTaliza[0][9]
				if ToTaliza[0][10] != None:	Tfabo = ToTaliza[0][10]
				if ToTaliza[0][11] != None:	Tfaca = ToTaliza[0][11]
				if ToTaliza[0][12] != None:	Tfina = ToTaliza[0][12]
				if ToTaliza[0][13] != None:	TTick = ToTaliza[0][13]
				if ToTaliza[0][14] != None:	Tpgcr = ToTaliza[0][14]
				if ToTaliza[0][15] != None:	Tdepo = ToTaliza[0][15]
				if ToTaliza[0][16] != None:	Trclo = ToTaliza[0][16]
				if ToTaliza[0][18] != None:	TTdes = ToTaliza[0][18]

				""" Somando recebimento de dias anteriores """
				vTdav += TTdav # Total de vendas Recebidas
				vTdes += TTdes
				vTrec += TTrec # Total de Davs Recebidos
				vTroc += TTroc # Total do Troco
				vTran += TTran # Total da Transferencia para conta corrente
				vTpcc += Tpgcr # Total do Pagamento com credito 
				vTrcl += Trclo # Receber Local

			if reTorAnt !=0:
				
				if TotalAnt[0][0]  != None:	vAdav = TotalAnt[0][0]
				if TotalAnt[0][1]  != None:	vArec = TotalAnt[0][1]
				if TotalAnt[0][2]  != None:	vAroc = TotalAnt[0][2]
				if TotalAnt[0][3]  != None:	vAran = TotalAnt[0][3]
				if TotalAnt[0][5]  != None:	Adinh = TotalAnt[0][5]
				if TotalAnt[0][6]  != None:	Achav = TotalAnt[0][6]
				if TotalAnt[0][7]  != None:	Achpr = TotalAnt[0][7]
				if TotalAnt[0][8]  != None:	Accre = TotalAnt[0][8]
				if TotalAnt[0][9]  != None:	Acdeb = TotalAnt[0][9]
				if TotalAnt[0][10] != None:	Afabo = TotalAnt[0][10]
				if TotalAnt[0][11] != None:	Afaca = TotalAnt[0][11]
				if TotalAnt[0][12] != None:	Afina = TotalAnt[0][12]
				if TotalAnt[0][13] != None:	ATick = TotalAnt[0][13]
				if TotalAnt[0][14] != None:	Apgcr = TotalAnt[0][14]
				if TotalAnt[0][15] != None:	Adepo = TotalAnt[0][15]
				if TotalAnt[0][16] != None:	Arclo = TotalAnt[0][16]
				if TotalAnt[0][17] != None:	Adesc = TotalAnt[0][17]

				""" Somando recebimento de dias anteriores """
				vTdav += vAdav # Total de vendas Recebidas
				vTdes += Adesc
				vTrec += vArec # Total de Davs Recebidos
				vTroc += vAroc # Total do Troco
				vTran += vAran # Total da Transferencia para conta corrente
				vTpcc += vApcc # Total do Pagamento com credito 
				vTrcl += Arclo # Receber Local

			#----:[ Pagamento de devolucao em dinheiro ]
			if reTorDev !=0:
				if TotalDev[0][2] != None:	TDevd = TotalDev[0][2]

			#----:[  Pagamento de creditos ]
			if reTorCon !=0:

				if TotalCon[0][0] != None:	TCont = TotalCon[0][0]
				if vReTorno == 0 and TCont !=0:	vReTorno = 1

			""" Somanda o contas areceber [ contas recebidas ] """
			if rcbReto != 0:

				vTdav += vRdav #-: Total de vendas Recebidas
				vTrec += vRrec #-: Total de Davs Recebidos
				vTroc += vRroc #-: Total do Troco
				vTran += vRran #-: Total da Transferencia para conta corrente
				vTpcc += Rpgcr #-: Total do Pagamento com credito 

			""" Valor Totais de Vendas e Custos de Vendas """
			condicao = "SELECT SUM(cr_tnot),SUM(cr_cust) FROM cdavs WHERE cr_edav >='"+dIni+"' and cr_edav <='"+dFim+"' and cr_reca!='3' and cr_tipo='1' and cr_tfat!='2'"
			if rFiliais == True:	condicao = condicao.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")

			_mensagem = mens.showmsg("Montando relatorio { Totalizando custo de vendas }!!\n\nAguarde...")
			cRetorno = sql[2].execute(condicao)
			ToTaliza = sql[2].fetchall()
			if cRetorno !=0 and ToTaliza[0][0] != None:	vTven = ToTaliza[0][0]
			if cRetorno !=0 and ToTaliza[0][1] != None:	CusVd = ToTaliza[0][1]

			""" Verifica Custo Vazio """
			cusVazio = "SELECT cr_vazc FROM cdavs WHERE cr_edav >='"+dIni+"' and cr_edav <='"+dFim+"' and cr_reca!='3' and cr_tipo='1' and cr_vazc='T' and cr_tfat!='2'"
			if rFiliais == True:	cusVazio = cusVazio.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")

			_mensagem = mens.showmsg("Montando relatorio { Totalizando custos vazios }!!\n\nAguarde...")
			cVazio   = sql[2].execute(cusVazio)

			""" Verifica Custo Vazio """
			dcusVazio = "SELECT cr_vazc FROM dcdavs WHERE cr_edav >='"+dIni+"' and cr_edav <='"+dFim+"' and cr_reca!='3' and cr_tipo='1' and cr_vazc='T' and cr_tfat!='2'"
			if rFiliais == True:	dcusVazio = dcusVazio.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")
			
			dcVazio   = sql[2].execute(cusVazio)
			
			""" Totaliza Devolucoes e Custos de Devolucoẽs """
			_devoluca = "SELECT  SUM(cr_tnot),SUM(cr_cust) FROM dcdavs WHERE cr_edav >='"+dIni+"' and cr_edav <='"+dFim+"' and cr_reca!='3' and cr_tfat!='2'"
			if rFiliais == True:	_devoluca = _devoluca.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")

			_mensagem = mens.showmsg("Montando relatorio { Totalizando custo de devoluções }!!\n\nAguarde...")
			cDevoluc = sql[2].execute(_devoluca)
			TDevoluc = sql[2].fetchall()
			if cDevoluc !=0 and TDevoluc[0][0] != None:	TTdev = TDevoluc[0][0]
			if cDevoluc !=0 and TDevoluc[0][1] != None:	CusDv = TDevoluc[0][1]

			""" Valore Totais de Vendas em aberto """
			condicao = "SELECT SUM(cr_tnot) FROM cdavs WHERE cr_edav >='"+dIni+"' and cr_edav <='"+dFim+"' and cr_reca='' and cr_tipo='1' and cr_tfat!='2'"
			if rFiliais == True:	condicao = condicao.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")

			_mensagem = mens.showmsg("Montando relatorio { Totalizando davs abertos }!!\n\nAguarde...")
			cRetorno = sql[2].execute(condicao)
			ToTaliza = sql[2].fetchall()
			if cRetorno !=0 and ToTaliza[0][0] != None:	vTabe = ToTaliza[0][0]

			""" Valor Totais de Vendas cancelados """
			condicao = "SELECT SUM(cr_tnot) FROM cdavs WHERE cr_edav >='"+dIni+"' and cr_edav <='"+dFim+"' and cr_reca='3'  and cr_tipo='1' and cr_tfat!='2'"
			if rFiliais == True:	condicao = condicao.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")

			_mensagem = mens.showmsg("Montando relatorio { Totalizando vendas canceladas }!!\n\nAguarde...")
			cRetorno = sql[2].execute(condicao)
			ToTaliza = sql[2].fetchall()
			if cRetorno !=0 and ToTaliza[0][0] != None:	vTcan = ToTaliza[0][0]

			""" Valor Totais de Vendas estornado """
			condicao = "SELECT SUM(cr_tnot) FROM cdavs WHERE cr_edav >='"+dIni+"' and cr_edav <='"+dFim+"' and cr_reca='2'  and cr_tipo='1' and cr_tfat!='2'"
			if rFiliais == True:	condicao = condicao.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and ")

			_mensagem = mens.showmsg("Montando relatorio { Totalizando vendas estornadas }!!\n\nAguarde...")
			cRetorno = sql[2].execute(condicao)
			ToTaliza = sql[2].fetchall()
			if cRetorno !=0 and ToTaliza[0][0] != None:	vTest = ToTaliza[0][0]
			
			conn.cls(sql[1])

		del _mensagem
		
		if   vReTorno == 0:	alertas.dia(par,u"Sem registro de vendas p/o período informado...",u"Relatórios: Posição de Vendas")
		elif vReTorno != 0:
			
			_mensagem = mens.showmsg("Montando relatorio!!\n\nAguarde...")
			nomeArquivo = diretorios.usPasta+"psv_"+login.usalogin.lower()+".pdf"

			""" Abertura do Arquivo """
			cv = canvas.Canvas(nomeArquivo, pagesize=landscape(A4))

			linhas = 435
			lcampo = 440
			regis  = 1
			pagin  = 1
			
			if lnhsn == True:
				
				nPg = ( Decimal(reTorAnt+vReTorno) / Decimal('47') )
				if      str(nPg) != "1" and len( str(nPg).split('.') ) == 2 and str(nPg).split('.')[1][:2] == "00":	nPg = int(nPg)
				else:	nPg = ( int(nPg) + 2 )
					
			else:

				nPg = ( Decimal(reTorAnt+vReTorno) / Decimal('70') )
				if      str(nPg) != "1" and len( str(nPg).split('.') ) == 2 and str(nPg).split('.')[1][:2] == "00":	nPg = int(nPg)
				else:	nPg = ( int(nPg) + 2 )

			""" Montagem da Pagina do Resumo """
			cabvendas(False)

			ln = 480
			for i in range(18):
				
				cv.line(20,ln,820,ln) #-->[ Linha  ]
				ln -=10

			cl = 180
			for i in range(8):

				cv.line(cl,480,cl,320) #-->[ Colunas ]
				cl +=80

			""" Cor de fundo no cabecalho de Titulos """
			cv.setFillGray(0.1,0.1) 
			cv.rect(20,470,800,10, fill=1)
			cv.rect(500,320,320,150, fill=1)
			cv.rect(20,310,800,10, fill=1)
			cv.rect(455,87.5,355,46.5, fill=1) #-: Conta Corrente [ Entrada,Saida,Saldo ]
			cv.setFillColor(HexColor('0x000000'))

			""" Totalização de Lucro e Custo """
			cv.line(810,290,800,290) #-->[ Linha Pequena Fecha em cima Lateral Direita ]
			cv.line(810,275,455,275) #-->[ Linha Primeira Linha ]

			cv.line(810, 70,810,290) #-->[ Linha Lateral Direita  ]
			cv.line(810, 70,450, 70) #-->[ Linha Ultima Linha ]
			cv.line(450, 70,450, 75) #-->[ Linha Pequena em Baixo Lateral Esquerda  ]

			cv.setFont('Helvetica-Bold', 10)
			cv.setFillColor(HexColor('0x000000'))
			cv.drawString(565,277,"Resumo do Lucro-Custo")

			cv.setFont('Helvetica', 9)
			cv.setFillColor(HexColor('0x4D4D4D'))
			cv.drawString(460,260,"a)Total de Vendas")
			cv.drawString(460,245,"b) Total de Devoluções")
			
			cv.drawString(460,214,"c) Total do Custo de Vendas")
			cv.drawString(460,200,"d) Total do Custo de Devoluções")
			cv.drawString(460,170,"g) Margem de Lucro (e-f)")


			""" Conta Corrente e DAVs Abertos """
			cv.setFont('Helvetica-Bold', 9)
			cv.setFillColor(HexColor('0x275362'))
			cv.drawString(460,154,"DAV(s) de Devoluções em Aberto de Dias Anteriores")
			cv.drawString(460,138,"DAV(s) em Aberto de Dias Anteriores")
			if TDRAbert[0][0] != None and  TDRAbert[0][0]: cv.drawRightString(805,154,format(TDRAbert[0][0],',')) #-: Total de Devolucoes Aberto Totos
			if TRAberto[0][0] != None and  TRAberto[0][0]: cv.drawRightString(805,138,format(TRAberto[0][0],',')) #-: Total de DAVs Aberto Totos

			cv.setFillColor(HexColor('0x2E2E97'))
			cv.drawString(460,122,"Conta Corrente Movimento: "+format(datetime.datetime.now(),'%d/%m/%Y')+" { Entrada }")
			if TRConTES[0][0] != None and  TRConTES[0][0]: cv.drawRightString(805,122,format(TRConTES[0][0],',')) #-: Conta Corrente Entrada

			cENT = cSAI = Decimal('0.00')
			if TRConTES[0][0] !=None and TRConTES[0][0]:	cENT = TRConTES[0][0]
			if TRConTES[0][1] !=None and TRConTES[0][1]:	cSAI = TRConTES[0][1]
			cSAL = ( cENT - cSAI )

			cv.setFillColor(HexColor('0xD31313'))
			cv.drawString(460,106,"Conta Corrente Movimento: "+format(datetime.datetime.now(),'%d/%m/%Y')+" { Saida }")
			if TRConTES[0][1] != None and  TRConTES[0][1]: cv.drawRightString(805,106,format(TRConTES[0][1],',')) #-: Conta Corrente Saida

			if cSAL:	cv.setFillColor(HexColor('0x2E2E97'))
			cv.drawString(460,91,"Conta Corrente { Saldo }")
			if cSAL: cv.drawRightString(805,91,format(cSAL,',')) #-: Conta Corrente Saldo
			cv.setFillColor(HexColor('0x000000'))
			cv.setFont('Helvetica', 9)

			""" Conta Corrente e Abertos """


			if par.ToTMarg.GetValue() and vTven: cv.drawRightString(805,260,format(vTven,',')) #-: Total de Vendas
			if par.ToTMarg.GetValue() and TTdev: cv.drawRightString(805,245,format(TTdev,',')) #-: Total de Devolucoes
			if par.ToTMarg.GetValue() and CusVd: cv.drawRightString(805,215,format(CusVd,',')) #-: Total de Devolucoes
			if par.ToTMarg.GetValue() and CusVd: cv.drawRightString(805,200,format(CusDv,',')) #-: Total de Devolucoes

			sVendas = ( vTven - TTdev )
			sCustos = ( CusVd - CusDv )
			mLucros = ( sVendas - sCustos )

			if mLucros and sVendas:	margemL = T.trunca(3, ( mLucros / sVendas * 100 ) )
			else:margemL = Decimal('0.00')
			
			if par.ToTMarg.GetValue() and mLucros: cv.drawRightString(805,170,format(mLucros,','))
			if cVazio or dcVazio:	cv.setFillColor(HexColor('0xC11919'))
			if par.ToTMarg.GetValue() and margemL: cv.drawRightString(700,170,"( "+str(margemL)+" % )") #-: Margem de lucro

			cv.setFont('Helvetica-Bold', 9)
			cv.setFillColor(HexColor('0x1A1A1A'))
			cv.drawString(460,230,"e) Saldo de Vendas (a-b)")
			cv.drawString(460,185,"f) Saldo do Custo (c-d)")
			if par.ToTMarg.GetValue() and sVendas > 0: cv.drawRightString(805,230,format(sVendas,',')) #-: Total de Devolucoes
			if par.ToTMarg.GetValue() and sCustos > 0: cv.drawRightString(805,185,format(sCustos,',')) #-: Total de Devolucoes
			
			lrc = 258
			for l in range(12):
				cv.line(810,lrc,455,lrc) #-->[ Linha  ]
				lrc -= 15.5

			cv.line(720, ( lrc + 17 ),720,273) #-->[ Linha  ]
			cv.line(455, ( lrc + 15.5 ),455,275) #-->[ Linha  ]

			""" Resumo de Vendas """
			se = separ
			ln = lnhsn
			separ = lnhsn = False

			cv.setFont('Helvetica-Bold', 12)	
			if rFiliais == True:	cv.drawString(22,538,"{ Resumo de Vendas } Filial: "+str( Filial ) )
			else:	cv.drawString(22,538,"Resumo de Vendas")

			cv.setFont('Helvetica', 9)	
			cv.drawString(22,515,"Usuario:")
			cv.drawString(22,505,"Periodo:")
			cv.drawString(22,495,"Tipo:")
			cv.drawString(22,485,"Nº Paginas:")
			cv.drawString(80,515,str(login.usalogin))
			cv.drawString(80,505,str(cIni)+' A '+str(cFim))
			cv.drawString(80,495,str(relTipo))
			cv.drawString(80,485,str(nPg))

			cv.setFillColor(HexColor('0x7F7F7F'))
			cv.drawString(340,515,"Total de vendas:")
			cv.drawString(540,515,"Descontos:")
			cv.drawString(340,505,"Abertos:")
			cv.drawString(340,495,"Abertos estornados:")
			cv.drawString(540,485,"DAVs cancelados:")

			cv.setFillColor(HexColor('0x4D4D4D'))
			cv.drawString(340,485,"S a l d o:")

			cv.setFillColor(HexColor('0x000000'))
			cv.setFont('Helvetica-Bold', 6)
			cv.drawString(182,472,"Recebimentos {"+datetime.datetime.strptime(dI.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")+"}")
			cv.setFont('Helvetica-Bold', 7)
			cv.drawString(23, 472,"Formas de Pagamento")
			cv.drawString(262,472,"Rcbto Dias anteriores")
			cv.drawString(342,472,"Contas a receber")
			cv.drawString(422,472,"Total de recebimentos")
			cv.drawString(502,472,"Sangria")
			cv.drawString(582,472,"Devolução dinheiro")
			cv.drawString(662,472,"Pagamento do crédito")
			cv.drawString(742,472,"S a l d o")

			#cv.drawString(22,462,"a-Dinheiro")
			#cv.drawString(22,452,"b-Cheque avista")
			#cv.drawString(22,442,"c-Cheque predatado")
			#cv.drawString(22,432,"d-Cartão de crédito")
			#cv.drawString(22,422,"f-Cartão de débito")
			#cv.drawString(22,412,"g-Faturado boleto")
			#cv.drawString(22,402,"h-Faturado carteira")
			#cv.drawString(22,392,"i-Financeira")
			#cv.drawString(22,382,"j-Tickete")
			#cv.drawString(22,372,"l-Pagamento com crédito")
			#cv.drawString(22,362,"m-Depósito em conta")
			#cv.drawString(22,352,"n-Transferência CC")
			#cv.drawString(22,342,"o-Receber no Local")
			#cv.drawString(22,332,"T r o c o")
			#cv.drawString(22,322,"a1-Suprimentos de Caixa")

			#cv.drawString(22,462,"a-Dinheiro")
			#cv.drawString(22,452,"m-Depósito em conta")
			#cv.drawString(22,442,"n-Transferência CC")
			#cv.drawString(22,432,"b-Cheque avista")
			#cv.drawString(22,422,"c-Cheque predatado")
			#cv.drawString(22,412,"d-Cartão de crédito")
			#cv.drawString(22,402,"f-Cartão de débito")
			#cv.drawString(22,392,"g-Faturado boleto")
			#cv.drawString(22,382,"h-Faturado carteira")
			#cv.drawString(22,372,"i-Financeira")
			#cv.drawString(22,362,"j-Tickete")
			#cv.drawString(22,352,"l-Pagamento com crédito")
			#cv.drawString(22,342,"o-Receber no Local")
			#cv.drawString(22,332,"T r o c o")

			cv.setFont('Helvetica', 8)
			cv.drawString(22,462,"a-Dinheiro")
			cv.drawString(22,452,"m-Depósito em conta")
			cv.drawString(22,442,"b-Cheque avista")
			cv.drawString(22,432,"c-Cheque predatado")
			cv.drawString(22,422,"d-Cartão de crédito")
			cv.drawString(22,412,"f-Cartão de débito")
			cv.drawString(22,402,"g-Faturado boleto")
			cv.drawString(22,392,"h-Faturado carteira")
			cv.drawString(22,382,"i-Financeira")
			cv.drawString(22,372,"j-Tickete")
			cv.drawString(22,362,"l-Pagamento com crédito")
			cv.drawString(22,352,"n-Transferência CC")
			cv.drawString(22,342,"o-Receber no Local")
			cv.drawString(22,332,"T r o c o")
			cv.drawString(22,322,"a1-Suprimentos de Caixa")
			cv.drawString(22,312,"Observação")

			cv.rect(30,47,333,30, fill=0)
			cv.setFillColor(HexColor('0x7F7F7F'))
			cv.drawString(210,65,"3 - Devolução em dinheiro:")
			cv.drawString(210,55,"Saldo do avista ( 1 - 3 ):")
			
			"""   Loucuras de alguns lojistas   """
			if len( login.filialLT[ Filial ][35].split(";") ) >=43 and login.filialLT[ Filial ][35].split(";")[42] == "T":

				cv.drawString(32,65,"1 - Total do Avista ( a,b,c,d,f,j ):")
				cv.drawString(32,55,"2 - Total do Aprazo ( g,h,i,m, o ):")
			else:
				
				cv.drawString(32,65,"1 - Total do Avista ( a,b,f,j,m ):")
				cv.drawString(32,55,"2 - Total do Aprazo ( c,d,g,h,i,o ):")
		
			cv.setFont('Helvetica-Bold', 8)
			cv.setFillColor(HexColor('0x7F7F7F'))
			if vTven > 0: cv.drawRightString(470,515,format( ( vTven + vTdes ),',')) #-: Total de Vendas
			if vTdes > 0: cv.drawRightString(670,515,format(vTdes,',')) #-: Total de descontos
			if vTabe > 0: cv.drawRightString(470,505,format(vTabe,',')) #-: Pedidos em aberto
			if vTest > 0: cv.drawRightString(470,495,format(vTest,',')) #-: Pedidos em aberto e estornados
			if vTcan > 0 and cancelado == 'F':	cv.drawRightString(670,485,format(vTcan,',')) #-: Pedidos cancelados
			cv.setFillColor(HexColor('0x4D4D4D'))
			if TTdav > 0: cv.drawRightString(470,485,format(TTdav,',')) #-: Saldo { Total do Recebimento }

			""" Recebimentos do dia inicial """
			cv.setFillColor(blue)
			if Tdinh !=0:	cv.drawRightString(258,462,format(Tdinh,','))
			if Tdepo !=0:	cv.drawRightString(258,452,format(Tdepo,','))
			if Tchav !=0:	cv.drawRightString(258,442,format(Tchav,','))
			if Tchpr !=0:	cv.drawRightString(258,432,format(Tchpr,','))
			if Tccre !=0:	cv.drawRightString(258,422,format(Tccre,','))
			if Tcdeb !=0:	cv.drawRightString(258,412,format(Tcdeb,','))
			if Tfabo !=0:	cv.drawRightString(258,402,format(Tfabo,','))
			if Tfaca !=0:	cv.drawRightString(258,392,format(Tfaca,','))
			if Tfina !=0:	cv.drawRightString(258,382,format(Tfina,','))
			if TTick !=0:	cv.drawRightString(258,372,format(TTick,','))
			if Tpgcr !=0:	cv.drawRightString(258,362,format(Tpgcr,','))
			if TTran !=0:	cv.drawRightString(258,352,format(TTran,','))
			if Trclo !=0:	cv.drawRightString(258,342,format(Trclo,','))
			if TTroc !=0:	cv.drawRightString(258,332,format(TTroc,','))
			
#			if Tdinh !=0:	cv.drawRightString(258,462,format(Tdinh,','))
#			if Tchav !=0:	cv.drawRightString(258,452,format(Tchav,','))
#			if Tchpr !=0:	cv.drawRightString(258,442,format(Tchpr,','))
#			if Tccre !=0:	cv.drawRightString(258,432,format(Tccre,','))
#			if Tcdeb !=0:	cv.drawRightString(258,422,format(Tcdeb,','))
#			if Tfabo !=0:	cv.drawRightString(258,412,format(Tfabo,','))
#			if Tfaca !=0:	cv.drawRightString(258,402,format(Tfaca,','))
#			if Tfina !=0:	cv.drawRightString(258,392,format(Tfina,','))
#			if TTick !=0:	cv.drawRightString(258,382,format(TTick,','))
#			if Tpgcr !=0:	cv.drawRightString(258,372,format(Tpgcr,','))
#			if Tdepo !=0:	cv.drawRightString(258,362,format(Tdepo,','))
#			if TTran !=0:	cv.drawRightString(258,352,format(TTran,','))
#			if TTran !=0:	cv.drawRightString(258,352,format(TTran,','))
#			if Trclo !=0:	cv.drawRightString(258,342,format(Trclo,','))
#			if TTroc !=0:	cv.drawRightString(258,332,format(TTroc,','))

			""" Suprimentos """
			cv.setFillColor(HexColor('0x0E59A2'))
			if sasup !=0:	cv.drawRightString(258,322,"("+format(sasup,',')+")")

			""" Recebimentos de dias anteriores """
			cv.setFillColor(orange)
			#if Adinh !=0:	cv.drawRightString(338,462,format(Adinh,','))
			#if Achav !=0:	cv.drawRightString(338,452,format(Achav,','))
			#if Achpr !=0:	cv.drawRightString(338,442,format(Achpr,','))
			#if Accre !=0:	cv.drawRightString(338,432,format(Accre,','))
			#if Acdeb !=0:	cv.drawRightString(338,422,format(Acdeb,','))
			#if Afabo !=0:	cv.drawRightString(338,412,format(Afabo,','))
			#if Afaca !=0:	cv.drawRightString(338,402,format(Afaca,','))
			#if Afina !=0:	cv.drawRightString(338,392,format(Afina,','))
			#if ATick !=0:	cv.drawRightString(338,382,format(ATick,','))
			#if Apgcr !=0:	cv.drawRightString(338,372,format(Apgcr,','))
			#if Adepo !=0:	cv.drawRightString(338,362,format(Adepo,','))
			#if vAran !=0:	cv.drawRightString(338,352,format(vAran,','))
			#if Arclo !=0:	cv.drawRightString(338,342,format(Arclo,','))
			#if vAroc !=0:	cv.drawRightString(338,332,format(vAroc,','))

			if Adinh !=0:	cv.drawRightString(338,462,format(Adinh,','))
			if Adepo !=0:	cv.drawRightString(338,452,format(Adepo,','))
			if Achav !=0:	cv.drawRightString(338,442,format(Achav,','))
			if Achpr !=0:	cv.drawRightString(338,432,format(Achpr,','))
			if Accre !=0:	cv.drawRightString(338,422,format(Accre,','))
			if Acdeb !=0:	cv.drawRightString(338,412,format(Acdeb,','))
			if Afabo !=0:	cv.drawRightString(338,402,format(Afabo,','))
			if Afaca !=0:	cv.drawRightString(338,392,format(Afaca,','))
			if Afina !=0:	cv.drawRightString(338,382,format(Afina,','))
			if ATick !=0:	cv.drawRightString(338,372,format(ATick,','))
			if Apgcr !=0:	cv.drawRightString(338,362,format(Apgcr,','))
			if vAran !=0:	cv.drawRightString(338,352,format(vAran,','))
			if Arclo !=0:	cv.drawRightString(338,342,format(Arclo,','))
			if vAroc !=0:	cv.drawRightString(338,332,format(vAroc,','))

			""" Recebimentos do contas areceber """
			cv.setFillColor(green)
			#if Rdinh !=0:	cv.drawRightString(418,462,format(Rdinh,','))
			#if Rchav !=0:	cv.drawRightString(418,452,format(Rchav,','))
			#if Rchpr !=0:	cv.drawRightString(418,442,format(Rchpr,','))
			#if Rccre !=0:	cv.drawRightString(418,432,format(Rccre,','))
			#if Rcdeb !=0:	cv.drawRightString(418,422,format(Rcdeb,','))
			#if Rfina !=0:	cv.drawRightString(418,392,format(Rfina,','))
			#if RTick !=0:	cv.drawRightString(418,382,format(RTick,','))
			#if Rpgcr !=0:	cv.drawRightString(418,372,format(Rpgcr,','))
			#if Rdepo !=0:	cv.drawRightString(418,362,format(Rdepo,','))
			#if vRran !=0:	cv.drawRightString(418,352,format(vRran ,','))
			#if vRroc !=0:	cv.drawRightString(418,332,format(vRroc ,','))

			if Rdinh !=0:	cv.drawRightString(418,462,format(Rdinh,','))
			if Rdepo !=0:	cv.drawRightString(418,452,format(Rdepo,','))
			if Rchav !=0:	cv.drawRightString(418,442,format(Rchav,','))
			if Rchpr !=0:	cv.drawRightString(418,432,format(Rchpr,','))
			if Rccre !=0:	cv.drawRightString(418,422,format(Rccre,','))
			if Rcdeb !=0:	cv.drawRightString(418,412,format(Rcdeb,','))
			if Rfina !=0:	cv.drawRightString(418,382,format(Rfina,','))
			if RTick !=0:	cv.drawRightString(418,372,format(RTick,','))
			if Rpgcr !=0:	cv.drawRightString(418,362,format(Rpgcr,','))
			if vRran !=0:	cv.drawRightString(418,352,format(vRran ,','))
			if vRroc !=0:	cv.drawRightString(418,332,format(vRroc ,','))
                                                   
			""" Totalizador de recebimentos """    
			TgDin = ( Tdinh + Adinh + Rdinh ) #-: Dinheiro
			TgCha = ( Tchav + Achav + Rchav ) #-: Cheque Avista
			TgCpr = ( Tchpr + Achpr + Rchpr ) #-: Cheque Predatado
			TgCcr = ( Tccre + Accre + Rccre ) #-: Cartao Credito
			TgCdb = ( Tcdeb + Acdeb + Rcdeb ) #-: Cartao Debito
			TgBol = ( Tfabo + Afabo ) #---------: Boleto
			TgCar = ( Tfaca + Afaca ) #---------: Carteira
			TgFin = ( Tfina + Afina + Rfina ) #-: Financeira
			TgTik = ( TTick + ATick + RTick ) #-: Tickete
			TgPgc = ( Tpgcr + Apgcr + Rpgcr ) #-: Pagamento c/Credito
			TgDep = ( Tdepo + Adepo + Rdepo ) #-: Deposito em conta
			TgTra = ( TTran + vAran + vRran ) #-: Transferencia p/Conta Corrente
			TgTro = ( TTroc + vAroc + vRroc ) #-: Troco

			"""   Totaliza Avista,Aprazo   """
			"""   Loucuras de alguns lojistas  { Moacir Madeirao }   """
			if len( login.filialLT[ Filial ][35].split(";") ) >=43 and login.filialLT[ Filial ][35].split(";")[42] == "T":

				ToTalAvisTA = ( TgDin + TgCha + TgCpr + TgCcr + TgCdb + TgTik - TgTro)
				ToTalAprazo = ( TgBol + TgCar + TgFin + TgDep  )
			else:

				ToTalAvisTA = ( TgDin + TgCha + TgCdb + TgDep + TgTik -TgTro )
				ToTalAprazo = ( TgCpr + TgCcr + TgBol + TgCar + TgFin  )

			cv.setFillColor(HexColor('0x7F7F7F'))
			if ToTalAvisTA > 0: cv.drawRightString(198,65,format(ToTalAvisTA,','))
			if ToTalAprazo > 0:	cv.drawRightString(198,55,format(ToTalAprazo,','))
			if TDevd > 0:	cv.drawRightString(360,65,format(TDevd,','))
			if ToTalAvisTA:	cv.drawRightString(360,55,format( ( ToTalAvisTA - TDevd ),','))

			cv.setFillColor(HexColor('0x10355A'))
			#if TgDin !=0:	cv.drawRightString(498,462,format(TgDin,','))
			#if TgCha !=0:	cv.drawRightString(498,452,format(TgCha,','))
			#if TgCpr !=0:	cv.drawRightString(498,442,format(TgCpr,','))
			#if TgCcr !=0:	cv.drawRightString(498,432,format(TgCcr,','))
			#if TgCdb !=0:	cv.drawRightString(498,422,format(TgCdb,','))
			#if TgBol !=0:	cv.drawRightString(498,412,format(TgBol,','))
			#if TgCar !=0:	cv.drawRightString(498,402,format(TgCar,','))
			#if TgFin !=0:	cv.drawRightString(498,392,format(TgFin,','))
			#if TgTik !=0:	cv.drawRightString(498,382,format(TgTik,','))
			#if TgPgc !=0:	cv.drawRightString(498,372,format(TgPgc,','))
			#if TgDep !=0:	cv.drawRightString(498,362,format(TgDep,','))
			#if TgTra !=0:	cv.drawRightString(498,352,format(TgTra,','))
			#if vTrcl !=0:	cv.drawRightString(498,342,format(vTrcl,','))
			#if TgTro !=0:	cv.drawRightString(498,332,format(TgTro,','))

			if TgDin !=0:	cv.drawRightString(498,462,format(TgDin,','))
			if TgDep !=0:	cv.drawRightString(498,452,format(TgDep,','))
			
			if TgCha !=0:	cv.drawRightString(498,442,format(TgCha,','))
			if TgCpr !=0:	cv.drawRightString(498,432,format(TgCpr,','))
			if TgCcr !=0:	cv.drawRightString(498,422,format(TgCcr,','))
			if TgCdb !=0:	cv.drawRightString(498,412,format(TgCdb,','))
			if TgBol !=0:	cv.drawRightString(498,402,format(TgBol,','))
			if TgCar !=0:	cv.drawRightString(498,392,format(TgCar,','))
			if TgFin !=0:	cv.drawRightString(498,382,format(TgFin,','))
			if TgTik !=0:	cv.drawRightString(498,372,format(TgTik,','))
			if TgPgc !=0:	cv.drawRightString(498,362,format(TgPgc,','))
			if TgTra !=0:	cv.drawRightString(498,352,format(TgTra,','))
			if vTrcl !=0:	cv.drawRightString(498,342,format(vTrcl,','))
			if TgTro !=0:	cv.drawRightString(498,332,format(TgTro,','))

			"""Saldo Sangria """
			sanDin = ( saDin - seDin )
			sanCha = ( saCha - seCha )
			sanCpr = ( saChp - seChp )
			sanCcr = ( saCcr - seCcr )
			sanCdb = ( saCdb - seCdb )

			SDin = SCha = SChp = SCdb = SCre = SBol = SCar = SFin = STic = Decimal('0.00')
			
			""" Saldos Geral """
			SDin = ( TgDin - sanDin - TDevd -TCont - TgTro)
			SCha = ( TgCha - sanCha )
			SChp = ( TgCpr - sanCpr )
			SCre = ( TgCcr - sanCcr )
			SCdb = ( TgCdb - sanCdb )
			SBol = ( TgBol )
			SCar = ( TgCar )
			SFin = ( TgFin )
			STic = ( TgTik )

			""" 
				So Totaliza saldos se for o mesmo dias Periodo apenas totaliza vendas 
				p/Nao fazer confusao SPA-PS
			"""
			if hoje == dIni:
				
				""" Sangria: Saida """
				cv.setFillColor(HexColor('0xD11D1D'))
				cv.setFont('Helvetica-Bold', 6)
				if sanDin:	cv.drawRightString(578,462,format(sanDin,',')) #cv.drawRightString(578,462,format(sanDin,','))
				if sanCha:	cv.drawRightString(578,442,format(sanCha,',')) #cv.drawRightString(578,452,format(sanCha,','))
				if sanCpr:	cv.drawRightString(578,432,format(sanCpr,',')) #cv.drawRightString(578,442,format(sanCpr,','))
				if sanCcr:	cv.drawRightString(578,422,format(sanCcr,',')) #cv.drawRightString(578,432,format(sanCcr,','))
				if sanCdb:	cv.drawRightString(578,412,format(sanCdb,',')) #cv.drawRightString(578,422,format(sanCdb,','))

				""" Sangria: Entrada """
				cv.setFillColor(HexColor('0x25588A'))
				if seDin:	cv.drawRightString(532,466,format(seDin,',')) #cv.drawRightString(532,466,format(seDin,','))
				if seCha:	cv.drawRightString(532,446,format(seCha,',')) #cv.drawRightString(532,456,format(seCha,','))
				if seChp:	cv.drawRightString(532,436,format(seChp,',')) #cv.drawRightString(532,446,format(seChp,','))
				if seCcr:	cv.drawRightString(532,426,format(seCcr,',')) #cv.drawRightString(532,436,format(seCcr,','))
				if seCdb:	cv.drawRightString(532,416,format(seCdb,',')) #cv.drawRightString(532,426,format(seCdb,','))

				""" Sangria:  Saldo Entrada - Saida """
				cv.setFillColor(HexColor('0xD11D1D'))
				if saDin and seDin:	cv.drawRightString(532,460,format(saDin,',')) #cv.drawRightString(532,460,format(saDin,','))
				if saCha and seCha:	cv.drawRightString(532,440,format(saCha,',')) #cv.drawRightString(532,450,format(saCha,','))
				if saChp and seChp:	cv.drawRightString(532,430,format(saChp,',')) #cv.drawRightString(532,440,format(saChp,','))
				if saCcr and seCcr:	cv.drawRightString(532,420,format(saCcr,',')) #cv.drawRightString(532,430,format(saCcr,','))
				if saCdb and seCdb:	cv.drawRightString(532,410,format(saCdb,',')) #cv.drawRightString(532,420,format(saCdb,','))


				""" Devolucao em Dinheiro  """
				cv.setFont('Helvetica-Bold', 8)
				cv.setFillColor(violet)
				if TDevd !=0:	cv.drawRightString(657,462,format(TDevd,','))

				""" Devolucao em dinheiro do Troco """
				cv.setFillColor(HexColor('0xA52A2A'))
				if TgTro !=0:	cv.drawRightString(657,332,format(TgTro,','))
				
				""" Pagamento do credito """
				if TCont !=0:	cv.drawRightString(737,462,format(TCont,','))


				""" 
					Saldo 
				"""
				#if SDin > 0:	cv.setFillColor(HexColor('0x215F9C'))
				#else:	cv.setFillColor(HexColor('0xA52A2A'))
				#if SDin != 0:	cv.drawRightString(818,462,format(SDin,','))
				#															
				#if SCha > 0:	cv.setFillColor(HexColor('0x215F9C'))       
				#else:	cv.setFillColor(HexColor('0xA52A2A'))               
				#if SCha != 0:	cv.drawRightString(818,452,format(SCha,','))
				#															
				#if SChp > 0:	cv.setFillColor(HexColor('0x215F9C'))       
				#else:	cv.setFillColor(HexColor('0xA52A2A'))               
				#if SChp != 0:	cv.drawRightString(818,442,format(SChp,','))
				#															
				#if SCre > 0:	cv.setFillColor(HexColor('0x215F9C'))       
				#else:	cv.setFillColor(HexColor('0xA52A2A'))               
				#if SCre != 0:	cv.drawRightString(818,432,format(SCre,','))
				#
				#if SCdb > 0:	cv.setFillColor(HexColor('0x215F9C'))
				#else:	cv.setFillColor(HexColor('0xA52A2A'))
				#if SCdb != 0:	cv.drawRightString(818,422,format(SCdb,','))

				if SDin > 0:	cv.setFillColor(HexColor('0x215F9C'))
				else:	cv.setFillColor(HexColor('0xA52A2A'))
				if SDin != 0:	cv.drawRightString(818,462,format(SDin,','))
																			
				if SCha > 0:	cv.setFillColor(HexColor('0x215F9C'))       
				else:	cv.setFillColor(HexColor('0xA52A2A'))               
				if SCha != 0:	cv.drawRightString(818,442,format(SCha,','))
																			
				if SChp > 0:	cv.setFillColor(HexColor('0x215F9C'))       
				else:	cv.setFillColor(HexColor('0xA52A2A'))               
				if SChp != 0:	cv.drawRightString(818,432,format(SChp,','))
																			
				if SCre > 0:	cv.setFillColor(HexColor('0x215F9C'))       
				else:	cv.setFillColor(HexColor('0xA52A2A'))               
				if SCre != 0:	cv.drawRightString(818,422,format(SCre,','))

				if SCdb > 0:	cv.setFillColor(HexColor('0x215F9C'))
				else:	cv.setFillColor(HexColor('0xA52A2A'))
				if SCdb != 0:	cv.drawRightString(818,412,format(SCdb,','))

				"""   Nao Mostrar o saldo no resumo para essas formas de pagamentos { Loucuras Madeirao }   """
				nSaldo = True
				if len( login.filialLT[ Filial ][35].split(";") ) >=45 and login.filialLT[ Filial ][35].split(";")[44] == "T":	nSaldo = False

				#if SBol > 0:	cv.setFillColor(HexColor('0x215F9C'))
				#else:	cv.setFillColor(HexColor('0xA52A2A'))
				#if SBol != 0 and nSaldo == True:	cv.drawRightString(818,412,format(SBol,','))
				#
				#if SCar > 0:	cv.setFillColor(HexColor('0x215F9C'))
				#else:	cv.setFillColor(HexColor('0xA52A2A'))
				#if SCar != 0 and nSaldo == True:	cv.drawRightString(818,402,format(SCar,','))
				#
				#if SFin > 0:	cv.setFillColor(HexColor('0x215F9C'))
				#else:	cv.setFillColor(HexColor('0xA52A2A'))
				#if SFin != 0 and nSaldo == True:	cv.drawRightString(818,392,format(SFin,','))
				#
				#if STic > 0:	cv.setFillColor(HexColor('0x215F9C'))
				#else:	cv.setFillColor(HexColor('0xA52A2A'))
				#if STic != 0:	cv.drawRightString(818,382,format(STic,','))

				if SBol > 0:	cv.setFillColor(HexColor('0x215F9C'))
				else:	cv.setFillColor(HexColor('0xA52A2A'))
				if SBol != 0 and nSaldo == True:	cv.drawRightString(818,402,format(SBol,','))

				if SCar > 0:	cv.setFillColor(HexColor('0x215F9C'))
				else:	cv.setFillColor(HexColor('0xA52A2A'))
				if SCar != 0 and nSaldo == True:	cv.drawRightString(818,392,format(SCar,','))

				if SFin > 0:	cv.setFillColor(HexColor('0x215F9C'))
				else:	cv.setFillColor(HexColor('0xA52A2A'))
				if SFin != 0 and nSaldo == True:	cv.drawRightString(818,382,format(SFin,','))

				if STic > 0:	cv.setFillColor(HexColor('0x215F9C'))
				else:	cv.setFillColor(HexColor('0xA52A2A'))
				if STic != 0:	cv.drawRightString(818,372,format(STic,','))
			
			cv.setFont('Courier', 8)
			cv.setFillColor(HexColor('0x1A1A1A'))
			#cv.drawString(30,280,"Dinheiro")
			#cv.drawString(30,265,"Cheque avista")
			#cv.drawString(30,250,"Cheque predatado")
			#cv.drawString(30,235,"Cartão de crédito")
			#cv.drawString(30,220,"Cartão de débito")
			#cv.drawString(30,205,"Boleto")
			#cv.drawString(30,190,"Carteira")
			#cv.drawString(30,175,"Financeira")
			#cv.drawString(30,160,"Tickete")
			#cv.drawString(30,145,"Pgto crédito")
			#cv.drawString(30,130,"Deposito em conta")
			#cv.drawString(30,115,"Receber no Local")

			cv.drawString(30,280,"Dinheiro")
			cv.drawString(30,265,"Deposito em conta")
			cv.drawString(30,250,"Cheque avista")
			cv.drawString(30,235,"Cheque predatado")
			cv.drawString(30,220,"Cartão de crédito")
			cv.drawString(30,205,"Cartão de débito")
			cv.drawString(30,190,"Boleto")
			cv.drawString(30,175,"Carteira")
			cv.drawString(30,160,"Financeira")
			cv.drawString(30,145,"Tickete")
			cv.drawString(30,130,"Pgto crédito")
			cv.drawString(30,115,"Receber no Local")

			""" Grafico """
			x = 110
			y = 430
			cv.setStrokeColorRGB(0.9,0.9,0.9)
			for c in range(12):
				cv.line(24,x,y,x) #-->[ Linha 1 ]
				x += 15
				if c <=9:	y -= 30
				
			x = 130
			y = 130
			for c in range(50):
				cv.line(y,291,y,110) #-->[ Linha 1 ]
				y +=6

			for c in range(11):
				cv.line(x,295,x,110) #-->[ Linha 1 ]
				x +=30

			cv.setStrokeColorRGB(0.0,0.0,0.0)
			cv.line(22,290,22,105) #---: Coluna 1
			cv.line(22,105,32,105) #---: Linha  1

			cv.line(22, 290,440,290) #--: Linha  2
			cv.line(440,290,440,285) #-: Coluna 1

			x = 130
			cv.setFont('Helvetica', 6)
			cv.setFillColor(HexColor('0x7F7F7F'))
			for c in range(11):
				cv.drawString(x-5,295,str(c*10)+"%")
				x +=30

			pDin = pCha = pCpr = pCre = pCdb = pBol = pCar = pFin = pTic = pPcr = pDep = pRcl = Decimal('0.00')
			nDin = nCha = nCpr = nCre = nCdb = nBol = nCar = nFin = nTic = nPcr = nDep = nRcl = Decimal('0.00')

			""" Debitar o Troco do Dinheiro p/Calculo do percentual """
			if Tdinh > 0 and TTroc > 0:	TpDin = ( Tdinh - TTroc )
			else:	TpDin = Tdinh
				
			if TpDin > 0 and TTdav > 0:	nDin = T.trunca( 5, ( TpDin / TTdav * 100 ) )
			if Tchav > 0 and TTdav > 0:	nCha = T.trunca( 5, ( Tchav / TTdav * 100 ) )
			if Tchpr > 0 and TTdav > 0:	nCpr = T.trunca( 5, ( Tchpr / TTdav * 100 ) )
			if Tccre > 0 and TTdav > 0:	nCre = T.trunca( 5, ( Tccre / TTdav * 100 ) )
			if Tcdeb > 0 and TTdav > 0:	nCdb = T.trunca( 5, ( Tcdeb / TTdav * 100 ) )
			if Tfabo > 0 and TTdav > 0:	nBol = T.trunca( 5, ( Tfabo / TTdav * 100 ) )
			if Tfaca > 0 and TTdav > 0:	nCar = T.trunca( 5, ( Tfaca / TTdav * 100 ) )
			if Tfina > 0 and TTdav > 0:	nFin = T.trunca( 5, ( Tfina / TTdav * 100 ) )
			if TTick > 0 and TTdav > 0:	nTic = T.trunca( 5, ( TTick / TTdav * 100 ) )
			if Tpgcr > 0 and TTdav > 0:	nPcr = T.trunca( 5, ( Tpgcr / TTdav * 100 ) )
			if Tdepo > 0 and TTdav > 0:	nDep = T.trunca( 5, ( Tdepo / TTdav * 100 ) )
			if Trclo > 0 and TTdav > 0:	nRcl = T.trunca( 5, ( Trclo / TTdav * 100 ) )

			if TpDin > 0 and TTdav > 0:	pDin = ( TpDin / TTdav * 300 )
			if Tchav > 0 and TTdav > 0:	pCha = ( Tchav / TTdav * 300 )
			if Tchpr > 0 and TTdav > 0:	pCpr = ( Tchpr / TTdav * 300 )
			if Tccre > 0 and TTdav > 0:	pCre = ( Tccre / TTdav * 300 )
			if Tcdeb > 0 and TTdav > 0:	pCdb = ( Tcdeb / TTdav * 300 )
			if Tfabo > 0 and TTdav > 0:	pBol = ( Tfabo / TTdav * 300 )
			if Tfaca > 0 and TTdav > 0:	pCar = ( Tfaca / TTdav * 300 )
			if Tfina > 0 and TTdav > 0:	pFin = ( Tfina / TTdav * 300 )
			if TTick > 0 and TTdav > 0:	pTic = ( TTick / TTdav * 300 )
			if Tpgcr > 0 and TTdav > 0:	pPcr = ( Tpgcr / TTdav * 300 )
			if Tdepo > 0 and TTdav > 0:	pDep = ( Tdepo / TTdav * 300 )
			if Trclo > 0 and TTdav > 0:	pRcl = ( Trclo / TTdav * 300 )
			
			cv.setFillColor(HexColor('0x4D4D4D'))
			cv.drawString(22,292,"Recebimentos: "+format(TTdav,','))

			cv.setFont('Helvetica', 8)
			cv.setFillColor(HexColor('0xFFA500'))
			if pDin !=0:	cv.rect(130,277,pDin,11, fill=1)                       
			if pDin !=0:	cv.drawString((pDin + 132 ),277,format(nDin,",")+"%")

			cv.setFillColor(HexColor('0x8B6914'))
			if pDep !=0:	cv.rect(130,262,pDep,11, fill=1)
			if pDep !=0:	cv.drawString((pDep + 132 ),262,format(nDep,",")+"%")

			cv.setFillColor(HexColor('0xA52A2A'))
			if pCha !=0:	cv.rect(130,247,pCha,11, fill=1)
			if pCha !=0:	cv.drawString((pCha + 132 ),247,format(nCha,",")+"%")

			cv.setFillColor(HexColor('0x008000'))
			if pCpr !=0:	cv.rect(130,232,pCpr,11, fill=1)
			if pCpr !=0:	cv.drawString((pCpr + 132 ),232,format(nCpr,",")+"%")

			cv.setFillColor(HexColor('0xADD8E6'))
			if pCre !=0:	cv.rect(130,217,pCre,11, fill=1)
			if pCre !=0:	cv.drawString((pCre + 132 ),217,format(nCre,",")+"%")

			cv.setFillColor(HexColor('0x0000FF'))
			if pCdb !=0:	cv.rect(130,202,pCdb,11, fill=1)
			if pCdb !=0:	cv.drawString((pCdb + 132 ),202,format(nCdb,",")+"%")

			cv.setFillColor(HexColor('0x800080'))
			if pBol !=0:	cv.rect(130,187,pBol,11, fill=1)
			if pBol !=0:	cv.drawString((pBol + 132 ),187,format(nBol,",")+"%")

			cv.setFillColor(HexColor('0xFF0000'))
			if pCar !=0:	cv.rect(130,172,pCar,11, fill=1)
			if pCar !=0:	cv.drawString((pCar + 132 ),172,format(nCar,",")+"%")

			cv.setFillColor(HexColor('0x90EE90'))
			if pFin !=0:	cv.rect(130,157,pFin,11, fill=1)
			if pFin !=0:	cv.drawString((pFin + 132 ),157,format(nFin,",")+"%")

			cv.setFillColor(HexColor('0xFFC0CB'))
			if pTic !=0:	cv.rect(130,142,pTic,11, fill=1)
			if pTic !=0:	cv.drawString((pTic + 132 ),142,format(nTic,",")+"%")

			cv.setFillColor(HexColor('0x1E90FF'))
			if pPcr !=0:	cv.rect(130,127,pPcr,11, fill=1)
			if pPcr !=0:	cv.drawString((pPcr + 132 ),127,format(nPcr,",")+"%")

			cv.setFillColor(HexColor('0xC19037'))
			if pRcl !=0:	cv.rect(130,112,pRcl,11, fill=1)
			if pRcl !=0:	cv.drawString((pRcl + 132 ),112,format(nRcl,",")+"%")

			#if pCre !=0:	cv.rect(130,232,pCre,11, fill=1)
			#if pCre !=0:	cv.drawString((pCre + 132 ),232,format(nCre,",")+"%")
			#
			#cv.setFillColor(HexColor('0x0000FF'))
			#if pCdb !=0:	cv.rect(130,217,pCdb,11, fill=1)
			#if pCdb !=0:	cv.drawString((pCdb + 132 ),217,format(nCdb,",")+"%")
			#
			#cv.setFillColor(HexColor('0x800080'))
			#if pBol !=0:	cv.rect(130,202,pBol,11, fill=1)
			#if pBol !=0:	cv.drawString((pBol + 132 ),202,format(nBol,",")+"%")
			#
			#cv.setFillColor(HexColor('0xFF0000'))
			#if pCar !=0:	cv.rect(130,187,pCar,11, fill=1)
			#if pCar !=0:	cv.drawString((pCar + 132 ),187,format(nCar,",")+"%")
			#
			#cv.setFillColor(HexColor('0x90EE90'))
			#if pFin !=0:	cv.rect(130,172,pFin,11, fill=1)
			#if pFin !=0:	cv.drawString((pFin + 132 ),172,format(nFin,",")+"%")
			#
			#cv.setFillColor(HexColor('0xFFC0CB'))
			#if pTic !=0:	cv.rect(130,157,pTic,11, fill=1)
			#if pTic !=0:	cv.drawString((pTic + 132 ),157,format(nTic,",")+"%")
			#
			#cv.setFillColor(HexColor('0x1E90FF'))
			#if pPcr !=0:	cv.rect(130,142,pPcr,11, fill=1)
			#if pPcr !=0:	cv.drawString((pPcr + 132 ),142,format(nPcr,",")+"%")
			#
			#cv.setFillColor(HexColor('0x8B6914'))
			#if pDep !=0:	cv.rect(130,127,pDep,11, fill=1)
			#if pDep !=0:	cv.drawString((pDep + 132 ),127,format(nDep,",")+"%")
			#
			#cv.setFillColor(HexColor('0xC19037'))
			#if pRcl !=0:	cv.rect(130,112,pRcl,11, fill=1)
			#if pRcl !=0:	cv.drawString((pRcl + 132 ),112,format(nRcl,",")+"%")


			del _mensagem
			if Trl == 1: #--: Relatorio geral de vendas { 1-Geral de vendas 2-Geral do resumo }
							
				""" Nova Pagina"""
				pg +=1
				cv.addPageLabel(pg)
				cv.showPage()						
				
				""" F I M """
				separ = se
				lnhsn = ln = 520
				cabvendas(False)
				nRegistro = 0

				lcampo = 515
				ccampo = 525

				cv.setFont('Helvetica', 8)
				for v in rl:

					moT = cc1= cc2= cc3= cc4= cc5= cc6= cc7= cc8= cc9= cc10= cc11= cc12='' 
					dem = drc = hem = hrc = vlp = vlr = ''

					if   rl[v][10] == "2":	moT = "Estornado"
					elif rl[v][10] == "3":	moT = "Cancelado"
					
					if rl[v][7] !=0:	vlp = format(rl[v][7],',')
					if rl[v][9] !=0:	vlr = format(rl[v][9],',')
					if rl[v][3] !=None:	dem = str(rl[v][3].strftime("%d/%m/%Y"))
					if rl[v][5] !=None:	drc = str(rl[v][5].strftime("%d/%m/%Y"))
					
					rec = str(rl[v][2])
					if moT !='':	rec = str(rl[v][2][:10])+' [ '+moT+' ]' 

					if str(rl[v][4]) != '0:00:00':	hem = str(rl[v][4])
					if str(rl[v][6]) != '0:00:00':	hrc = str(rl[v][6])

					if Decimal(rl[v][12]) > 0:	devp = " ("+str(rl[v][12])+")"
					else: devp = ''

					emi = dem+' '+hem+' '+str(rl[v][8])
					rec = drc+' '+hrc+' '+rec+devp

					if rl[v][11] == "1":	cv.setFillColor(blue) #-----------------------: Primeiro dia do periodo e/ou dia atual
					if rl[v][11] == "2":	cv.setFillColor(orange) #---------------------: Dias anterior
					if rl[v][11] == "3":	cv.setFillColor(green) #----------------------: Contas Areceber
					if rl[v][11] == '4' or rl[v][11] == '5':	cv.setFillColor(violet) #-: PgTo c/Credito Devolucao em dinheiro
					if rl[v][11] == '8':	cv.setFillColor(HexColor('0x61C561')) #-------: PgTo c/Credito Devolucao em dinheiro

					if rl[v][1][:4] == "[RA]":	cv.setFillColor(HexColor('0x2D5A2D')) #---: Contas Areceber Lancamento Manual

					if dIni != dFim and rl[v][3] !=None and rl[v][5] !=None and rl[v][3] != rl[v][5]:	cv.setFillColor(red)
					if dIni == dFim and rl[v][3] !=None and rl[v][5] !=None and Inicial == rl[v][3] and rl[v][3] != rl[v][5]:	cv.setFillColor(red)
					
					cv.setFont('Helvetica', 6)
					cv.drawString(22, float(lcampo),str(regis).zfill(5) )
					cv.setFont('Helvetica', 8)
					cv.drawString(42, float(lcampo),str(rl[v][0]) )
					cv.drawString(112,float(lcampo),str(emi) )
					
					cv.drawRightString(315,float(lcampo), vlp )
					cv.drawString(322,float(lcampo),str(rec) )
					cv.drawRightString(565,float(lcampo), vlr )
					cv.drawString(572,float(lcampo),str(rl[v][1]) )
					cv.line(20,(lcampo-2),820,(lcampo-2))
					cv.setFillColor(black)
					
					""" Rodape """
					rd1= rd2= rd3= rd4= rd5= rd6= rd7= rd8= rd9='' 

					regis +=1
					pagin +=1
					lcampo -= 10
					nRegistro +=1
					
					if pagin >= 49: # and nRegistro < vReTorno !='':

						cabvendas(True)

						rd1 = '22|33|110|'+login.identifi+'-'+login.emfantas+' ( Posição de Vendas )|'
						mdl.rodape(cv,rd1,rd2,rd3,rd4,rd5,rd6,rd7,rd8,rd9,6)

						lcampo = 515
						ccampo = 525

						pagin = 1
						pg +=1
						cv.addPageLabel(pg)
						cv.showPage()						
						cabvendas(False)					

				cabvendas(True)
				
				rd1= rd2= rd3= rd4= rd5= rd6= rd7= rd8= rd9='' 
				rd1 = '22|33|110|'+login.identifi+'-'+login.emfantas+' ( Posição de Vendas )|'
				mdl.rodape(cv,rd1,rd2,rd3,rd4,rd5,rd6,rd7,rd8,rd9,6)
										
			""" Salva Arquivo Enviar p/o Gerenciador """
			cv.save()
			gerenciador.Anexar = nomeArquivo

			gerenciador.secund = ''
			gerenciador.emails = ''
			gerenciador.TIPORL = ''
			gerenciador.imprimir = True
			gerenciador.Filial   = Filial
			
			ger_frame=gerenciador(parent=par,id=-1)
			ger_frame.Centre()
			ger_frame.Show()
				

class extrato:
	
	#---------:[ Extrato de Creditos e Debitos ]
	def extratocliente( self, _doc, par, Filial = "", NomeCliente = "", fpagamento = '' ):

		atrasados = False
		if len( login.filialLT[ Filial ][35].split(";") ) >= 78 and login.filialLT[ Filial ][35].split(";")[77] == "T":
			
			incl = wx.MessageDialog(par,"{ Estrato do cliente }\n\nFiltrar apenas titulos vencidos\n"+(" "*130),"Extrato do cliente",wx.YES_NO|wx.NO_DEFAULT)
			if incl.ShowModal() ==  wx.ID_YES:	atrasados = True
		
		def cabvendas():

			""" Cabecalho """
			pag = str(pg).zfill(3)+' ['+str(nPg).zfill(3)+']'
			rls.cabecalhopadrao( cv, ImageReader, dh, pag, Filial, "Extrato do cliente",1)
		
			""" Titulo de Cabecalho """
			cb1= cb2= cb3= cb4= cb5= cb6= cb7= cb8= cb9= cb10= cb11= cb12=''
			rel =  'Usuário: '+str(login.usalogin)
			if nPg == 1:

				cb1 =  "22|687|ORD|"
				cb2 =  "35|687|Nº DAV|"
				cb3 = "102|687|Nº Nota Fiscal|"
				cb4 = "137|687|Lançamento|"
				cb5 = "210|687|Vencimento|"
				cb6 = "255|687|Valor nominal|"
				cb7 = "310|687|Mora-Juros|"
				cb8 = "363|687|Valor final|"
				cb9 = "392|687|Forma de Pagamento|"
			else:

				cb1 =  "22|765|ORD|"
				cb2 =  "35|765|Nº DAV|"
				cb3 = "102|765|Nº Nota Fiscal|"
				cb4 = "137|765|Lançamento|"
				cb5 = "210|765|Vencimento|"
				cb6 = "255|765|Valor nominal|"
				cb7 = "310|765|Mora-Juros|"
				cb8 = "363|765|Valor final|"
				cb9 = "392|765|Forma de Pagamento|"

#				cb1 =  "22|765|ORD|"
#				cb2 =  "35|765|Nº DAV|"
#				cb3 = "102|765|Nº Nota Fiscal|"
#				cb4 = "137|765|Lançamento|"
#				cb5 = "210|765|Vencimento|"
#				cb6 = "255|765|V a l o r|"
#				cb7 = "310|765|Forma de Pagamento|"

			mdl.mtitulo(rel,cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12,5,1)

		def separar():
			
			cv.line(35,float(ccampo),35,float(lcampo))
			cv.line(102,float(ccampo),102,float(lcampo))
			cv.line(135,float(ccampo),135,float(lcampo))
			cv.line(210,float(ccampo),210,float(lcampo))
			cv.line(255,float(ccampo),255,float(lcampo))
			cv.line(300,float(ccampo),300,float(lcampo))
			cv.line(340,float(ccampo),340,float(lcampo))
			cv.line(390,float(ccampo),390,float(lcampo))

			cv.line(20,float(lcampo),570,float(lcampo))
		
		if _doc == '':
			
			alertas.dia(par,"Nº CNPJ-CPF vazio, cliente não cadastrado...\n"+(" "*80),"Extrator do Cliente")			
			return
			
			
		sald = formasPagamentos()
		T    = truncagem()
		mdl  = modelo()

		conn = sqldb()
		sql  = conn.dbc("Extrato do cliente", fil = Filial, janela = par )

		_sal = Decimal('0.00')
		_cad = Decimal('0.00')
		_dAT = datetime.datetime.now().strftime("%Y/%m/%d")
		hoje = datetime.datetime.now().date()
		
		dh   = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
		pg   = 1

		if sql[0] == True:

			_ccc,_deb = sald.saldoCC(sql[2],str(_doc))

			_sal = ( _ccc - _deb )
			_cad,_atraso = sald.saldoRC( sql[2], str(_doc), _dAT, Filial )

			pesq = "SELECT rc_ndocum,rc_apagar,rc_formap,rc_formap,rc_dtlanc,rc_hslanc,rc_clnome,rc_vencim,rc_nparce,rc_notafi,rc_indefi FROM receber WHERE rc_cpfcnp='"+_doc+"' and rc_status='' ORDER BY rc_vencim"
		
			if fpagamento and fpagamento.split('-')[0]:	pesq = pesq.replace("WHERE","WHERE rc_formap='"+str( fpagamento )+"' and")

			soma = sql[2].execute( pesq )
			rece = sql[2].fetchall()

			conn.cls(sql[1])
			nfl = []
			if rece !=None:

				""" Pegar o numero de registros """
				numeroReg = 0
				TAreceber = juros_mora = Decimal('0.00')
				
				_v02 = _v03 = _v06 = _v07 = _v11 = _v12 = Decimal('0.00')

				
				for f in login.ciaRelac:
					
					if f.split('-')[0] !="":
						
						vfl = Decimal("0.00")
						
						for c in rece:

							continuar = True
							if atrasados == True and c[7] > hoje:	continuar = False
							if c[10] == f.split('-')[0] and continuar:
								
								if c[3][:2] in ['02','03','06','07','11','12']:	vfl +=c[1]
						
						if vfl !=0:	nfl.append( str( login.filialLT[ f.split('-')[0] ][14].title() )+";"+format(vfl,',') )
					
				for i in rece:

					continuar = True
					if atrasados == True and i[7] > hoje:	continuar = False
					
					if i[3][:2] in ['02','03','06','07','11','12'] and continuar:

						"""  Calculo de mora-juros  """
						__ap, __jm = self.calcularJurosMora( i, Filial, T )
						if __jm:	juros_mora += __jm
						"""" //--------------------------------------// """

						numeroReg +=1
						TAreceber += ( i[1] + __jm )

						if i[3][:2] == "02":	_v02 += __ap # Decimal( i[1] )
						if i[3][:2] == "03":	_v03 += __ap # Decimal( i[1] )
						if i[3][:2] == "06":	_v06 += __ap # Decimal( i[1] )
						if i[3][:2] == "07":	_v07 += __ap # Decimal( i[1] )
						if i[3][:2] == "11":	_v11 += __ap # Decimal( i[1] )
						if i[3][:2] == "12":	_v12 += __ap # Decimal( i[1] )

				cli = "{ "+str( _doc )+" } " + NomeCliente
				
				nPg  = 1

				if numeroReg >= 63 and numeroReg <= 69:	nPg = 2
				else:	

					nPg = T.trunca(3,( Decimal(numeroReg) / Decimal('69') ) )
				
					if      str(nPg).split('.')[0] != "1" and str(nPg).split('.')[1][:2] == "00":	nPg = int(nPg)
					else:	nPg = ( int(nPg) + 1 )

				nomeArquivo = diretorios.usPasta+"ext_"+login.usalogin.lower()+".pdf"

				""" Abertura do Arquivo """
				cv = canvas.Canvas(nomeArquivo, pagesize=A4)
				
				""" Cabecalho """
				cabvendas()

				cv.setFont('Helvetica-Bold', 8)	
				cv.drawString(22,740,"Extrato do cliente: "+ cli )

				""" Totalizacao do Contas AReceber e Conta Corrente """
				cv.setFont('Helvetica', 7)	
				cv.drawString(22,720,"a - Saldo Conta Corrente:")
				if _sal > 0:	cv.drawRightString(150,720,format(_sal,','))

				if _cad > 0:	cv.setFillColor(HexColor('0x9E2F2F'))
				cv.drawString(22,710,"b - AReceber Vencidos:")
				if _cad > 0:	cv.drawRightString(150,710,format(_cad,','))
				if _cad > 0:	cv.setFillColor(HexColor('0x1A1A1A'))

				cv.drawString(22,700,"c - Total Areceber:")
				cv.drawRightString(150,700,format(TAreceber,','))
				
				cv.drawString(180,720,"Mora-Juros:")
				cv.drawString(180,710,"Saldo ( a - b ):")
				cv.drawRightString(270,720,format(juros_mora,','))
				
				if ( _sal - _cad ) < 0:

					cv.setFillColor(HexColor('0x9E2F2F'))
					cv.drawRightString(270,710,"( "+format(( _sal - _cad ),',')+" )")

				else:	cv.drawRightString(270,710,format(( _sal - _cad ),','))
				cv.setFillColor(HexColor('0x1A1A1A'))

				cv.drawString(180,700,"Nº Paginas:")
				cv.drawRightString(230,700,str(nPg))

				""" Totalizacao """
				cv.drawString(335,720,"Cheque Avista:")
				cv.drawString(335,710,"Cheque Predatado:")
				cv.drawString(335,700,"Boleto:")
				cv.drawString(455,720,"Carteira:")
				cv.drawString(455,710,"Deposito em Conta:")
				cv.drawString(455,700,"Receber no Local:")

				cv.setFillColor(HexColor('0x4D4D4D'))
				if _v02 > 0:	cv.drawRightString(450,720,format( _v02, ',' ) )
				if _v03 > 0:	cv.drawRightString(450,710,format( _v03, ',' ) )
				if _v06 > 0:	cv.drawRightString(450,700,format( _v06, ',' ) )
				if _v07 > 0:	cv.drawRightString(568,720,format( _v07, ',' ) )
				if _v11 > 0:	cv.drawRightString(568,710,format( _v11, ',' ) )
				if _v12 > 0:	cv.drawRightString(568,700,format( _v12, ',' ) )
				cv.setFillColor(HexColor('0x1A1A1A'))
				
				cv.line(20,695,570,695)
				cv.line(20,685,570,685)

				""" Impressao no PDF """
				regis  = 1
				pagin  = 1
				lcampo = 675
				ccampo = 685
				hoje   = datetime.datetime.now().date()

				"""  Totaliza Filias  """
				if nfl !=[]:

					colunas = 210
					for svlT in nfl:
						
						cv.setFont('Helvetica', 6)	
						cv.drawRightString(colunas,40,svlT.split(";")[0]+": "+svlT.split(";")[1])
						cv.setFont('Helvetica', 7)	
						colunas +=90

				for i in rece:

					continuar = True
					if atrasados == True and i[7] > hoje:	continuar = False

					if continuar:
						
						if i[3][:2] == '02' or i[3][:2] == '03' or i[3][:2] == '06' or i[3][:2] == '07' or i[3][:2] == '11' or i[3][:2] == '12':

							dias   = ""
							atraso = ( hoje - i[7] ).days
							if atraso > 0:	dias = "Atraso: "+str(atraso)+" dias"

							cv.setFont('Helvetica', 7)	
							
							cv.drawString(22,float(lcampo),str(regis).zfill(3))
							cv.drawString(37,float(lcampo),str(i[0])+'/'+str(i[8]).zfill(2))
							cv.drawString(105,float(lcampo),str(i[9]))
							cv.drawString(140,float(lcampo),str(i[4].strftime("%d/%m/%Y"))+"  "+str(i[5]))
							cv.drawString(215,float(lcampo),str(i[7].strftime("%d/%m/%Y")))
							cv.drawRightString(298,float(lcampo),format(i[1],','))

							"""  Calculo de mora-juros  """
							__ap, __jm = self.calcularJurosMora( i, Filial, T )
							"""" //--------------------------------------// """
	
							cv.drawRightString(338,float(lcampo),format( __jm, ',' ) )
							cv.drawRightString(388,float(lcampo),format( __ap, ',' ))

							cv.drawString(392,float(lcampo),str(i[3]))

							cv.setFillColor(HexColor('0x9E2F2F'))
							cv.drawString(470,float(lcampo),dias)
							cv.setFillColor(HexColor('0x1A1A1A'))
							cv.setFont('Helvetica', 5)	
							cv.drawString(550,float(lcampo),str(i[10]))
							cv.setFont('Helvetica', 7)	
							if regis < numeroReg:	cv.line(20,float(lcampo-3),570,float(lcampo-3))
							
							regis  += 1
							pagin  += 1
							lcampo -= 10

							sp = False
							if pg == 1 and pagin >= 64:	sp = True
							elif pg > 1 and pagin >=69:	sp = True
							if sp == True:

								rd1= rd2= rd3= rd4= rd5= rd6= rd7= rd8= rd9='' 
								rd1 = '22|33|110|'+login.identifi+'-'+login.emfantas+' ( Extrato do cliente )|'
								mdl.rodape(cv,rd1,rd2,rd3,rd4,rd5,rd6,rd7,rd8,rd9,6)

								separar()
								pagin  = 1
								ccampo = 750
								lcampo = 740

								pg +=1
								cv.addPageLabel(pg)
								cv.showPage()						
								cabvendas()

				rd1= rd2= rd3= rd4= rd5= rd6= rd7= rd8= rd9='' 
				rd1 = '22|33|110|'+login.identifi+'-'+login.emfantas+' ( Extrato do cliente )|'
				mdl.rodape(cv,rd1,rd2,rd3,rd4,rd5,rd6,rd7,rd8,rd9,6)
					
				separar()

				""" Salva Arquivo Enviar p/o Gerenciador """
				cv.save()
				gerenciador.TIPORL = ''
				gerenciador.Anexar = nomeArquivo
				gerenciador.imprimir = True
				gerenciador.Filial   = Filial

				ger_frame=gerenciador(parent=par,id=-1)
				ger_frame.Centre()
				ger_frame.Show()

	def calcularJurosMora(self, r, filial, T ):

		"""  Calculo dos juros mora  """
		mora_juros = Decimal("0.00")
		
		hoje   = datetime.datetime.now().date()
		posica = ['02','03','06','07','11','12']
		apagar = r[1]

		if r[2][:2] in posica:

			"""  Taxa de Juros Mensal   """
			TaxaDiaria = Decimal( "0.00" )
			multa_venc = Decimal( "0.00" )
			if len( login.filialLT[ filial ][35].split(";") ) >=39 and Decimal( login.filialLT[ filial ][35].split(";")[38] ) !=0:	TaxaDiaria = ( Decimal( login.filialLT[ filial ][35].split(";")[38] ) / Decimal(30) )
			if len( login.filialLT[ filial ][35].split(";") ) >=96 and Decimal( login.filialLT[ filial ][35].split(";")[95] ) !=0:	multa_venc = Decimal( login.filialLT[ filial ][35].split(";")[95] ) 

			atraso = ''
			moraju = ''
			vmulta = ''
			cJuros = ["02","03","06","07","12"]
			#			pesq = "SELECT rc_ndocum,rc_apagar,rc_formap,rc_formap,rc_dtlanc,rc_hslanc,rc_clnome,rc_vencim,rc_nparce,rc_notafi,rc_indefi FROM receber WHERE rc_cpfcnp='"+_doc+"' and rc_status='' ORDER BY rc_vencim"

			if hoje > r[7]:	atraso = ( hoje - r[7] ).days
			if atraso and r[2][:2] in cJuros:

			#-------------:[ Cobranca de Juros ]
				moraju  = Decimal('0.00')
				moraju = T.arredonda( 2, ( ( ( r[1] * TaxaDiaria ) / 100 ) * atraso  ) )
				vmulta = T.arredonda( 2, ( ( r[1] * multa_venc ) / 100 ) )
				apagar   += moraju + vmulta
				
				mora_juros = moraju + vmulta
				moraju    = format( moraju,',' )
				vmulta    = format( vmulta,',' )

		return apagar, mora_juros
		
	#---------:[ Extrato de Conta Correne do Cliente ]
	def extratoConta( self, _doc, dI, dF, par, Filial = '' ):

		def cabvendas():

			""" Cabecalho """
			pag = str(pg).zfill(3)+' ['+str( nPg ).zfill(3)+']'
			rls.cabecalhopadrao( cv, ImageReader, dh, pag,Filial, "Extrato conta corrente",1)
		
			""" Titulo de Cabecalho """
			cb1= cb2= cb3= cb4= cb5= cb6= cb7= cb8= cb9= cb10= cb11= cb12=''
			rel =  'Usuário: '+str(login.usalogin)+(' '*10)+"Período: "+datetime.datetime.strptime(dI.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")+" A "+datetime.datetime.strptime(dF.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			cb1 =  "22|765|Registro|"
			cb2 =  "62|765|Lançamento|"
			cb3 = "202|765|Crédito-Débito|"
			cb4 = "280|765|Saldo|"
			cb5 = "307|765|Filial|"
			cb6 = "330|765|Histórico|"
			
			mdl.mtitulo(rel,cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12,7,1)

		def separar():
			
			cv.line(60,float(ccampo),60,float(lcampo))
			cv.line(200,float(ccampo),200,float(lcampo))
			cv.line(252,float(ccampo),252,float(lcampo))
			cv.line(304,float(ccampo),304,float(lcampo))
			cv.line(328,float(ccampo),328,float(lcampo))
			cv.line(20,float(lcampo),570,float(lcampo))
			
		
		sald = formasPagamentos()
		mdl  = modelo()

		conn = sqldb()
		sql  = conn.dbc("Extrato do conta corrente", fil = Filial, janela = par )

		_sal = Decimal('0.00')
		_cad = Decimal('0.00')
		_dAT = datetime.datetime.now().strftime("%Y/%m/%d")


		dIni = datetime.datetime.strptime(dI.FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
		dFim = datetime.datetime.strptime(dF.FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
		hoje = format(datetime.datetime.now(),'%Y/%m/%d')

		cIni = datetime.datetime.strptime(dI.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
		cFim = datetime.datetime.strptime(dF.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
		dh   = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
		
		dh   = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
		pg   = 1

		if sql[0] == True and _doc !='':

			_ccc,_deb = sald.saldoCC(sql[2],str(_doc))

			_sal = ( _ccc - _deb )
			_cad,_atraso = sald.saldoRC( sql[2], str( _doc ), _dAT, Filial )


			conta = "SELECT * FROM conta WHERE cc_lancam >='"+dIni+"' and cc_lancam <='"+dFim+"' and cc_docume='"+_doc+"'"

			soma = sql[2].execute( conta )
			rece = sql[2].fetchall()
			conn.cls( sql[1] )

			if soma !=0:

				cli  = rece[0][9]
				if _doc[:3] == "DEV":	cli = "Ticket: "+_doc
				soma += 5
				nPg  = 1
				if soma >= 63 and soma <= 69:	nPg = 2
				else:	

					nPg = ( Decimal(soma) / Decimal('69') )

					if      str(nPg) != "1" and str(nPg).split('.')[1][:2] == "00":	nPg = int(nPg)
					else:	nPg = ( int(nPg) + 1 )

				nomeArquivo = diretorios.usPasta+"ext_"+login.usalogin.lower()+".pdf"

				""" Abertura do Arquivo """
				cv = canvas.Canvas(nomeArquivo, pagesize=A4)
				
				""" Cabecalho """
				cabvendas()

				cv.setFont('Helvetica-Bold', 8)	
				cv.drawString(22,740,"Conta Corrente { Extrato }: "+str( cli ))

				""" Totalizacao do Contas AReceber e Conta Corrente """
				cv.setFont('Helvetica', 7)

				cv.drawString(22,730,"Total de créditos:")
				cv.drawRightString(150,730,format(_ccc,','))

				cv.drawString(22,720,"Total de cébitos:")
				cv.drawRightString(150,720,format(_deb,','))

				if _sal > 0:	cv.setFillColor(blue)
				else:	cv.setFillColorRGB (1,0,0.30 )

				cv.drawString(22,710,"Saldo na conta corrente:")
				cv.drawRightString(150,710,format(_sal,','))

				cv.setFillColor(black)
				cv.drawString(22,700,"Nº Paginas:")
				cv.drawRightString(150,700,str(nPg))

				cv.drawString(459,700,"Período:")
				cv.drawRightString(567,700,datetime.datetime.strptime(dI.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")+" A "+datetime.datetime.strptime(dF.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y"))

				cv.line(20,695,570,695)
				
				regis  = 1
				pagin  = 1
				lcampo = 685
				ccampo = 695
				
				for i in rece:
					
					cv.setFont('Helvetica', 7)	

					if i[14] > 0:	cv.setFillColor(blue)
					if i[15] > 0:	cv.setFillColorRGB (1,0,0.30 )
		
					cv.drawString(22,float(lcampo),str(i[0]).zfill(8))
					cv.drawString(62,float(lcampo),str(i[1].strftime("%d/%m/%Y"))+' '+str(i[2])+' '+str(i[4]))
					if i[14] > 0:	cv.drawRightString(250,float(lcampo),format(i[14],','))
					if i[15] > 0:	cv.drawRightString(250,float(lcampo),format(i[15],','))

					if i[16] >= 0:	cv.setFillColor(blue)
					else:	cv.setFillColorRGB (1,0,0.30 )
					cv.drawRightString(302,float(lcampo),format(i[16],','))

					cv.setFillColor(black)
					cv.setFont('Helvetica', 6)
					
					
					Historico = i[7]+' {'+str(i[12])+'} '+i[13]
					cv.drawString(307,float(lcampo),i[6])
					cv.drawString(330,float(lcampo),Historico)
						
					regis  += 1
					pagin  += 1
					lcampo -= 10

					sp = False
					if pg == 1 and pagin >= 64:	sp = True
					elif pg > 1 and pagin >=69:	sp = True
					if sp == True:

						rd1= rd2= rd3= rd4= rd5= rd6= rd7= rd8= rd9='' 
						rd1 = '22|33|110|'+login.identifi+'-'+login.emfantas+' ( Conta Corrente: Extrato do cliente )|'
						mdl.rodape(cv,rd1,rd2,rd3,rd4,rd5,rd6,rd7,rd8,rd9,6)

						separar()
						pagin  = 1
						ccampo = 750
						lcampo = 740

						pg +=1
						cv.addPageLabel(pg)
						cv.showPage()						
						cabvendas()

				rd1= rd2= rd3= rd4= rd5= rd6= rd7= rd8= rd9='' 
				rd1 = '22|33|110|'+Filial+' ( Conta Corrente: Extrato do cliente )|'
				mdl.rodape(cv,rd1,rd2,rd3,rd4,rd5,rd6,rd7,rd8,rd9,6)
					
				separar()

				""" Salva Arquivo Enviar p/o Gerenciador """
				cv.save()
				gerenciador.TIPORL = ''
				gerenciador.Anexar = nomeArquivo
				gerenciador.imprimir = True
				gerenciador.Filial   = Filial

				ger_frame=gerenciador(parent=par,id=-1)
				ger_frame.Centre()
				ger_frame.Show()
				
			else:	alertas.dia(par,"Não consta lançamento para o documento, "+str(_doc),"Extrator do Cliente")

		
class recibo:
	
	def recibocliente(self,cld,vlr,vlrext,ref,ema,par,_vd,_vc, Filial = "" ):

		def cabvendas():

			""" Cabecalho """
			pag = str(pg).zfill(3)
			rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"R E C I B O",1)
		
			""" Titulo de Cabecalho """
			cb1= cb2= cb3= cb4= cb5= cb6= cb7= cb8= cb9= cb10= cb11= cb12='' 
			rel =  'Usuário: '+str(login.usalogin)
			cb1 =  "22|765|[< R E C I B O >]|"
			mdl.mtitulo(rel,cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12,7,1)

		def separar():
			
			cv.line(85,float(ccampo),85,float(lcampo))
			cv.line(170,float(ccampo),170,float(lcampo))
			cv.line(255,float(ccampo),255,float(lcampo))
			cv.line(20,float(lcampo),570,float(lcampo))
			
		mdl    = modelo()
		Trunca = truncagem()
		valor  = format(Trunca.trunca(3, Decimal( vlr ) ),',')
		vlrTo  = format(Trunca.trunca(3, Decimal( _vd ) ),',')
		vlrcc  = format(Trunca.trunca(3, Decimal( _vc ) ),',')
		
		dh   = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
		pg   = 1

		nomeArquivo = diretorios.usPasta+"rec_"+login.usalogin.lower()+".pdf"

		""" Abertura do Arquivo """
		cv = canvas.Canvas(nomeArquivo, pagesize=A4)
				
		""" Cabecalho """
		cabvendas()

		limTe = 0
		cv.line(20,( 580-30 ),570,( 580-30 ) )
		cv.drawString(22,552,"2ª -Via-")
		for x in range(2):
			
			if x==1: limTe = 220
			cv.setFont('Helvetica-Bold', 8)	
			cv.drawString(22, ( 740-limTe ),u"Recibo referente a crédito(s) de compras")
			cv.drawString(22, ( 730-limTe ),"Valor: R$ "+format(Trunca.trunca(3, Decimal( vlr ) ),','))
			cv.drawString(22, ( 710-limTe ),"Cliente: "+ cld )
			cv.drawString(300,( 710-limTe ),u"Referência: "+ref)

			TexTo1 = "Recebi(emos) de "+str(login.filialLT[login.identifi][1])
			TexTo2 = "a importancia de R$ "+valor+" ("+ vlrext +")"
			TexTo3 = "referente a creditos de compras, "+ref

			cv.drawString(70,( 680-limTe ),TexTo1)
			cv.drawString(50,( 670-limTe ),TexTo2)
			cv.drawString(50,( 660-limTe ),TexTo3)
			cv.line(50,( 630-limTe ),320,( 630-limTe ))
			cv.drawString(50,( 620-limTe ),"Cliente:             "+ cld )
			cv.drawString(50,( 610-limTe ),"Recebimento: "+str(dh))

			cv.line(20,( 580-limTe ),570,( 580-limTe ) )
			cv.setFont('Helvetica', 6)	

			cv.rect(465,( 585-limTe ),100,30, fill=0)
			cv.drawString(467,( 608-limTe ),"Valor total:")
			cv.drawString(467,( 598-limTe ),"Valor devolvido:")
			cv.drawString(467,( 588-limTe ),"Transferido p/cc:")
			
			cv.drawRightString(563,( 608-limTe ),vlrTo)
			cv.drawRightString(563,( 598-limTe ),valor)
			cv.drawRightString(563,( 588-limTe ),vlrcc)
				
		lcampo = 685
		ccampo = 695
		cv.setFont('Helvetica', 7)	

		rd1= rd2= rd3= rd4= rd5= rd6= rd7= rd8= rd9='' 
		rd1 = '22|33|110|'+login.identifi+'-'+login.emfantas+' ( Recibo de Devolução de Mercadorias )|'
		mdl.rodape(cv,rd1,rd2,rd3,rd4,rd5,rd6,rd7,rd8,rd9,6)

		cv.addPageLabel(pg)
		cv.showPage()						
					
		""" Salva Arquivo Enviar p/o Gerenciador """
		cv.save()

		gerenciador.TIPORL = ''
		gerenciador.Anexar = nomeArquivo
		gerenciador.emails = ema
		gerenciador.imprimir = True
		gerenciador.Filial   = Filial

		ger_frame=gerenciador(parent=par,id=-1)
		ger_frame.Centre()
		ger_frame.Show()

class relcompra:
	
	def compras( self, par, pedido, TP, Filiais = "", email = True, mostrar = True ):

		def cabcompra():

			""" Cabecalho """
			pag = str(pg).zfill(3)
			_pd = "COMPRAS"
			
			if TP == "2":	_pd = "ACERTO ESTOQUE"	
			if TP == "3":	_pd = "DEVOLUÇÃO RMA"	
			if TP == "4":	_pd = "TRANSFERÊNCIA"	
			if TP == "5":	_pd = "ORÇAMENTO"	
			
			rls.cabecalhopadrao( cv, ImageReader, dh, pag, Filiais, _pd, 2)
		
			""" Titulo de Cabecalho """
			cb1= cb2= cb3= cb4= cb5= cb6= cb7= cb8= cb9= cb10= cb11= cb12='' 
			rel =  "Fornecedor: "+fr+(" "*20)+" Usuário: "+str( login.usalogin )
			
			if int( pag ) > 1:

				cb1  =   "22|540|ITEM|"
				cb2  =   "44|540|Código|"
				cb3  =  "117|540|Referência|"
				cb4  =  "202|540|Descrição dos Produtos|"
				cb5  =  "468|540|Endereco  Fabricante|"
				cb6  =  "582|540|Quantidade|"
				cb7  =  "632|540|UN|"
				cb8  =  "652|540|Preço Unitario|"
				cb9  =  "712|540|Valor Total|"
				cb10 =  "770|540|Preço Custo|"
			
			elif int( pag ) == 1:
				
				cb1  =   "22|482|ITEM|"
				cb2  =   "44|482|Código|"
				cb3  =  "117|482|Referência|"
				cb4  =  "202|482|Descrição dos Produtos|"
				cb5  =  "468|482|Endereco  Fabricante|"
				cb6  =  "582|482|Quantidade|"
				cb7  =  "632|482|UN|"
				cb8  =  "652|482|Preço Unitario|"
				cb9  =  "712|482|Valor Total|"
				cb10 =  "770|482|Preço Custo|"
			
			mdl.mtitulo(rel,cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12,7,2)
			""" Cor de fundo no cabecalho de Titulos """
			cv.setFillGray(0.1,0.1) 
			if int(pag) == 1:	cv.rect(20,480,800,10, fill=1)
			if int(pag)  > 1:	cv.rect(20,535,800,15, fill=1)
			cv.setFillColor(HexColor('0x000000'))

		def separar():
			
			cv.line(42, float(ccampo), 42,float(lcampo+7))
			cv.line(115,float(ccampo),115,float(lcampo+7))
			cv.line(200,float(ccampo),200,float(lcampo+7))
			cv.line(500,float(ccampo),500,float(lcampo+7))
			cv.line(580,float(ccampo),580,float(lcampo+7))
			cv.line(630,float(ccampo),630,float(lcampo+7))
			cv.line(650,float(ccampo),650,float(lcampo+7))
			cv.line(710,float(ccampo),710,float(lcampo+7))
			cv.line(768,float(ccampo),768,float(lcampo+7))
			
		""" Buscar dados da compra """

		emai = listaemails()
		conn = sqldb()
		sql  = conn.dbc("Compras: Lista de pedidos", fil = Filiais, janela = par )
		cnt  = True
		
		if sql[0] == True:	

			#--------------: Controle de compras
			cmpa = sql[2].execute("SELECT *  FROM ccmp WHERE cc_contro='"+str( pedido )+"'")
			self.cm = sql[2].fetchall()
			
			#--------------: Itens de compras
			item = sql[2].execute("SELECT *  FROM iccmp WHERE ic_contro='"+str( pedido )+"'")
			self.it = sql[2].fetchall()
			
			#--------------: Lista de emails do fornecedor
			if cmpa !=0:	emails = emai.fremail( self.cm[0][1], sql[2] )
			else:	emails = ""

			#conn.cls(sql[1])

			if item == 0 or  cmpa == 0:	alertas.dia(par,u"Pedido de controle nº "+str( pedido )+u", não localizado !!\n"+(' '*100),"Compras: Relatorio")
			if item != 0 and cmpa != 0:

				mdl = modelo()
				Tru = truncagem()

				dh  = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
				pg  = 1
				nf  = str(self.cm[0][6])
				em  = str(self.cm[0][7])+' '+str(self.cm[0][8])
				fr  = str(self.cm[0][2])

				nomeArquivo = diretorios.usPasta+"rec_"+login.usalogin.lower()+".pdf"

				""" Abertura do Arquivo """
				cv = canvas.Canvas(nomeArquivo, pagesize=landscape(A4))
						
				""" Cabecalho """
				cabcompra()

				#------------: Confeccao do relatorio
				Tpedido = "Pedido de compra:"
				if TP == "2":	Tpedido = "Acerto de Estoque:"
				if TP == "5":	Tpedido = "Cotação-Orçamento:"
				cv.setFont('Helvetica', 8)
				cv.drawString(22,515,Tpedido)
				cv.drawString(22,505,"Nome do Fornecedor:")
				cv.drawString(22,495,"Emissão-NFe-DANFE:")

				cv.drawString(500,515,"Emissão: ")
				cv.drawString(500,505,"Usuário: ")
				cv.drawString(500,495,"Nº Items:")

				if TP == "4":
					
					if not self.cm[0][51].strip():

						cv.setFont('Helvetica-Bold', 9)
						cv.setFillColor(HexColor('0xA52A2A'))
						cv.drawString(605,540,"Aguardando aceite da filiali de destino [ "+str( self.cm[0][49] )+" ]")

					if self.cm[0][51].strip():

						cv.setFont('Helvetica-Bold', 9)
						cv.setFillColor(HexColor('0xA52A2A'))
						cv.drawString(605,540,"ACEITE:  [ "+str( self.cm[0][51] )+" ]")

					cv.setFont('Helvetica-Bold', 9)
					cv.setFillColor(HexColor('0x127D12'))
					cv.drawString(22,540,"Filial Origem: [ "+str( self.cm[0][48] )+" ]>---: Destino: [ "+str( self.cm[0][49] )+" ]")
					cv.setFillColor(HexColor('0x000000'))

				cv.drawString(537,515,format(self.cm[0][7],"%d-%m-%Y")+"  "+str(self.cm[0][8]))
				cv.drawString(537,505,self.cm[0][9])
				cv.drawString(537,495,str(len(self.it)))
				
				cv.drawString(110,515,pedido)
				cv.drawString(110,505,fr)
				
				dadEmi = ""
				if self.cm[0][10] !=None and str( self.cm[0][10] ).upper() !="NONE":	dadEmi = format(self.cm[0][10],"%d-%m-%Y")
				cv.drawString( 110, 495, str(dadEmi)+"  "+str(self.cm[0][6])+"  "+str(self.cm[0][5]))
				
				cv.line(20,490,820,490)
				cv.line(20,480,820,480)

				""" Rodape """
				if TP == "5":

					rd1= rd2= rd3= rd4= rd5= rd6= rd7= rd8= rd9='' 
					if TP == '5':	rd1 = '22|33|110|'+login.identifi+'-'+login.emfantas+' ( Pedido de cotação - Orçamento )|'
					mdl.rodape(cv,rd1,rd2,rd3,rd4,rd5,rd6,rd7,rd8,rd9,7)

				lcampo = 470
				ccampo = 480
				linhas = 4
				ordems = 1

				cv.setFont('Helvetica', 8)

				for i in self.it:

					valor = format(Tru.trunca(3, Decimal( i[11] ) ),',')
					subto = format(Tru.trunca(3, Decimal( i[12] ) ),',')
					custo = format(Tru.trunca(3, Decimal( i[48] ) ),',')
					quant = str( format(i[10],',') )

					codigo_endereco = i[59] 
					filial_endereco = i[75]
					endereco_estoque = ""

					if sql[2].execute("SELECT ef_endere FROM estoque WHERE ef_codigo='"+ codigo_endereco +"' and ef_idfili='"+ filial_endereco+"'"):	endereco_estoque = sql[2].fetchone()[0]
					if not endereco_estoque and sql[2].execute("SELECT pd_ende FROM produtos WHERE pd_codi='"+ codigo_endereco +"'"):	endereco_estoque = sql[2].fetchone()[0]
					
					if TP == "5" and Filiais and len( login.filialLT[ Filiais ][35].split(";") ) >= 67 and login.filialLT[ Filiais ][35].split(";")[66] == "T":	custo = valor = subto = ""
					
					ds2 = vi2 ='' 
					ds1 = i[6]
					vi1 = i[50]
					if len(i[6]) > 60:
						
						ds1 = i[6][:60]
						ds2 = i[6][60:]

					if len(i[50]) > 60:
						
						vi1 = i[50][:60]
						vi2 = i[50][60:]
						
					ajqtd = str(i[10]).split('.')
					if int( ajqtd[1] ) == 0:	quant = ajqtd[0]
		
					cv.drawString(22,float(lcampo),str(ordems).zfill(3))
					cv.drawString(44,float(lcampo),str(i[59]))
					cv.drawString(117,float(lcampo),str(i[4]))
					cv.setFont('Helvetica', 7)
					cv.drawString(202,float(lcampo),ds1)
					cv.drawRightString(499,float(lcampo),endereco_estoque)
							
					cv.setFillColor(HexColor('0x4D4D4D'))
					cv.setFont('Helvetica', 6)
					cv.drawString(502,float(lcampo),str(i[46]))

					cv.setFillColor(HexColor('0x1A1A1A'))
					cv.setFont('Helvetica', 8)

					cv.drawRightString(628,float(lcampo),quant)
					if TP == "2":	cv.drawString(582,float(lcampo),i[66])

					"""  no atccdd veio unidade com codificacao diferente e nao conseguia abrir o pdf  """
					try:	cv.drawRightString(646,float(lcampo),i[9][:2])
					except Exception as __er:	cv.drawRightString(646,float(lcampo),"UN")
					if mostrar:
						
						cv.drawRightString(708,float(lcampo),valor)
						cv.drawRightString(766,float(lcampo),subto)
						cv.drawRightString(818,float(lcampo),custo)

					if ds2 != '':
						
						linhas +=1
						lcampo -=10
						cv.drawString(202,float(lcampo),ds2)
					
					if vi1 !='':

						linhas +=1
						lcampo -=10
						cv.setFillColor(HexColor('0x7F7F7F'))
						cv.drawString(44,float(lcampo),str(i[59]))
						cv.drawString(117,float(lcampo),"{ Vinculado }")
						cv.drawString(202,float(lcampo),vi1)
						
						if i[49] !=0:	cv.drawRightString(628,float(lcampo),str(i[49]))
						if i[57] !=0:	cv.drawRightString(708,float(lcampo),str(i[57]))
						if i[60] !=0:	cv.drawRightString(766,float(lcampo),str(i[60]))
						cv.setFillColor(HexColor('0x1A1A1A'))

					if vi2 !='':

						linhas +=1
						lcampo -=10
						cv.setFillColor(HexColor('0x7F7F7F'))
						cv.drawString(202,float(lcampo),vi2)
						cv.setFillColor(HexColor('0x1A1A1A'))
	
					cv.line(20,float(lcampo-3),820,float(lcampo-3))
					
					linhas +=1
					ordems +=1
					lcampo -=10
					
					if linhas >= 47:

						separar()
						""" Rodape """
						rd1= rd2= rd3= rd4= rd5= rd6= rd7= rd8= rd9='' 
						rd1 = '22|33|110|'+login.identifi+'-'+login.emfantas+' '+Tpedido+'|'
						mdl.rodape(cv,rd1,rd2,rd3,rd4,rd5,rd6,rd7,rd8,rd9,7)

						lcampo = 515
						ccampo = 525
						linhas = 4
						ordems = 1

						pg +=1
						cv.addPageLabel(pg)
						cv.showPage()						
						cabcompra()

						if TP == "4":
							
							if not self.cm[0][51].strip():

								cv.setFont('Helvetica-Bold', 9)
								cv.setFillColor(HexColor('0xA52A2A'))
								cv.drawString(605,540,"Aguardando aceite da filiali de destino [ "+str( self.cm[0][49] )+" ]")

							if self.cm[0][51].strip():

								cv.setFont('Helvetica-Bold', 9)
								cv.setFillColor(HexColor('0xA52A2A'))
								cv.drawString(605,540,"ACEITE:  [ "+str( self.cm[0][51] )+" ]")

							cv.setFont('Helvetica-Bold', 9)
							cv.setFillColor(HexColor('0x127D12'))
							cv.drawString(22,540,"Filial Origem: [ "+str( self.cm[0][48] )+" ]>---: Destino: [ "+str( self.cm[0][49] )+" ]")
							cv.setFillColor(HexColor('0x000000'))

				conn.cls(sql[1])

				""" Totalização """
				if TP !="5":

					cv.setFont('Helvetica', 8)
					cv.setFillColor(HexColor('0x7F7F7F'))
					cv.drawString(22,34, "ST Fora: ")
					cv.drawString(22,24, "Seguro: ")
					cv.drawString(120,34,"Despesas ACS: ")
					cv.drawString(230,34,"Frete: ")
					cv.drawString(330,34,"Frete Avulso: ")
					cv.drawString(330,24,"Total ICMS: ")
					cv.drawString(120,24,"Desconto: ")
					cv.drawString(230,24,"Total NF: ")
					cv.drawRightString(110,34,format(self.cm[0][33],','))
					cv.drawRightString(110,24,format(self.cm[0][38],','))
					cv.drawRightString(220,34,format(self.cm[0][39],','))
					cv.drawRightString(220,24,format(self.cm[0][35],','))
					cv.drawRightString(320,34,format(self.cm[0][18],','))
					cv.drawRightString(420,24,format(self.cm[0][15],','))
					cv.drawRightString(320,24,format(self.cm[0][40],','))
					cv.drawRightString(420,34,format(self.cm[0][34],','))

				sair_custos = False if TP == "5" and Filiais and len( login.filialLT[ Filiais ][35].split(";") ) >= 67 and login.filialLT[ Filiais ][35].split(";")[66] == "T" else True

				if mostrar:

					cv.setFillColor(blue)
					cv.drawString(490,34,"Total dos produtos: ")
					cv.drawString(490,24,"Total do  pedido: ")
					
					if sair_custos:	cv.drawRightString(605,34,format(self.cm[0][13],','))
					if sair_custos:	cv.drawRightString(605,24,format(self.cm[0][26],','))
					cv.setFillColor(black)

					cv.drawString(615,34,"Valor ST: ")
					cv.drawString(615,24,"Valor IPI: ")
					if sair_custos:	cv.drawRightString(700,34,format(self.cm[0][17],','))
					if sair_custos:	cv.drawRightString(700,24,format(self.cm[0][22],','))

					cv.drawString(710,34,"Valor PIS: ")
					cv.drawString(710,24,"Valor COFINS: ")
					if sair_custos:	cv.drawRightString(815,34,format(self.cm[0][23],','))
					if sair_custos:	cv.drawRightString(815,24,format(self.cm[0][24],','))

				separar()
							
				""" Salva Arquivo Enviar p/o Gerenciador """
				cv.save()
				
				gerenciador.Anexar = nomeArquivo
				gerenciador.emails = emails
				gerenciador.TIPORL = "COT"
				gerenciador.cdclie = self.cm[0][1]
				gerenciador.nupcmp = str(pedido)
				gerenciador.imprimir = True
				gerenciador.Filial   = Filiais
				gerenciador.enviarem = email
				
				ger_frame=gerenciador(parent=par,id=-1)
				ger_frame.Centre()
				ger_frame.Show()

class comprovante:
	
	def relacao(self,dav,par,imp, Filial = ''):

		def cabcomprov():

			""" Cabecalho """
			pag = str(pg).zfill(3)
			rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"Comprovante",1)
		
			""" Titulo de Cabecalho """
			cb1= cb2= cb3= cb4= cb5= cb6= cb7= cb8= cb9= cb10= cb11= cb12='' 
			rel =  'Usuário: '+str(login.usalogin)
			cb1 =  "22|765|Contas Areceber [ Desmembramento ]|"

			mdl.mtitulo(rel,cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12,6,1)

		def separar():
			
			cv.line(85,float(ccampo),85,float(lcampo))
			cv.line(170,float(ccampo),170,float(lcampo))
			cv.line(255,float(ccampo),255,float(lcampo))
			cv.line(20,float(lcampo),570,float(lcampo))

		conn = sqldb()
		sql  = conn.dbc("Compravantes de pagamentos", fil = Filial, janela = par )
		cnt  = True

		if sql[0] == True:	

			nDav = dav.split('/')[0]

			comp = sql[2].execute("SELECT * FROM receber WHERE rc_ndocum='"+str( nDav )+"'")
			cm = sql[2].fetchall()
			conn.cls(sql[1])

			if comp == 0:	alertas.dia(par,u"Título: {"+dav[:13]+"}, não localizado...\n"+(' '*100),"Contas Areceber: Comprovante de pagamento")

			if comp !=0:

				if cm[0][64] == None:

					alertas.dia(par,u"Desmembramento vazio...\n"+(' '*80),"Contas Areceber: Compravens de pagamento")
					return
				
				TT  = cm[0][64].split('|')
			
				mdl = modelo()
				dh  = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
				pg  = 1

				nomeArquivo = diretorios.usPasta+"comprovrc_"+login.usalogin.lower()+".pdf"

				""" Abertura do Arquivo """
				cv = canvas.Canvas(nomeArquivo, pagesize=A4)
			
				""" Cabecalho """
				cabcomprov()

				if imp == 2: #--:Reimpressao

					cv.saveState()
					cv.setFont("Courier", 70) 
					cv.setFillGray(0.2,0.2) 
					cv.translate(700,100) 
					cv.rotate(45) 
					cv.drawCentredString (0, 500, "Reimpressão!")
										
					cv.restoreState()

				""" Totalizacao dos Titulos """
				valorT = Decimal('0.00')
				linhas = 0
				
				for i in TT:

					if i != '':

						sa = i.split(';')
						valorT +=( Decimal( sa[2].replace(',','') ) )
						linhas +=1
						
				cv.setFont('Helvetica', 8)	
				cv.drawString(22,740,"Comprovante de recebimento { Relação de títulos baixados }:")
				
				cv.setFont('Helvetica', 7)
				cv.drawString(22,720,"Código CPF-CPNJ:")
				cv.drawString(22,710,"Fantasia-Nome:")
				
				cv.drawString(115,720,"{ "+str(cm[0][11])+" }   "+str(cm[0][14]))
				cv.drawString(115,710,"{ "+str(cm[0][13])+" }   "+str(cm[0][12]))

				cv.setFont('Helvetica', 6)
				if cm[0][7] != None:	cv.drawString(260,740,"Emisaão: "+format(cm[0][7],'%d/%m/%Y')+'  '+str(cm[0][8])+"  "+str(cm[0][10]))

				cv.setFont('Helvetica-Bold', 7)

				cv.drawString(420,740,"Total de títulos baixados:")
				cv.drawString(420,720,"Troco:")
				cv.drawString(420,710,"Transferido para ContaCorrente:")
				cv.drawRightString(567,740,format(valorT,','))
				cv.drawRightString(567,720,format(cm[0][41],','))
				cv.drawRightString(567,710,format(cm[0][42],','))
				cv.line(20,705,570,705)
				cv.line(20,695,570,695)

				cv.setFont('Helvetica-Bold', 6)

				cv.drawString(22, 698,"Nº Título")
				cv.drawString(101,698,"Vencimento")
				cv.drawString(184,698,"Valor")
				cv.drawString(210,698,"Atraso")
				cv.drawString(237,698,"Forma de pagamento")

				lcampo = 685
				ccampo = 695
				ordems = 1
				cv.setFont('Helvetica', 7)	

				for i in TT:
					
					if i != '':

						sa  = i.split(';')
						
						cv.drawString(22, float(lcampo),sa[0])
						cv.drawString(100,float(lcampo),sa[1])
						cv.drawRightString(200,float(lcampo),sa[2])
						cv.drawRightString(230,float(lcampo),sa[3])
						cv.drawString(237,float(lcampo),sa[4])

						cv.setFont('Helvetica', 5)
						cv.setFillColor(HexColor('0x7F7F7F'))
						cv.drawRightString(566,float(lcampo),str(ordems).zfill(3))
						cv.setFillColor(HexColor('0x1A1A1A'))
						cv.setFont('Helvetica', 7)	
						ordems +=1
						lcampo -=10

				cv.line(20,( lcampo + 7 ),570,( lcampo + 7 ))
				cv.line(90,705,90,  ( lcampo + 7 ))
				cv.line(140,705,140,( lcampo + 7 ))
				cv.line(205,705,205,( lcampo + 7 ))
				cv.line(235,705,235,( lcampo + 7 ))
				cv.line(555,695,555,( lcampo + 7 ))
				
				""" Relacao dos novos vencimentos """
				lcampo -=20
				cv.setFillColor(HexColor('0x4D4D4D'))
				cv.setFont('Helvetica-Bold', 6)	
				cv.drawString(22, float(lcampo),"Lançamentos de títulos através do desmembramento das baixas relacionadas acima")
				cv.setFillColor(HexColor('0x1A1A1A'))
				
				cv.line(20,( lcampo-2 ),570,( lcampo-2 ))
				cv.line(20,( lcampo-12 ),570,( lcampo-12 ))

				cv.drawString(22, ( lcampo-8 ),"Nº Título")
				cv.drawString(101,( lcampo-8 ),"Vencimento")
				cv.drawString(184,( lcampo-8 ),"Valor")
				cv.drawString(207,( lcampo-8 ),"Recebimento-Baixa")
				cv.drawString(342,( lcampo-8 ),"Estado do título")
				cv.drawString(442,( lcampo-8 ),"Forma de pagamento-recebimento")
				
				posicao = ( lcampo-2 )
				cv.setFont('Helvetica', 7)	
				lcampo -=20
				
				for i in cm:

					paga = ''
					stat = 'Recebido [Documento]'
					if   i[35] == '1':	stat = 'Recebido-Baixado'
					elif i[35] == '2':	stat = 'Liquidação'
					elif i[35] == '3':	stat = 'Estornado'
					elif i[35] == '4':	stat = 'Cancelado p/desmembramento'
					elif i[35] == '5':	stat = 'Cancelado'
					
					if i[19] !=None:	paga = format(i[19],'%d/%m/%Y')+' '+str(i[20])+' '+str(i[17])
					if paga != '':	cv.setFillColor(HexColor('0xA52A2A'))

					if i[35] == '4' or i[35] == '5':	cv.setFillColor(HexColor('0xBC0D0D'))
					cv.drawString(22, float(lcampo),i[1]+'/'+str(i[3]))
					cv.drawString(100,float(lcampo),format(i[26],'%d/%m/%Y'))
					cv.drawRightString(200,float(lcampo),format(i[5],','))
					cv.drawString(207,float(lcampo),paga)
					cv.drawString(342,float(lcampo),stat)
					cv.drawString(442,float(lcampo),i[6])

					cv.setFillColor(HexColor('0x4D4D4D'))
					lcampo -=10

				cv.line(20,( lcampo + 7 ),570,( lcampo + 7 ))
				cv.line(90, posicao,90, ( lcampo + 7 ))
				cv.line(140,posicao,140,( lcampo + 7 ))
				cv.line(205,posicao,205,( lcampo + 7 ))
				cv.line(340,posicao,340,( lcampo + 7 ))
				cv.line(440,posicao,440,( lcampo + 7 ))

				cv.addPageLabel(pg)
				cv.showPage()						
							
				""" Salva Arquivo Enviar p/o Gerenciador """
				cv.save()

				gerenciador.TIPORL = ''
				gerenciador.Anexar = nomeArquivo
				gerenciador.imprimir = True
				gerenciador.Filial   = Filial

				ger_frame=gerenciador(parent=par,id=-1)
				ger_frame.Centre()
				ger_frame.Show()


class sangrias:
	
	def resumoSangria(self,dI,dF,cx,par, rFiliais = False, Filial = "", Tr = "1" ):

		def cabsangria():

			""" Cabecalho """
			#_fid, _ffl, _frm = nF.rF( 1 )
			pag = str(pg).zfill(3)
			rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"Sangrias",1)
		
			""" Titulo de Cabecalho """
			cb1= cb2= cb3= cb4= cb5= cb6= cb7= cb8= cb9= cb10= cb11= cb12='' 
			rel =  'Usuário: '+str(login.usalogin)
			if rFiliais == True:	cb1 =  "22|765|{ Relatorio de Sangrias } Filial: "+str( Filial )+"|"
			else:	cb1 =  "22|765|Relatorio de Sangrias|"
			mdl.mtitulo(rel,cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12,6,1)

		def separar():
			
			cv.line(140,float(ccampo),140,float(lcampo))
			cv.line(335,float(ccampo),335,float(lcampo))
			cv.line(345,float(ccampo),345,float(lcampo))

			cv.line(390,float(ccampo),390,float(lcampo))
			cv.line(435,float(ccampo),435,float(lcampo))
			cv.line(480,float(ccampo),480,float(lcampo))
			cv.line(525,float(ccampo),525,float(lcampo))

		def SangriaCab():

			cv.setFont('Helvetica', 8)	
			cv.drawString(22,740,"Relatório de sangrias")
			cv.drawString(22,730,"Periódo:")

			cv.drawString(160,740,"Valor entrada:")
			cv.drawString(160,730,"Valor saidas:")
			cv.drawString(440,740,"Suprimentos de caixa:")
			cv.drawString(440,730,"Nome do caixa:")

			cv.drawString(275,740,"Devolução em dinheiro:")
			cv.drawString(275,730,"Pagamentos de créditos:")

			cv.setFont('Helvetica', 7)
			cv.drawString(500,730,str(cx))
			cv.drawString(58, 730,str(cIni)+" A "+str(cFim))
			cv.drawString(58, 730,str(cIni)+" A "+str(cFim))
						
			vle = vls = vsc = Decimal('0.00')
			for i in sang:
					
				if i[11] == "E":	vle += ( i[6] + i[7] + i[8] + i[9] + i[10] )
				if i[11] == "S":	vls += ( i[6] + i[7] + i[8] + i[9] + i[10] )
				if i[11] == "C":	vsc += ( i[6] + i[7] + i[8] + i[9] + i[10] )

			cv.setFont('Helvetica-Bold', 6)
			vls += ( par.dvDinhe + par.pgCredi )
			cv.drawRightString(265,740,format(vle,','))
			cv.drawRightString(265,730,format(vls,','))
			cv.drawRightString(565,740,format(vsc,','))

			cv.drawRightString(430,730,format(par.dvDinhe,','))
			cv.drawRightString(430,740,format(par.pgCredi,','))
				
			cv.line(20,725,570,725)
			cv.line(20,715,570,715)

			cv.setFont('Helvetica-Bold', 6)

			cv.drawString(22, 718,"Lançamento")
			cv.drawString(142,718,"Historico")
			cv.drawString(335,718,"E/S")
			cv.drawString(347,718,"Dinheiro")
			cv.drawString(392,718,"Cartão Débito")
			cv.drawString(437,718,"Cartão Crédito")
			cv.drawString(482,718,"Ch.Avista")
			cv.drawString(527,718,"Ch.Predatado")

			""" Rodape """
			rd1= rd2= rd3= rd4= rd5= rd6= rd7= rd8= rd9='' 
			rd1 = '22|33|110|'+login.identifi+'-'+login.emfantas+' ( Relatorio de sangria )|'
			mdl.rodape(cv,rd1,rd2,rd3,rd4,rd5,rd6,rd7,rd8,rd9,7)
			
	
		conn = sqldb()
		sql  = conn.dbc("Caixa: Sangrias", fil = Filial, janela = par )
		cnt  = True

		if sql[0] == True:	

			dIni = datetime.datetime.strptime(dI.FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			dFim = datetime.datetime.strptime(dF.FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			hoje = format(datetime.datetime.now(),'%Y/%m/%d')

			cIni = datetime.datetime.strptime(dI.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			cFim = datetime.datetime.strptime(dF.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")

			sangra = "SELECT * FROM sansu WHERE ss_lancam >='"+str(dIni)+"' and ss_lancam <='"+str(dFim)+"'"
			if cx != "":	sangra = sangra.replace("WHERE","WHERE ss_usnome ='"+str(cx.split('-')[1])+"' and")
			if rFiliais == True:	sangra = sangra.replace("WHERE","WHERE ss_idfila='"+str( Filial )+"' and")

			sangrias = sql[2].execute(sangra)
			
			sang = sql[2].fetchall()
			conn.cls(sql[1])

			if sangrias ==0:	alertas.dia(par,u"Sem registro de sangria para o periódo ou para o caixa...\n"+(' '*100),"Caixa: Relatorio de sangria")

			if sangrias !=0:
									
				mdl    = modelo()
				dh   = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
				pg   = 1

				nomeArquivo = diretorios.usPasta+"sangrias"+login.usalogin.lower()+".pdf"

				""" Abertura do Arquivo """
				cv = canvas.Canvas(nomeArquivo, pagesize=A4)
						
				""" Cabecalho """
				cabsangria()
				SangriaCab()

				lcampo = 705
				ccampo = 715
				linhas = 1
				
				cv.setFont('Helvetica', 7)
				for i in sang:

					if i[11] == "E":	cv.setFillColor(HexColor('0xDF2020'))
					if i[11] == "C":	cv.setFillColor(HexColor('0x0000FF'))

					cv.drawString(22, float(lcampo), str(linhas)+' '+format(i[1],'%d/%m/%Y')+'  '+str(i[2])+'  '+str(i[3]) )
					cv.drawString(337,float(lcampo), i[11] )
					if i[6]  > 0:	cv.drawRightString(386, float(lcampo),format( i[6],  ',' ) )
					if i[10] > 0:	cv.drawRightString(432, float(lcampo),format( i[10], ',' ) )
					if i[9]  > 0:	cv.drawRightString(478, float(lcampo),format( i[9],  ',' ) )
					if i[7]  > 0:	cv.drawRightString(522, float(lcampo),format( i[7],  ',' ) )
					if i[8]  > 0:	cv.drawRightString(568, float(lcampo),format( i[8], ',' ) )


					if linhas > 64:

						cv.line(20, ( lcampo - 2 ), 570, ( lcampo - 2 ) )
						lcampo -=2
						separar()

						lcampo = 705
						ccampo = 715
						linhas = 0

						pg +=1
						cv.addPageLabel(pg)
						cv.showPage()						

						cabsangria()
						SangriaCab()

					if i[12] != None:
						
						hsT = i[12]
						if len( hsT.split('\n') ) == 1 and len( hsT ) > 60:
							hsT = hsT[:60]+'\n'+hsT[60:]
							
						his = hsT.split('\n')
						if len(his) > 1:	linhas +=( len(his) - 1 )
						for x in his:

							cv.drawString(142, float(lcampo), str(x) )
							lcampo -=10
							
					else:	lcampo -=10

					cv.setFillColor(HexColor('0x1A1A1A'))
					cv.line(20,( lcampo + 7 ),570,( lcampo + 7 ))
					linhas +=1

				lcampo +=7
				separar()

				cv.addPageLabel(pg)
				cv.showPage()						
							
				""" Salva Arquivo Enviar p/o Gerenciador """
				cv.save()

				gerenciador.TIPORL = ''
				gerenciador.Anexar = nomeArquivo
				gerenciador.imprimir = True
				gerenciador.Filial   = Filial

				ger_frame=gerenciador(parent=par,id=-1)
				ger_frame.Centre()
				ger_frame.Show()
		

	def ContaCorrente(self,dI,dF,par, rFiliais = False, Filial = "", Tp = "1", iTems = "", Davs = "", ClienTe = "", nfes = "", conTigencia = "" ):

		def cabConta(_separa):


			if Tp == "2":	_mensagem = mens.showmsg("Montando PDF-DANFE NFCe!!\nAguarde...", filial =  Filial )

			""" Cabecalho """
			pag = str(pg).zfill(3)
			if Tp == "1":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filial, "Conta Corrente",1)
			if Tp == "2":	rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filial, "DANFE NFCe",1)
		
			""" Titulo de Cabecalho """
			cb1= cb2= cb3= cb4= cb5= cb6= cb7= cb8= cb9= cb10= cb11= cb12='' 
			rel =  'Usuário: '+str(login.usalogin)
			
			if Tp == "1":
				
				if rFiliais == True:	cb1 =  "22|765|{ Relatorio: Movimento do Conta Conrrente } Filial: "+str( Filial )+"|"
				else:	cb1 =  "22|765|Relatorio: Movimento do Conta Conrrente|"

				cb2  =   "22|718|DAV Vinculado|#7F7F7F"
				cb3  =  "142|718|Descrição do Cliente|"
				cb4  =  "360|718|Entrada|"
				cb5  =  "400|718|Saida|"
				cb6  =  "440|718|Histórico|"

				cv.setFont('Helvetica', 8)	
				cv.drawString(22,740,"Relatório de Movimento do Conta Corrente")
				
				cv.drawString(22,730,"Periódo:")
				_dI = datetime.datetime.strptime(cIni.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
				_dF = datetime.datetime.strptime(cFim.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
				cv.setFont('Helvetica', 7)
				cv.drawString( 58,730, str( _dI )+" A "+str( _dF ) )
			
				cv.setFont('Helvetica', 8)	
				cv.drawString(22,740,"Relatório de Movimento do Conta Corrente")
				cv.drawString(22,730,"Periódo:")
				cv.drawString(260,740,"Valor entrada:")
				cv.drawString(260,730,"Valor saidas:")
				cv.drawString(440,730,"Saldo:")

				cv.drawRightString(370,740,format( par.ccEntra,',' ) )
				cv.drawRightString(370,730,format( par.ccSaida,',' ) )
				cv.drawRightString(520,730,format( par.ccSaldo,',' ) )

			elif Tp == "2":
				
				cb2  =   "22|533|ITEM|#7F7F7F"
				cb3  =  " 40|533|Código|"
				cb4  =  "100|533|Descrição dos Produtos|"
				cb5  =  "350|533|Unidade|"
				cb6  =  "380|533|Quantidade|"
				cb7  =  "440|533|Valor Unitario|"
				cb8  =  "500|533|Valor Total|"

			if _separa == False:	mdl.mtitulo(rel,cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12,6,1)
			else:

				cv.line((float(cb2.split('|')[0])-2), float(ccampo), (float(cb2.split('|')[0])-2), float(lcampo))
				cv.line((float(cb3.split('|')[0])-2), float(ccampo), (float(cb3.split('|')[0])-2), float(lcampo))
				cv.line((float(cb4.split('|')[0])-2), float(ccampo), (float(cb4.split('|')[0])-2), float(lcampo))
				cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float(lcampo))
				cv.line((float(cb6.split('|')[0])-2), float(ccampo), (float(cb6.split('|')[0])-2), float(lcampo))

				if Tp == "2":

					"""   Notas de Rodape, Informacoes Fiscais   """
					if os.path.exists(diretorios.aTualPsT+"/srv/nferodape.cnf") == True:	ardp = open(diretorios.aTualPsT+"/srv/nferodape.cnf","r").read()
					else:	ardp = ""

					cv.line((float(cb7.split('|')[0])-2), float(ccampo), (float(cb7.split('|')[0])-2), float(lcampo))
					cv.line((float(cb8.split('|')[0])-2), float(ccampo), (float(cb8.split('|')[0])-2), float(lcampo))

					cv.rect(20, 542,550,68, fill=0)
					cv.rect(20, 530,550,10, fill=0)


					cv.setFont('Helvetica-Bold', 8)
					cv.drawString(35,765,"DANFE NFCe - Documento Auxiliar da Nota Fiscal Eletrônica para Consumidor Final  { Não Permite Aproveitamento de Crédito de ICMS }")

					_mensagem = mens.showmsg("Gerando QRCODE da DANFE!!\nAguarde...", filial = Filial )

					sitech = "" #-: Pesquisa pela chave 
					siteqr = "" #-: Pesquisa pela qrcode
					sitech = login.filialLT[ Filial ][38].split(";")[17].split("|")[0] if len( login.filialLT[ Filial ][38].split(";") ) >=18 else ""
					siteqr = login.filialLT[ Filial ][35].split(";")[8] if len( login.filialLT[ Filial ][35].split(";") ) >=9 else ""
					
					cv.setFont('Helvetica', 6.5)
					cv.drawString(25,740,"Consulta via leitor de QR-CODE")

					qrw = QrCodeWidget( str( nfc[0][0].strip() ) )
					b = qrw.getBounds()

					w=b[2]-b[0] 
					h=b[3]-b[1] 

					d = Drawing(100,100,transform=[100./w,0,0,100./h,0,0]) 
					d.add(qrw)
					renderPDF.draw(d, cv, 20, 640)

					cv.line(130,735,570,735)
					
					cv.line(158,735,158,720) #-: Vertical
					cv.line(188,735,188,720) #-: Vertical
					cv.line(258,735,258,720) #-: Vertical

					cv.line(198,690,198,675) #-: Vertical

					cv.line(230,660,230,645) #-: Vertical
					cv.line(300,660,300,645) #-: Vertical
					cv.line(358,660,358,645) #-: Vertical

					cv.rect(130,645,270,90, fill=0)
					cv.rect(20, 615,380,25, fill=0)
					lnh = 720
					for r in range(5):
						
						cv.line(130,lnh,400,lnh)
						lnh -=15
						
					cv.setFont('Helvetica-Bold', 8)

					if nfc[6][0] == "1":	cv.drawString(130,740,"Emitido em ambiente de Produção")
					if nfc[6][0] == "2":	cv.drawString(130,740,"Emitido em ambiente de Homlogação SEM-VALOR FISCAL")

					cv.setFont('Helvetica', 7)
					cv.drawString(402,728,"Quantidade Total do Items:")
					cv.drawString(402,718,"Sub-Total:")
					cv.drawString(402,708,"Outros:")
					cv.drawString(402,688,"Desconto:")
					cv.drawString(402,678,"Valor Total:")
					cv.setFont('Helvetica-Bold', 7)
					cv.drawString(402,668,"Forma de Pagamento")
					cv.drawString(532,668,"Valor Pago")
					cv.setFont('Helvetica', 7)
					cv.drawString(402,660,"Dinheiro:")
					cv.drawString(402,652,"Cheque:")
					cv.drawString(402,644,"Cartão de Crébito:")
					cv.drawString(402,636,"Cartão de Dédito:")
					cv.drawString(402,628,"Crédito Loja:")
					cv.drawString(402,620,"Outros:")

					ifd= ifi = ies= imu= cha= ver= fon = ''
					if ibp and len( ibp.split('|') ) >= 7:	ifd, ies, ifi, imu, cha, ver, fon = ibp.split('|')
					
					ibpT  = "Informações dos Tributos Totais Incidentes Lei Federal 12.741/2012"
					valoI = ""
					if ibp:

						valoI = "Trib aprox  Federal, R$ "+format( Decimal( ifd ),',') +" Estadual R$ "+format( Decimal( ies ),',' )+" Municipal R$ "+format( Decimal( imu ),',')+" Fonte: "+str( fon )+' '+str( ver )+' '+str( cha )
						
					cv.setFont('Helvetica', 5)
					cv.drawString(22,633, ibpT )
					cv.drawString(22,626, valoI )
					cv.setFont('Helvetica-Bold', 6)
					cv.drawString(22,603,"{ Menssagem Fiscal }" )
					cv.setFont('Helvetica', 7)

					ardp = open(diretorios.aTualPsT+"/srv/nferodape.cnf","r").read()
					if ardp.strip() !="":

						rdpa = 593
						for rd in ardp.split('\n'):
							
							cv.drawString(22,rdpa, rd )
							rdpa -=10
						
					cv.setFont('Helvetica', 5)
					cv.drawString(132,730,"Número")
					cv.drawString(160,730,"Série")
					cv.drawString(190,730,"Emissão")
					cv.drawString(260,730,"Protocolo de Autorização")
					cv.drawString(132,715,"Nº Chave de Acesso")
					cv.drawString(132,700,"Consulta pela Chave de Acesso em")

					cv.drawString(132,685,"Destinatario CPF-CNPJ")
					cv.drawString(200,685,"Nome")
					cv.drawString(132,670,"Endereço")
					cv.drawString(132,655,"Municipio")
					cv.drawString(232,655,"Bairro")
					cv.drawString(302,655,"CEP")
					cv.drawString(360,655,"Estado")
					cv.setFont('Helvetica-Bold', 8)
					
					chav = nfc[2][0] #-: Nº Chave
					proT = nfc[1][0] #-: Nº Protocolo
					dTas = hora = ""
					emDH = nF.conversao( str( nfc[3][0].split('T')[0] ), 3 ) # +" "+ str( nfc[3][0].split('T')[1] )
					
					if nfc[3][0] !='': #-: Data de Autorizacao do Protocolo
							
						dTas = nF.conversao( nfc[3][0].split('T')[0], 3 )
						hora = nfc[3][0].split("T")[1].split('-')[0]
						
					mChav = ""
					mTama = 0

					if chav !='':

						for ch in chav:
							
							mTama += 1
							mChav += ch
							if mTama == 4:	mChav += ' '
							if mTama == 4:	mTama  = 0
					
					cv.drawString(132,707, mChav )

					cv.drawString(132,722, nfc[4][0] ) #-: Nº Nota
					cv.drawString(162,722, nfc[5][0] ) #-: Nº Serie
					cv.setFont('Helvetica-Bold', 7)
					if nfc[3][0].strip():	cv.drawString(190,722, emDH ) #-: Data e hora da emissao envio
					if nfc[3][0].strip():	cv.drawString(262,722, proT+'   '+ dTas +" "+ hora ) #-: Protocolo, Data-Hora da Autorizacaos
				
					cv.setFont('Helvetica-Bold', 6)
					cv.drawString(132,693, sitech ) #-: Site de consulta pela chave
					
					if ClienTe[2]:

						_doc = ClienTe[0][0] if ClienTe[0][0] else ClienTe[1][0] #-: CNPJ-CPF
						cv.drawString( 132,677, nF.conversao( str( _doc ), 4 ) )

						cv.setFont('Helvetica-Bold', 5)
						cv.drawString( 201,677, ClienTe[2][0] )
						cv.drawString( 132,662, ClienTe[3][0] +" "+ ClienTe[4][0]+ " "+ ClienTe[5][0] )
						cv.setFont('Helvetica-Bold', 6)

						cv.drawString( 132,647, ClienTe[7][0] )
						cv.drawString( 232,647, ClienTe[6][0]  )
						cv.drawString( 302,647, nF.conversao( ClienTe[9][0],2 ) )
						cv.drawString( 360,647, ClienTe[8][0] )

					else:	cv.drawString( 201,677, "Cliente nao identificado" )
						
					"""   Totalizacao   """
					sTOT = format( Decimal( tot[0][0] ),',' )
					sDes = format( Decimal( tot[1][0] ),',' )
					sAcr = format( Decimal( tot[4][0] ),',' ) #-: vOutro
					vTOT = format( Decimal( tot[2][0] ),',' )


					"""   Formas de Pagamentos   """
					din = chq = cTc = cTd = cLj = ouT = tOut = Decimal("0.00")
					for pgto in range( len( pgt[0] ) ):
						
						if pgt[0][pgto] == "01":	din += Decimal( pgt[1][pgto] )
						if pgt[0][pgto] == "02":	chq += Decimal( pgt[1][pgto] )
						if pgt[0][pgto] == "03":	cTc += Decimal( pgt[1][pgto] )
						if pgt[0][pgto] == "04":	cTd += Decimal( pgt[1][pgto] )
						if pgt[0][pgto] == "05":	cLj += Decimal( pgt[1][pgto] )
						if pgt[0][pgto] == "99":	ouT += Decimal( pgt[1][pgto] )
				
					cv.setFont('Helvetica-Bold', 7)
					cv.drawRightString(568,728, str( len( ite[0] ) ) )

					if Decimal( sTOT.replace(',','') ):	cv.drawRightString(568,718, sTOT )
					if Decimal( sAcr.replace(',','') ):	cv.drawRightString(568,708, sAcr )
					if Decimal( sDes.replace(',','') ):	cv.drawRightString(568,688, sDes )
					if Decimal( vTOT.replace(',','') ):	cv.drawRightString(568,678, vTOT )

					if din:	cv.drawRightString(568,660, format( din,',' ) )
					if chq:	cv.drawRightString(568,652, format( chq,',' ) )
					if cTc:	cv.drawRightString(568,644, format( cTc,',' ) )
					if cTd:	cv.drawRightString(568,636, format( cTd,',' ) )
					if cLj:	cv.drawRightString(568,628, format( cLj,',' ) )
					if ouT:	cv.drawRightString(568,620, format( ouT,',' ) )

					if din !=0:	cv.drawRightString(568,660, format( din,',' ) )
					if chq !=0:	cv.drawRightString(568,652, format( chq,',' ) )
					if cTc !=0:	cv.drawRightString(568,644, format( cTc,',' ) )
					if cTd !=0:	cv.drawRightString(568,636, format( cTd,',' ) )
					if cLj !=0:	cv.drawRightString(568,628, format( cLj,',' ) )
					if ouT !=0:	cv.drawRightString(568,620, format( ouT,',' ) )

					cv.setFillColor(HexColor('0xCD4646'))
					cv.setFont('Helvetica-Bold', 30)
					cv.rotate(45) 

					if  nfc[6][0] !='1':	cv.drawString(100,0, "Ambiente de Homologação { Sem Valor Fiscal }")
					cv.rotate(-45) 
					
					cv.setFillColor(HexColor('0x000000'))
					
			if Tp == "1":	cv.line(20,725,570,725)
			if Tp == "1":	cv.line(20,715,570,715)

			""" Rodape """
			rd1= rd2= rd3= rd4= rd5= rd6= rd7= rd8= rd9='' 
			if Tp == "1":	rd1 = '22|33|110|'+login.identifi+'-'+login.emfantas+' ( Relatorio de Movimento do Conta Corrente )|'
			if Tp == "2":	rd1 = '22|33|110|'+login.identifi+'-'+login.emfantas+' ( Emissão da NFCe )|'
			mdl.rodape(cv,rd1,rd2,rd3,rd4,rd5,rd6,rd7,rd8,rd9,7)
			

		cIni = dI # datetime.datetime.strptime(dI.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
		cFim = dF # datetime.datetime.strptime(dF.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")

							
		mdl    = modelo()
		dh   = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
		pg   = 1

		if Tp == "1":	nomeArquivo = diretorios.usPasta+"movcc"+login.usalogin.lower()+".pdf"
		if Tp == "2":	nomeArquivo = diretorios.usPasta+"movcc"+login.usalogin.lower()+".pdf"

		""" Abertura do Arquivo """
		cv = canvas.Canvas(nomeArquivo, pagesize=A4)
					
		emi = dI #----------: dados do emitente
		des = ClienTe #-----: dados do cliente
		ite = iTems #-------: dados de itens
		tot = Davs #--------: totalizacao
		pgt = nfes #--------: dados de pagamentos
		nfc = conTigencia #-: dados da nota
		ibp = dF #----------: dados ibpt
		""" Cabecalho """
		cabConta(False)

		if Tp == "1":	lcampo = 705
		if Tp == "1":	ccampo = 715

		if Tp == "2":	lcampo = 520
		if Tp == "2":	ccampo = 530

		linhas = 1
		if Tp == "1":	nRegis = par.DEVconfs.GetItemCount()
		if Tp == "2":	nRegis = len( ite[0] )
		if Tp == "2":	_mensagem = mens.showmsg("Enviando DANFE p/Impressão!!\nAguarde...", filial = Filial )
		
		for i in range( nRegis ):
			
			if Tp == "1":
				
				Lanca = par.DEVconfs.GetItem(i,0).GetText()
				Clien = par.DEVconfs.GetItem(i,1).GetText()
				vlEnT = par.DEVconfs.GetItem(i,2).GetText()
				vlSai = par.DEVconfs.GetItem(i,3).GetText()
				HisTo = par.DEVconfs.GetItem(i,5).GetText()

				cv.setFont('Helvetica', 6)
				cv.drawString(22, float(lcampo), Lanca)
				cv.setFont('Helvetica', 7)
				cv.drawString(142,float(lcampo), Clien)
				cv.drawRightString(397,float(lcampo),vlEnT)
				cv.drawRightString(437,float(lcampo),vlSai)
				cv.setFont('Helvetica', 5)
				cv.drawString(441,float(lcampo),HisTo)
			
			if Tp == "2":

				cv.drawString(22, float(lcampo), str( i + 1 ).zfill(3) )
				cv.drawString(42,  float(lcampo), ite[0][i] )
				cv.setFont('Helvetica', 6)
				cv.drawString(101, float(lcampo), ite[1][i] )
				cv.setFont('Helvetica', 7)
				cv.drawString(355, float(lcampo), ite[2][i] )
				cv.drawRightString(437,float(lcampo), nF.eliminaZeros( str( ite[3][i] ) ) )
				cv.drawRightString(497,float(lcampo), format( Decimal( nF.eliminaZeros( str( ite[4][i] ) ) ),',' ) )
				cv.drawRightString(568,float(lcampo), format( Decimal( ite[5][i] ),',' ) )
				
			lcampo -=10
			if linhas > 65:

				lcampo +=5
				cabConta(True)

				lcampo = 705
				ccampo = 715
				linhas = 0

				pg +=1
				cv.addPageLabel(pg)
				cv.showPage()						

				cabConta(False)
			
			else:	cv.line(20,( lcampo + 7 ),570,( lcampo + 7 ))

			linhas +=1

		lcampo +=7
		cabConta(True)


		cv.addPageLabel(pg)
		cv.showPage()						
					
		""" Salva Arquivo Enviar p/o Gerenciador """
		cv.save()
		if Tp == "2":	del _mensagem

		gerenciador.TIPORL = ''
		gerenciador.Anexar = nomeArquivo
		gerenciador.imprimir = True
		gerenciador.Filial   = Filial

		ger_frame=gerenciador(parent=par,id=-1)
		ger_frame.Centre()
		ger_frame.Show()
		
class atendimentos:
	
	def aTresumo( self, dI, dF, cx, par, rFiliais = False, Filial = "" ):

		def cabAtendimentos(_separa):

			""" Cabecalho """
			pag = str(pg).zfill(3)
			rls.cabecalhopadrao(cv,ImageReader,dh,pag, Filial,"Atendimentos",2)
		
			""" Titulo de Cabecalho """
			cb1= cb2= cb3= cb4= cb5= cb6= cb7= cb8= cb9= cb10= cb11= cb12='' 
			rel =  'Usuário: '+str(login.usalogin)

			cb1  =   "22|482|Login"+(" "*22)+"Nome do Vendedor|"
			cb2  =  "260|482|Total Frete|#7F7F7F"
			cb3  =  "320|482|Total Acréscimos|#7F7F7F"
			cb4  =  "383|482|Em Aberto|#7F7F7F"
			cb5  =  "446|482||"
			cb6  =  "447|482||"
			cb7  =  "448|482|Atendimentos|#0000A3"
			cb8  =  "511|482|Total Produtos|#0000A3"
			cb9  =  "604|482|Descontos|#0000A3"
			cb10 =  "697|482|Devoluções|#0000A3"
			cb11 =  "760|482|Saldo|#0000A3"
			
			if _separa == False:	mdl.mtitulo(rel,cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12,7,2)
			else:
		
				cv.line((float(cb2.split('|')[0])-2), float(ccampo), (float(cb2.split('|')[0])-2), float(lcampo))
				cv.line((float(cb3.split('|')[0])-2), float(ccampo), (float(cb3.split('|')[0])-2), float(lcampo))
				cv.line((float(cb4.split('|')[0])-2), float(ccampo), (float(cb4.split('|')[0])-2), float(lcampo))

				"""Vazio"""
				cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float(lcampo))
				
				cv.line((float(cb6.split('|')[0])-2),  float(ccampo), (float(cb6.split('|')[0])-2), float(lcampo))
				cv.line((float(cb7.split('|')[0])-2),  float(ccampo), (float(cb7.split('|')[0])-2), float(lcampo))
				cv.line((float(cb8.split('|')[0])-2),  float(ccampo), (float(cb8.split('|')[0])-2), float(lcampo))
				cv.line((float(cb9.split('|')[0])-2),  float(ccampo), (float(cb9.split('|')[0])-2), float(lcampo))
				cv.line((float(cb10.split('|')[0])-2), float(ccampo), (float(cb10.split('|')[0])-2), float(lcampo))
				cv.line((float(cb11.split('|')[0])-2), float(ccampo), (float(cb11.split('|')[0])-2), float(lcampo))

				#-----: Linha Final
				cv.line(20,float(lcampo),820,float(lcampo))

		conn = sqldb()
		sql  = conn.dbc("Caixa: Relatorio de Atendimentos", fil = Filial, janela = par )
		cnt  = True
		TrT = truncagem()
		imp = False

		if sql[0] == True:	

			dIni = datetime.datetime.strptime(dI.FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			dFim = datetime.datetime.strptime(dF.FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			hoje = format(datetime.datetime.now(),'%Y/%m/%d')

			cIni = datetime.datetime.strptime(dI.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			cFim = datetime.datetime.strptime(dF.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")

			""" Busca a lista de vendedores no banco """
			vendedores  = "SELECT us_logi,us_nome,us_ecfs,us_regi FROM usuario ORDER BY us_logi"
			relVendedor = sql[2].execute(vendedores)
			
			rlvd = sql[2].fetchall()

			if relVendedor ==0:	alertas.dia(par,u"Sem registro no cadastro de vendedores...\n"+(' '*80),"Caixa: Relatorio de atendimentos")

			if relVendedor !=0:

				_mensagem = mens.showmsg("Montando relatorio de atendimentos!!\n\nAguarde...")

				mdl    = modelo()
				dh   = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
				pg   = 1

				nomeArquivo = diretorios.usPasta+"atendimentos"+login.usalogin.lower()+".pdf"

				""" Abertura do Arquivo """
				cv = canvas.Canvas(nomeArquivo, pagesize=landscape(A4))
						
				""" Cabecalho """
				cabAtendimentos(False)

						
				cv.setFont('Helvetica', 9)	
				cv.drawString(22,515,"Período:")
				cv.drawString(22,505,"Vendedor:")
				cv.drawString(22,495,"Relatório:")

				_vendedor = "{ Geral }"
				if cx !='':	_vendedor = cx

				cv.setFillColor(HexColor('#0000A3'))
				cv.drawString(511,515,"Nº de Atendimentos:")
				cv.drawString(518,505,"Total de Produtos:")
				cv.drawString(556,495,"S a l d o:")

				cv.drawString(700,505,"Descontos:")
				cv.drawString(700,495,"Devoluções:")

				cv.setFillColor(HexColor('#7F7F7F'))
				cv.drawString(285,515,"Frete:")
				cv.drawString(260,505,"Acréscimos:")
				cv.drawString(265,495,"Em Aberto:")
				cv.setFillColor(HexColor('#000000'))
				
				cv.drawString(80,515,str(cIni)+" A "+str(cFim))
				cv.drawString(80,505,str(_vendedor))
				cv.drawString(80,495,"{ Atendimentos }")
				 

				""" Conta o numero de atendimentos """

				__TN = "SELECT COUNT(*) FROM cdavs WHERE cr_edav>='"+str(dIni)+"' and cr_edav<='"+str(dFim)+"' and cr_reca='1' and cr_tipo='1' and cr_tfat!='2'"
				if rFiliais == True:	__TN = __TN.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and")
				
				_TNa = sql[2].execute(__TN)
				TNat = sql[2].fetchall()

				ATDM = int(0)
				if TNat[0][0] !=None:	ATDM = TNat[0][0]
				
				""" Totalizacao Geral """
				__TG = "SELECT SUM(cr_tpro),SUM(cr_vfre),SUM(cr_vacr),SUM(cr_vdes) FROM cdavs WHERE cr_edav>='"+str(dIni)+"' and cr_edav<='"+str(dFim)+"' and cr_reca='1' and cr_tipo='1' and cr_tfat!='2'"
				if rFiliais == True:	__TG = __TG.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and")
				
				_TGv = sql[2].execute(__TG)
				TGve = sql[2].fetchall()


				__Td = "SELECT SUM(cr_tpro),SUM(cr_vdes) FROM dcdavs WHERE cr_edav>='"+str(dIni)+"' and cr_edav<='"+str(dFim)+"' and cr_reca='1' and cr_tipo='1' and cr_tfat!='2'"
				if rFiliais == True:	__Td = __Td.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and")

				_Tde = sql[2].execute(__Td)
				Tdev = sql[2].fetchall()


				__TA = "SELECT SUM(cr_tpro) FROM cdavs WHERE cr_edav>='"+str(dIni)+"' and cr_edav<='"+str(dFim)+"' and cr_reca!='1' and cr_reca!='3' and cr_tipo='1' and cr_tfat!='2'"
				if rFiliais == True:	__TA = __TA.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and")

				_TAB = sql[2].execute(__TA)
				TABE = sql[2].fetchall()

				TotalVendas = pgDs = saldoVendas = Tgv = Tgf = Tga = Tgd = Tgs = Tdv = Tab = TdD = Decimal("0.00")
			
				if TGve[0][0] !=None:	Tgv  = TGve[0][0] #-: Total Geral de Vendas { Adiciona o desconto 2 vezes pq o total do dav ja vem com o desconto }
				if TGve[0][1] !=None:	Tgf  = TGve[0][1] #-: Total Geral do Frete
				if TGve[0][2] !=None:	Tga  = TGve[0][2] #-: Total Geral do acrescimo
				if TGve[0][3] !=None:	Tgd  = TGve[0][3] #-: Total Geral do desconot
	
				if TABE[0][0] !=None:	Tab  = TABE[0][0] #-: Total Em aberto
				if Tdev[0][0] !=None:	Tdv  = Tdev[0][0] #-: Total de devolucoes
				if Tdev[0][1] !=None:	TdD  = Tdev[0][1] #-: Total de desconto de devolucoes
				""" Debita desconto da Devolucao """
				if TdD !=0:	Tdv = ( Tdv - TdD )


				if Tgv !=0: TotalVendas  = Tgv 
				if Tgv !=0:	saldoVendas  = Tgv #-: Saldo de Vendas
				if Tdv !=0:	saldoVendas -= Tdv #-: Devolucao 
				if Tgd !=0:	saldoVendas -= Tgd #-: Desconto
		
				""" Media de venda  por atendimento """
				mediaDesconto = media = Decimal('0.00')
				if ATDM !=0 and saldoVendas !=0:	media = TrT.trunca( 1, ( TotalVendas / ATDM ) )
				if Tgv  !=0 and Tgd !=0:	mediaDesconto = TrT.trunca( 5, ( Tgd / Tgv * 100 ) )
				
				""" Media de desconto Geral """
				cv.setFont('Helvetica', 6)	
				cv.setFillColor(HexColor('0x093867'))
				if mediaDesconto !=0:	cv.drawRightString(819,517,"Média Descontos: ( "+format(mediaDesconto,',')+"%) ") #-: Desconto

				cv.setFont('Helvetica', 9)	
				
				cv.setFillColor(HexColor('#0000A3'))
				if ATDM !=0:	cv.drawString(600,515,format(ATDM,',')+"  { Média: ( "+format(media,',')+") }" ) #-----------------: Numero de Atendimentos
				if TotalVendas !=0:	cv.drawRightString(660,505,format(TotalVendas,',')) #-: Total Geral de Vendas
				if saldoVendas !=0:	cv.drawRightString(660,495,format(saldoVendas,',')) #-: Saldo de Vendas

				if TGve[0][3] !=None:	cv.drawRightString(818,505,format(Tgd,',')) #-: Desconto
				if Tdev[0][0] !=None:	cv.drawRightString(818,495,format(Tdv,',')) #-: Devolucao

				cv.setFillColor(HexColor('#7F7F7F'))
				if Tgf !=0:	cv.drawRightString(360,515,format(Tgf,',')) #-: Frete
				if Tga !=0:	cv.drawRightString(360,505,format(Tga,',')) #-: Acrescimo
				if Tab !=0:	cv.drawRightString(360,495,format(Tab,',')) #-: Em Aberto
				cv.setFillColor(HexColor('#000000'))

				cv.line(20,490,820,490)
				cv.line(20,480,820,480)

				cv.setFont('Helvetica-Bold', 6)

				""" Rodape """
				rd1= rd2= rd3= rd4= rd5= rd6= rd7= rd8= rd9='' 
				rd1 = '22|33|110|'+login.identifi+'-'+login.emfantas+' ( Relatorio de atendimentos )|'
				mdl.rodape(cv,rd1,rd2,rd3,rd4,rd5,rd6,rd7,rd8,rd9,7)

				lcampo = 470
				ccampo = 480
				posica = 490
				linhas = 1

				lista_vendedores = []
				lista_particapar = []
				lista_percentual = []
				lista_descontos  = []

				indice = 1
				
				relacao_atendimentos = {}
				cv.setFont('Helvetica', 9)
				
				for i in rlvd:

					_mensagem = mens.showmsg("Montando relatorio de atendimentos { "+str( i[1] )+" }!!\n\nAguarde...")

					lg = i[0] 
					us = i[1]
					cd = str(i[3]).zfill(4)
					""" Tota Vendas Recebidas,Devolucoes,Aberto """

					__TT = "SELECT SUM(cr_tnot) FROM cdavs WHERE cr_edav>='"+str(dIni)+"' and cr_edav<='"+str(dFim)+"' and cr_reca='1' and cr_vdcd='"+str(cd)+"' and cr_tipo='1' and cr_tfat!='2'"
					if rFiliais == True:	__TT = __TT.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and")

					_TTv = sql[2].execute(__TT)
					TTve = sql[2].fetchall()

					__rs = "SELECT SUM(cr_tpro), SUM(cr_vfre), SUM(cr_vacr), SUM(cr_vdes) FROM cdavs WHERE cr_edav>='"+str(dIni)+"' and cr_edav<='"+str(dFim)+"' and cr_reca='1' and cr_vdcd='"+str(cd)+"' and cr_tipo='1' and cr_tfat!='2'"
					if rFiliais == True:	__rs = __rs.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and")

					_res = sql[2].execute(__rs)
					resu = sql[2].fetchall()

					__dv = "SELECT SUM(cr_tpro),SUM(cr_vdes) FROM dcdavs WHERE cr_edav>='"+str(dIni)+"' and cr_edav<='"+str(dFim)+"' and cr_reca='1' and cr_vdcd='"+str(cd)+"' and cr_tipo='1' and cr_tfat!='2'"
					if rFiliais == True:	__dv = __dv.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and")

					_dev = sql[2].execute(__dv)
					devo = sql[2].fetchall()

					__ab = "SELECT SUM(cr_tpro) FROM cdavs WHERE cr_edav>='"+str(dIni)+"' and cr_edav<='"+str(dFim)+"' and cr_reca!='1' and cr_reca!='3' and cr_vdcd='"+str(cd)+"' and cr_tipo='1' and cr_tfat!='2'"
					if rFiliais == True:	__ab = __ab.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and")

					_abe = sql[2].execute(__ab)
					aber = sql[2].fetchall()

					""" Conta o numero de atendimentos """
					__aT = "SELECT COUNT(*) FROM cdavs WHERE cr_edav>='"+str(dIni)+"' and cr_edav<='"+str(dFim)+"' and cr_reca='1' and cr_tipo='1' and cr_vdcd='"+str(cd)+"' and cr_tfat!='2'"
					if rFiliais == True:	__aT = __aT.replace("WHERE","WHERE cr_inde='"+str( Filial )+"' and")

					_aTD = sql[2].execute(__aT)
					ATED = sql[2].fetchall()

					SaldoVenda = Tven = Tpro = Tfre = Tacr = Tdes = Tdev = Tabe = aTen = Tdvd = Decimal('0.00')
					
					if resu[0][0] !=None:	Tpro = resu[0][0]
					if resu[0][1] !=None:	Tfre = resu[0][1]
					if resu[0][2] !=None:	Tacr = resu[0][2]
					if resu[0][3] !=None:	Tdes = resu[0][3]

					if ATED[0][0] !=None:	aTen = ATED[0][0]
					if devo[0][0] !=None:	Tdev = devo[0][0]
					if devo[0][1] !=None:	Tdvd = devo[0][1]
					if aber[0][0] !=None:	Tabe = aber[0][0]
					if Tdvd !=0:	Tdev = ( Tdev - Tdvd )

					SaldoVenda = (  Tpro - Tdes - Tdev )
					
					""" Debita desconto da Devolucao """
					""" Percentuais """
					praT = prSv = prDs = prDr = Decimal('0.00')
					if TotalVendas and Tpro:	prSv = TrT.trunca( 5, ( Tpro / TotalVendas * 100 ) )
					if saldoVendas and Tdes:	prDs = TrT.trunca( 5, ( Tdes / TotalVendas * 100 ) )
					if saldoVendas and Tgd and Tdes:	prDr = TrT.trunca( 5, ( Tdes / Tgd * 100 ) )

					if ATDM !=0 and aTen !=0:

						TaT = Decimal( ATDM )
						TpT = Decimal( aTen )
						praT = TrT.trunca( 5, ( TpT / TaT * 100 ) )
					
					if ( Tpro + Tdev + Tabe ) !=0:

						lista_vendedores.append( str( i[0] ) )
						lista_particapar.append( float( prSv ) )
						lista_descontos.append( float( prDr ) )

						if par.ordenar_nao.GetValue():

							cv.drawString(22,float(lcampo),lg)
							cv.drawString(85,float(lcampo),us)
		
							cv.setFillColor(HexColor('#7F7F7F'))
							if Tfre > 0:	cv.drawRightString(317,float(lcampo),format(Tfre,','))
							if Tacr > 0:	cv.drawRightString(380,float(lcampo),format(Tacr,','))
							if Tabe > 0:	cv.drawRightString(443,float(lcampo),format(Tabe,','))
		
							cv.setFillColor(HexColor('#0000A3'))
		
							if aTen !=0:	cv.drawRightString(505,float(lcampo),format(aTen,',')) #ATENDIMENTOS
							if Tpro > 0:	cv.drawRightString(600,float(lcampo),format(Tpro,','))
		
							if Tdes > 0:	cv.drawRightString(693,float(lcampo),format(Tdes,','))
							if Tdev > 0:	cv.drawRightString(756,float(lcampo),format(Tdev,','))
							if SaldoVenda > 0:	cv.drawRightString(818,float(lcampo),format(SaldoVenda,','))
							if SaldoVenda < 0:
								cv.setFillColor(HexColor('#A52A2A'))
								cv.drawRightString(818,float(lcampo),'('+format(SaldoVenda,',')+')')
		
							""" Percentuais """
							cv.setFont('Helvetica', 6)
							cv.setFillColor(HexColor('0x093867'))
							if prDs > 0:	cv.drawString(603,float(lcampo),"("+format(prDs,',')+"%)")
							if prSv > 0:	cv.drawString(510,float(lcampo),"("+format(prSv,',')+"%)")
							if praT > 0:	cv.drawString(447,float(lcampo),"("+format(praT,',')+"%)")

						_tfr = format(Tfre,',') if Tfre else ""
						_tac = format(Tacr,',') if Tacr else ""
						_ttb = format(Tabe,',') if Tabe else ""
						_tat = format(aTen,',') if aTen else ""
						_ttp = format(Tpro,',') if Tpro else ""
						_tds = format(Tdes,',') if Tdes else ""
						_tdv = format(Tdev,',') if Tdev else ""
						_sld = "0.00"
						
						if SaldoVenda > 0:	_sld = format(SaldoVenda,',')
						if SaldoVenda < 0:	_sld = '('+format(SaldoVenda,',')+')'
						
						_pds = "("+format(prDs,',')+"%)" if prDs else ''
						_psv = "("+format(prSv,',')+"%)" if prSv else ''
						_pat = "("+format(praT,',')+"%)" if praT else ''

						if par.ordenar_valor.GetValue():	relacao_atendimentos[ Tpro+Decimal("0."+str( indice ).zfill(20) ) ] = lg+'|'+us+'|'+_tfr+'|'+_tac+'|'+_ttb+'|'+_tat+'|'+_ttp+'|'+_tds+'|'+_tdv+'|'+_sld+'|'+_pds+'|'+_psv+'|'+_pat+'|'+str( prDr )
						else:	relacao_atendimentos[ float( aTen )+float( str('0.')+str( indice ).zfill(20) ) ] = lg+'|'+us+'|'+_tfr+'|'+_tac+'|'+_ttb+'|'+_tat+'|'+_ttp+'|'+_tds+'|'+_tdv+'|'+_sld+'|'+_pds+'|'+_psv+'|'+_pat+'|'+str( prDr )
						indice +=1
						if par.ordenar_nao.GetValue():
							
							cv.setFillColor(HexColor('0x000000'))
		
							cv.setFont('Helvetica', 8)
							if linhas !=1:	cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))
								
							lcampo -=10
							linhas +=1


				if not par.ordenar_nao.GetValue():


					lista_vendedores = []
					lista_particapar = []
					lista_percentual = []
					lista_descontos  = []
						
					relacao_dados = sorted( relacao_atendimentos )
					for rld in relacao_dados:

						sd = relacao_atendimentos[ rld ].split('|')
						percentual_descontos    = float( Decimal( sd[13] ) ) if sd[13] else float(0)
						percentual_participacao = float( Decimal( sd[11].replace('(','').replace(')','').replace('%','') ) ) if sd[11] else float(0)

						lista_vendedores.append( sd[0] )
						lista_particapar.append( percentual_participacao )
						lista_descontos.append( percentual_descontos )

						cv.drawString(22,float(lcampo), sd[0] )
						cv.drawString(85,float(lcampo), sd[1] )
			
						cv.setFillColor(HexColor('#7F7F7F'))
						cv.drawRightString(317,float(lcampo), sd[2] )
						cv.drawRightString(380,float(lcampo), sd[3] )
						cv.drawRightString(443,float(lcampo), sd[4] )
			
						cv.setFillColor(HexColor('#0000A3'))
			
						cv.drawRightString(505,float(lcampo), sd[5] ) #ATENDIMENTOS
						cv.drawRightString(600,float(lcampo), sd[6] )
			
						cv.drawRightString(693,float(lcampo), sd[7] )
						cv.drawRightString(756,float(lcampo), sd[8] )

						if Decimal( sd[9].replace(',','') ) > 0:	cv.drawRightString(818,float(lcampo), sd[9] )
						if Decimal( sd[9].replace(',','') ) < 0:
							cv.setFillColor(HexColor('#A52A2A'))
							cv.drawRightString(818,float(lcampo), sd[9] )
			
						""" Percentuais """
						cv.setFont('Helvetica', 6)
						cv.setFillColor(HexColor('0x093867'))
						cv.drawString(603,float(lcampo), sd[10] )
						cv.drawString(510,float(lcampo), sd[11] )
						cv.drawString(447,float(lcampo), sd[12] )
								
						cv.setFillColor(HexColor('0x000000'))
			
						cv.setFont('Helvetica', 8)
						if linhas !=1:	cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))
									
						lcampo -=10
						linhas +=1

				cabAtendimentos( True )
				if linhas >= 26:

					cv.line(20,( lcampo + 8 ),820,( lcampo + 8 ))
					""" Cor de fundo no cabecalho de Titulos """
					cv.setFillGray(0.1,0.1) 
					cv.rect(444,lcampo,376,(posica - lcampo ), fill=1)
					cv.setFillColor(HexColor('0x000000'))
					pg +=1
					cv.addPageLabel( pg )
					cv.showPage()
					cabAtendimentos( False )

				else:
					
					""" Cor de fundo no cabecalho de Titulos """
					cv.setFillGray(0.1,0.1) 
					cv.rect(444,lcampo,376,(posica - lcampo ), fill=1)
					cv.setFillColor(HexColor('0x000000'))
							
				""" Salva Arquivo Enviar p/o Gerenciador """
				lista_percentual.append( tuple( lista_particapar ) )
				if par.grafico_desco.GetValue():	lista_percentual.append( tuple( lista_descontos ) )

				largura = 300
				if len( lista_vendedores ) > 10 and par.grafico_desco.GetValue():	largura += ( 12 * ( len( lista_vendedores ) - 10 ) )
				if len( lista_vendedores ) > 10 and not par.grafico_desco.GetValue():	largura += ( 10 * ( len( lista_vendedores ) - 10 ) )

				drawing = Drawing(400, 200)
				data = lista_percentual
				bc = VerticalBarChart()
				bc.x = 50
				bc.y = 50
				bc.height = 120
				bc.width = largura
				bc.data = data
				bc.valueAxis.valueMin = 0
				bc.valueAxis.valueMax = 100
				bc.valueAxis.valueStep = 10
				
				bc.categoryAxis.labels.boxAnchor = 'ne'
				bc.categoryAxis.labels.dx = 8
				bc.categoryAxis.labels.dy = -2
				bc.categoryAxis.labels.angle = 90
				bc.categoryAxis.labels.fontName = 'Helvetica'
		
				bc.categoryAxis.categoryNames = lista_vendedores
				drawing.add(bc)
				renderPDF.draw(drawing, cv, 5, 40)

				
				cv.save()
				imp = True

				del _mensagem
				
			conn.cls(sql[1])
			
			if imp == True:

				gerenciador.TIPORL = ''
				gerenciador.Anexar = nomeArquivo
				gerenciador.imprimir = True
				gerenciador.Filial   = Filial
				
				ger_frame=gerenciador(parent=par,id=-1)
				ger_frame.Centre()
				ger_frame.Show()

class RelatorioBordero:
	
	def resumoBordero( self, _Nbordero, par, Filial = "" ):

		def cabPrincipal():

			cv.setFont('Helvetica-Bold', 10)	
			cv.drawString(145,764,"TERMO DE CUSTÓDIA SIMPLES DE CHEQUES PRÉ-DATADOS")
			cv.drawImage(ImageReader("imagens/cef.gif"), 22,715, width=45, height=40) 
			cabBordero(False)
			
			hoje = datetime.datetime.now().strftime("%d/%m/%Y")		
			cv.setFont('Helvetica', 8)	
			cv.drawString(80, 740,"Nº Lote: ")
			cv.drawString(80, 730,"Movimento:")
			cv.drawString(200,740,"Nº Conta: ")
			cv.drawString(200,730,"Emissão:")
			cv.drawString(320,740,"Valor: ")
			cv.drawString(320,730,"Somatorio:")
			cv.drawString(440,730,"QTD Cheques:")

			cv.setFillColor(HexColor('0x7F7F7F'))
			cv.drawString(128,740,_Nbordero[4:])
			cv.drawString(365,740,format(vL[0][0],','))

			cv.drawString(128,730,format(resul[0][70],"%d/%m/%Y"))
			cv.drawString(240,730,hoje)
			cv.drawString(365,730,str(_som))
			cv.drawString(500,730,str(achei))
			cv.setFillColor(HexColor('0x000000'))
		
			mensagem1 = "Por Força de Contrato de Prestação de Serviços, transferido em custódia, á Caixa"
			mensagem2 = "Econômica Federal, grande rio, os cheques abaixo relacionados, os quais deverão"
			mensagem3 = "ser depositados na conta:  em suas respectivas datas de vencimento:"

			cv.setFont('Courier', 8)
			cv.drawString(70,710,mensagem1)					
			cv.drawString(70,700,mensagem2)					
			cv.drawString(70,690,mensagem3)					
			cv.rect(25,680,540,45, fill=0)

			cv.line(20,670,570,670)
			cv.line(20,660,570,660)

			""" Cor de fundo no cabecalho de Titulos """
			cv.setFillGray(0.1,0.1) 
			cv.rect(20,660,550,10, fill=1)
			cv.setFillColor(HexColor('0x000000'))

			""" Rodape """
			rd1= rd2= rd3= rd4= rd5= rd6= rd7= rd8= rd9='' 
			rd1 = '22|33|110|'+Filial+' ( Custódia Simples de Cheques )|'
			mdl.rodape(cv,rd1,rd2,rd3,rd4,rd5,rd6,rd7,rd8,rd9,7)
			
			
		def cabBordero(_separa):

			""" Cabecalho """
			pag = str(pg).zfill(3)
			rls.cabecalhopadrao(cv,ImageReader,dh,pag,Filial,"Custódia",1)
		
			""" Titulo de Cabecalho """
			cb1= cb2= cb3= cb4= cb5= cb6= cb7= cb8= cb9= cb10= cb11= cb12='' 
			rel =  'Usuário: '+str(login.usalogin)

			cb1  =   "22|663|SEQ|"
			cb2  =   "40|663|CPF-CNPJ|"
			cb3  =  "130|663|Vencimento|"
			cb4  =  "182|663|Comp|"
			cb5  =  "208|663|Banco|"
			cb6  =  "233|663|Agência|"
			cb7  =  "265|663|Nº Conta|"
			cb8  =  "360|663|Nº Cheque|"
			cb9  =  "410|663|"+(" "*72)+"Valor|"

			if _separa == False:	mdl.mtitulo(rel,cv,cb1,cb2,cb3,cb4,cb5,cb6,cb7,cb8,cb9,cb10,cb11,cb12,7,1)
			else:

				cv.line((float(cb2.split('|')[0])-2), float(ccampo), (float(cb2.split('|')[0])-2), float(lcampo))
				cv.line((float(cb3.split('|')[0])-2), float(ccampo), (float(cb3.split('|')[0])-2), float(lcampo))
				cv.line((float(cb4.split('|')[0])-2), float(ccampo), (float(cb4.split('|')[0])-2), float(lcampo))
				cv.line((float(cb5.split('|')[0])-2), float(ccampo), (float(cb5.split('|')[0])-2), float(lcampo))
				cv.line((float(cb6.split('|')[0])-2), float(ccampo), (float(cb6.split('|')[0])-2), float(lcampo))
				cv.line((float(cb7.split('|')[0])-2), float(ccampo), (float(cb7.split('|')[0])-2), float(lcampo))
				cv.line((float(cb8.split('|')[0])-2), float(ccampo), (float(cb8.split('|')[0])-2), float(lcampo))
				cv.line((float(cb9.split('|')[0])-2), float(ccampo), (float(cb9.split('|')[0])-2), float(lcampo))


		conn = sqldb()
		sql  = conn.dbc("Contas Areceber: Relatório Borderô", fil = Filial, janela = par )
		cnt  = True

		if sql[0] == True:	

			coman = "SELECT * FROM receber WHERE rc_border='"+str( _Nbordero )+"' ORDER BY rc_vencim"
			achei = sql[2].execute(coman)
			resul = sql[2].fetchall()

			vT = "SELECT SUM(rc_apagar) FROM receber WHERE rc_border='"+str( _Nbordero )+"'"
			TT = sql[2].execute(vT)
			vL = sql[2].fetchall()

			conn.cls(sql[1])

			if achei == 0:
				
				alertas.dia(par,"Borderô não localizado !!\n"+(" "*80),"Contas Areceber: Relatório")
				return
									
			mdl = modelo()
			dh  = datetime.datetime.now().strftime("{%b %a} %d/%m/%Y %T")
			pg  = 1

			nomeArquivo = diretorios.usPasta+"bordero"+login.usalogin.lower()+".pdf"

			""" Abertura do Arquivo """
			cv = canvas.Canvas(nomeArquivo, pagesize=A4)


			""" Somatorio da Data """
			_som   = 0
			for d in resul:

				if d[26] !=None:
					_ven  = format(d[26],"%d/%m/%Y")
					_som += int(_ven.replace('/',''))

					
			""" Cabecalho """
			cabBordero(False)
			cabPrincipal()

			lcampo = 650
			ccampo = 670
			linhas = 1
			squenc = 1
			
			cv.setFont('Helvetica', 9)
			for i in resul:

				if linhas == 61:

					lcampo +=8
					cabBordero(True)

					pg +=1
					cv.addPageLabel(pg)
					cv.showPage()						

					cabBordero(False)
					cabPrincipal()

					lcampo = 650
					ccampo = 670
					linhas = 1

				cv.drawString(22,float(lcampo),str(squenc).zfill(3))

				_doc = _ven = ""
				if len(i[28]) == 11:	_doc = i[28][:3]+'.'+i[28][3:6]+'.'+i[28][6:9]+'-'+i[28][9:11]
				if len(i[28]) == 14:	_doc = i[28][:2]+'.'+i[28][2:5]+'.'+i[28][5:8]+'/'+i[28][8:12]+'-'+i[28][12:14]
				if i[26] !=None:	_ven  = format(i[26],"%d/%m/%Y")
				
				cv.drawString(42, float(lcampo),_doc)
				cv.drawString(132,float(lcampo),_ven)
				cv.drawString(184,float(lcampo),i[57])
				cv.drawString(210,float(lcampo),i[30])
				cv.drawString(234,float(lcampo),i[31])
				cv.drawString(267,float(lcampo),i[32])
				cv.drawString(362,float(lcampo),i[33])
				cv.drawRightString(567,float(lcampo),format(i[5],','))
					
				cv.line(20,float(lcampo-2),570,float(lcampo-2))

				lcampo -=10
				squenc +=1
				linhas +=1

			if linhas >= 57:

				lcampo +=8
				cabBordero(True)

				pg +=1
				cv.addPageLabel(pg)
				cv.showPage()						
				lcampo = 650
				ccampo = 670
				cabPrincipal()
			else:	
				lcampo +=8
				cabBordero(True)
						
			""" Salva Arquivo Enviar p/o Gerenciador """
			
			cv.drawString(42,  float(lcampo-30),"_______________________________________________")
			cv.drawString(105, float(lcampo-40)," Assinatura do Cliente")

			cv.drawString(330, float(lcampo-30),"_______________________________________________")
			cv.drawString(350, float(lcampo-40),"Assinatura do Responsalvel CAIXA sob carimbo")
			
			TexToRd1 = str(datetime.datetime.now().day)+" de "+login.meses[datetime.datetime.now().month]+" de "+str(datetime.datetime.now().year)
			TexToRd2 = "Valido somente com o atestatdo da CAIXA de recebimento de cheques"
			TexToRd3 = "Fim do relatório"
			cv.drawString(230, float(lcampo-60),TexToRd1)
			cv.drawString(150, float(lcampo-70),TexToRd2)
			cv.drawString(240, float(lcampo-80),TexToRd3)

			cv.save()

			gerenciador.TIPORL = ''
			gerenciador.Anexar = nomeArquivo
			gerenciador.imprimir = True
			gerenciador.Filial   = Filial

			ger_frame=gerenciador(parent=par,id=-1)
			ger_frame.Centre()
			ger_frame.Show()

class relatorioSistema:

	def AreceberDiversos(self,dI,dF,par,__id,__modulo, __fl, Filial = "" ):

		m = modelo()
		r = RelatorioArecebr()
		r.rldiversos( m, par, dI, dF, __id, __modulo, Filiais = __fl, Filial = Filial )
	
	def ApagarDiversos(self,dI,dF,par,__id, __fl, __av, Filial = "" ):

		m = modelo()
		a = RelatoriosApagar()
		a.rldiversos( m, par, dI, dF, __id, __av, Filiais = __fl, Filial = Filial )
		
	def ProdutosDiversos( self, dI, dF, par, __id, __fl, FL = "" ):

		m = modelo()
		p = RelatoriosProdutos()
		p.rldiversos( m, par, dI, dF, __id, Filiais = __fl, Filial = FL )

	def CaixaDiversos(self,dI,dF,par,__id, __fl ):

		m = modelo()
		p = RelatoriosCaixa()
		p.rldiversos(m,par,dI,dF,__id, Filiais = __fl )

	def ClienteDiversos(self,dI,dF,par,__id):

		m = modelo()
		p = RelatoriosCliente()
		p.cldiversos(m,par,dI,dF,__id, Filial = par.Filial)

	def RomaneioFrete( self,dI, dF, par, _fl ):

		m = modelo()
		p = RelatoriosOutros()
		p.rlOutros( m, par, dI, dF, _fl )

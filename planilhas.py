#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Jose de Almeida Lobinho 01-11-2014 14:54
# Criacao de Planilhas para Excel Open
import wx
import xlwt
import datetime
import os
import wx.grid as gridlib
import shutil

from decimal  import *
from conectar import login,diretorios,truncagem,dialogos,gerenciador,sqldb,menssagem
alertas = dialogos()
mens    = menssagem()

colors = ['aqua','black','blue','blue_gray','bright_green','brown','coral','cyan_ega','dark_blue','dark_blue_ega','dark_green','dark_green_ega','dark_purple','dark_red',
            'dark_red_ega','dark_teal','dark_yellow','gold','gray_ega','gray25','gray40','gray50','gray80','green','ice_blue','indigo','ivory','lavender',
            'light_blue','light_green','light_orange','light_turquoise','light_yellow','lime','magenta_ega','ocean_blue','olive_ega','olive_green','orange','pale_blue','periwinkle','pink',
            'plum','purple_ega','red','rose','sea_green','silver_ega','sky_blue','tan','teal','teal_ega','turquoise','violet','white','yellow']

class CriarPlanilhas:
	
	def EstoqueFisico(self,par,mod):

		Tru   = truncagem()
		_DaTa = datetime.datetime.now().strftime("%d%m%Y")
		_Hoje = datetime.datetime.now().strftime("%d/%m/%Y %T")

		if mod.upper() == 'PRD':	__Arq = diretorios.fsPasta+login.emfantas+'_EstoqueFisico_'+_DaTa+'.xls'
		if mod.upper() == 'DIA':	__Arq = diretorios.fsPasta+'EstoqueFisicoDia_'+_DaTa+'.xls'
		if mod.upper() == 'DIA':	__CSV = 'EstoqueFisicoDia_'+_DaTa+'.csv'
		if mod.upper() == 'DIA':

			conn  = sqldb()
			sql   = conn.dbc("Produtos: Estoque Fisico do Dia Anterior", fil = login.identifi, janela = par )

			if sql[0]:

				gravar = True
				if sql[2].execute("SELECT pr_phos FROM parametr WHERE pr_regi=1") and sql[2].fetchone()[0] == _DaTa:
					
					conn.cls( sql[1] )
					return
					
				try:
					
					sql[2].execute("UPDATE parametr SET pr_phos='"+str( _DaTa )+"' WHERE pr_regi=1")
					sql[1].commit()

					#""" Backup da Base en CSV """
					#try:

					#	if sql[2].execute('SHOW VARIABLES LIKE "secure_file_priv"'):
							
					#		__nome,__pasta = sql[2].fetchone()
					#		if __pasta:

					#			_mensagem = mens.showmsg("Não fecha essa janela, aguarde ate o final do processo!!\n\nGravando dados do cadastro de produtos em CSV!!\nAguarde...")
					#			_csv = "SELECT * FROM produtos INTO OUTFILE '"+__pasta+__CSV+"' FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n'"
					#			_acs = sql[2].execute( _csv )

					#			# Usuario comum nao tem acesso shutil.copy2(__pasta+__CSV, diretorios.fsPasta)

					#except Exception as erros:	pass

					_mensagem = mens.showmsg("Não feche essa janela, aguarde ate o final do processo!!\n\nAbrindo cadastro do estoque fisico!!\nAguarde...")

					for fl in login.ciaRelac:

						_car = sql[2].execute( "SELECT * FROM estoque WHERE ef_idfili='"+str( fl.split('-')[0] )+"'ORDER BY ef_codigo")
						if _car:
							
							_rca  = sql[2].fetchall()
							__Arq = diretorios.fsPasta+str( fl.split('-')[0] )+'_EstoqueFisicoDia_'+_DaTa+'.xls'

							_registros = 0
							relacao = {}
							Tcom = Tcus = Tcum = Tven = Decimal('0.0000')
							pcom = pcus = pcum = pven = '0.0000'

							_mensagem = mens.showmsg("Não feche essa janela, aguarde ate o final do processo!!\n\nSelecionando produtos para confecção da planilha do estoque do dia anterior da filial [ "+str( fl.split('-')[0] )+" ]\n\nAguarde...")
							for i in _rca:

								esToqueFisico = "SELECT * FROM produtos WHERE pd_codi='"+str( i[2] )+"'ORDER BY pd_nome"
								if sql[2].execute( esToqueFisico ):
									
									_prd = sql[2].fetchall()
									
									_fil = str( i[1] ) #str(_prd[0][1]) #--: Filial [ 0 ]
									_dsp = str(_prd[0][3]) #--: Descricao do Produto [ 1 ]
									_esf = str( i[4] )#str(_prd[0][15]) #-: Estoque Fisico [ 2 ]
									_uni = str(_prd[0][7]) #--: Unidade
									_pcm = str(_prd[0][23]) #-: Preco de Compra [ 3 ]
									_pcu = str(_prd[0][24]) #-: Preco de Custo [ 4 ]
									_cum = str(_prd[0][25]) #-: Custo Medido [ 5 ]
									_pcv = str(_prd[0][28]) #-: Preco de Venda [ 6 ]

									_vir = str( i[5] ) #str(_prd[0][19]) #-: Estoque Virtual [ 7 ] 
									_grp = str(_prd[0][8]) #--: Grupo [ 8 ]
									_sg1 = str(_prd[0][61]) #-: Sub Grupo1 [ 9 ]
									_sg2 = str(_prd[0][62]) #-: Sub Grupo2 [ 10 ]
									_fab = str(_prd[0][9]) #--: Fabricante [ 11 ]
									_end = str(_prd[0][11]) #-: Endereco [ 12 ]
									_ncm = _prd[0][47].split('.')[0] #-: NMC
									_cod = str(_prd[0][2]) #-----------: Codigo
									_mar = str(_prd[0][20]) #----------: Margem de lucro

									if _esf and Decimal(_esf) > 0:	Tcom += Tru.trunca(5, ( Decimal( _prd[0][23] ) * Decimal( _esf ) ) )
									if _esf and Decimal(_esf) > 0:	Tcus += Tru.trunca(5, ( Decimal( _prd[0][24] ) * Decimal( _esf ) ) )
									if _esf and Decimal(_esf) > 0:	Tcum += Tru.trunca(5, ( Decimal( _prd[0][25] ) * Decimal( _esf ) ) )
									if _esf and Decimal(_esf) > 0:	Tven += Tru.trunca(5, ( Decimal( _prd[0][28] ) * Decimal( _esf ) ) )

									if _esf !="" and Decimal( _esf ) == 0:	_esf = ""
									if _pcm !="" and Decimal( _pcm ) == 0:	_pcm = ""
									if _pcu !="" and Decimal( _pcu ) == 0:	_pcu = ""
									if _cum !="" and Decimal( _cum ) == 0:	_cum = ""
									if _pcv !="" and Decimal( _pcv ) == 0:	_pcv = ""
									if _vir !="" and Decimal( _vir ) == 0:	_vir = ""

									_relatorio = _fil+"|"+_dsp+"|"+_esf+"|"+_pcm+"|"+_pcu+"|"+_cum+"|"+_pcv+"|"+_vir+"|"+_grp+"|"+_sg1+"|"+_sg2+"|"+_fab+"|"+_end+"|"+_ncm+'|'+_cod+"|"+_mar+"|"+_uni
									relacao[_registros] = _relatorio
									_registros +=1
							
							__nReg = len(relacao.values())

							del _mensagem

							if Tcom > 0:	pcom =  Tru.trunca(4, ( Tcom / Tven * 100 ) )
							if Tcus > 0:	pcus =  Tru.trunca(4, ( Tcus / Tven * 100 ) )
							if Tcum > 0:	pcum =  Tru.trunca(4, ( Tcum / Tven * 100 ) )
							
							self.criarPlanilha( __nReg, _car, Tcom, Tcus, Tcum, Tven, pcom, pcus, pcum, mod, relacao, _DaTa, _Hoje, Tru, __Arq, str( fl.split('-')[0] ) )

				except Exception as erros:

					grava = False
						
				conn.cls(sql[1])

			else:	return
		
		else:
			
			__nReg = par.RLTprodutos.GetItemCount()
			_car   = par.RLTprodutos.GetItemCount()

			Tcom = par._sTTcp
			Tcus = par._sTTcu
			Tcum = par._sTTcm
			Tven = par._sTTvd
			
			pcom = par._pCompra
			pcus = par._pCustos
			pcum = par._pCustom

			alignment = xlwt.Alignment()
			alignment.horz = xlwt.Alignment.HORZ_RIGHT
			horz_style = xlwt.XFStyle()
			horz_style.alignment = alignment
			
			wb = xlwt.Workbook(encoding='utf-8')
			ws0 = wb.add_sheet('0')
			
			if mod.upper() == 'DIA':	Tipo = "Sistema: Relatório Geral do Dia Anterior ao Arquivo"
			else:
				Tipo = "Usuario: "
				if par.pTodos.GetValue() == True:	Tipo += "{ Geral }"
				if par.pGrupo.GetValue() == True:	Tipo += "{ Grupo: "+str(par.selecao.GetValue())+" }"
				if par.psGru1.GetValue() == True:	Tipo += "{ Sub-Grupo [ 1 ]: "+str(par.selecao.GetValue())+" }"
				if par.psGru2.GetValue() == True:	Tipo += "{ Sub-Gripo [ 2 ]: "+str(par.selecao.GetValue())+" }"
				if par.pFabri.GetValue() == True:	Tipo += "{ Fabricante: "+str(par.selecao.GetValue())+" }"
				if par.pEnder.GetValue() == True:	Tipo += "{ Endereço: "+str(par.selecao.GetValue())+" }"
            
			_mensagem = mens.showmsg("Construindo Relatorio de Estoque Fisico do Dia Anterior!!\nAguarde...")
				
			ws0.write(0, 0, "Titulo",xlwt.easyxf("font: color Brown, bold on"))
			ws0.write(0, 1, "Valor do Estoque",xlwt.easyxf("font: color Brown, bold on; align: horiz right" ))
			ws0.write(0, 2, str(Tipo),xlwt.easyxf("font: color Brown, bold on; align: horiz right" ))
			ws0.write(1, 0, "Compra",xlwt.easyxf("font: color Black, bold on" ))
			ws0.write(2, 0, "Custo",xlwt.easyxf("font: color Black, bold on" ))
			#ws0.write(3, 0, "Custo Medio",xlwt.easyxf("font: color Black, bold on" ))
			ws0.write(4, 0, "Venda",xlwt.easyxf("font: color Black, bold on" ))
			ws0.write(4, 2, u"Nº Registros: "+str(_car)+"  "+str(_Hoje)+"  "+login.usalogin,xlwt.easyxf("font: color Black, bold on" ))
            
			ws0.write(1, 1, "R$ "+format(Decimal(format(Tcom, '.2f' )),','),xlwt.easyxf("font: color blue, bold on; align: horiz right" ))
			ws0.write(2, 1, "R$ "+format(Decimal(format(Tcus, '.2f' )),','),xlwt.easyxf("font: color blue, bold on; align: horiz right" ))
			#ws0.write(3, 1, "R$ "+format(Decimal(format(Tcum, '.2f' )),','),xlwt.easyxf("font: color blue, bold on; align: horiz right" ))
			ws0.write(4, 1, "R$ "+format(Decimal(format(Tven, '.2f' )),','),xlwt.easyxf("font: color green, bold on; align: horiz right" ))
            
			ws0.write(1, 2, str(pcom)+" %",xlwt.easyxf("font: color blue, bold on" ))
			ws0.write(2, 2, str(pcus)+" %",xlwt.easyxf("font: color blue, bold on" ))
			#ws0.write(3, 2, str(pcum)+" %",xlwt.easyxf("font: color blue, bold on" ))
            
			ws0.write(6, 0, "Filial",xlwt.easyxf("font: color black, bold on" ))
			ws0.write(6, 1, u"Código do Produto",xlwt.easyxf("font: color black, bold on" ))
			ws0.write(6, 2, u"Descrição dos Produtos",xlwt.easyxf("font: color black, bold on" ))
			ws0.write(6, 3, u"Código NCM",xlwt.easyxf("font: color black, bold on" ))
			ws0.write(6, 4, "Estoque Fisico",xlwt.easyxf("font: color black, bold on; align: horiz right" ))
			ws0.write(6, 5, "Valor de Compra",xlwt.easyxf("font: color black, bold on; align: horiz right" ))
			ws0.write(6, 6, "Total Compra",xlwt.easyxf("font: color black, bold on; align: horiz right" ))
			ws0.write(6, 7, "Valor de Custo",xlwt.easyxf("font: color black, bold on; align: horiz right" ))
			ws0.write(6, 8, "Total Custo",xlwt.easyxf("font: color black, bold on; align: horiz right" ))
			ws0.write(6, 9, "Valor de Venda",xlwt.easyxf("font: color black, bold on; align: horiz right" ))
			ws0.write(6,10, "Total Venda",xlwt.easyxf("font: color black, bold on; align: horiz right" ))
		    
			Linhas = 7
			Indice = 0
			for r in range(__nReg):
            
				if mod.upper() == 'DIA':	_rel = relacao.values()[r].split('|')
				else:	_rel = par.RLTprodutos.GetItem(r, 11).GetText().split('|')
            
				_sTcp = _sTcu = _sTcm = _sTvd = Decimal('0.0000')
				
				if _rel[2] !="" and Decimal( _rel[2] ) > 0 and _rel[3] !="" and Decimal( _rel[3] ) > 0:	_sTcp = Tru.trunca(5, ( Decimal( _rel[3] ) * Decimal( _rel[2] ) ) )
				if _rel[2] !="" and Decimal( _rel[2] ) > 0 and _rel[4] !="" and Decimal( _rel[4] ) > 0:	_sTcu = Tru.trunca(5, ( Decimal( _rel[4] ) * Decimal( _rel[2] ) ) )
				if _rel[2] !="" and Decimal( _rel[2] ) > 0 and _rel[5] !="" and Decimal( _rel[5] ) > 0:	_sTcm = Tru.trunca(5, ( Decimal( _rel[5] ) * Decimal( _rel[2] ) ) )
				if _rel[2] !="" and Decimal( _rel[2] ) > 0 and _rel[6] !="" and Decimal( _rel[6] ) > 0:	_sTvd = Tru.trunca(5, ( Decimal( _rel[6] ) * Decimal( _rel[2] ) ) )
            
				ws0.write(Linhas, 0 , _rel[0] )
				ws0.col(0).width = 160*20
            
				ws0.write(Linhas, 1 , _rel[14])
				ws0.col(1).width = 300*20
            
				ws0.write(Linhas, 2 , _rel[1] )
				ws0.col(2).width = 800*20
            
				ws0.write(Linhas, 3 , _rel[13])
				ws0.col(3).width = 200*20
            
				if _rel[2] != "" and Decimal( _rel[2] ) != 0:	mfisico = Tru.trunca( 5, Decimal( _rel[2] ) )
				else:	mfisico = ""
				ws0.write(Linhas, 4 , mfisico,horz_style)
				ws0.col(4).width = 300*20
            
				""" Compra """
				style1 = xlwt.XFStyle()
				style1.num_format_str = 'R$ ##,###,##0.0000'

				style2 = xlwt.XFStyle()
				style2.num_format_str = 'R$ ##,###,##0.0000'

				pattern = xlwt.Pattern()
				pattern.pattern = xlwt.Pattern.SOLID_PATTERN
				pattern.pattern_fore_colour = xlwt.Style.colour_map['gray80']
				style2.pattern = pattern

				
				if _rel[3] != "" and Decimal( _rel[3] )> 0:	mCompra = Decimal( _rel[3] )
				else:	mCompra = ""
				ws0.write(Linhas, 5 , mCompra, style1 if mCompra else horz_style)
				ws0.col(5).width = 250*20
            
				if _sTcp != "" and Decimal( _sTcp ) > 0:	_sTcp = Decimal( _sTcp )
				else:	_sTcp = " "
				ws0.write(Linhas, 6 , _sTcp, style2 if _sTcp else horz_style)
				ws0.col(6).width = 250*20
            
				""" Custo """
				if _rel[4] != "" and Decimal( _rel[4] ) > 0:	mCusTo = Decimal( _rel[4] )
				else:	mCusTo = ""

				ws0.write(Linhas, 7 , mCusTo,style1 if mCusTo else horz_style)
				ws0.col(7).width = 250*20
            
				if _sTcu != "" and Decimal( _sTcu ) > 0:	_sTcu = Decimal( _sTcu )
				else:	_sTcu = " "
				ws0.write(Linhas, 8 , _sTcu, style2 if _sTcu else horz_style)
				ws0.col(8).width = 250*20
				
				""" Venda """
				if _rel[6] != "" and Decimal( _rel[6] ) > 0:	mVenda = Decimal( _rel[6] )
				else:	mVenda = ""
				ws0.write(Linhas, 9 , mVenda, style1 if mVenda else horz_style)
				ws0.col(9).width = 250*20
            
				if _sTvd != "" and Decimal( _sTvd ) > 0:	_sTvd = Decimal( _sTvd )
				else:	_sTvd = " "
				ws0.write(Linhas,10 , _sTvd, style2 if _sTvd else horz_style)
				ws0.col(10).width = 250*20

				Linhas +=1
				Indice +=1
            
				_rel[0]
				_rel[1]
            
			del _mensagem
            
			_rT = wb.save(__Arq)
			
			if mod.upper() == 'PRD':
            
				gerenciador.Anexar = __Arq
				gerenciador.imprimir = False
				gerenciador.Filial   = login.identifi
						
				ger_frame=gerenciador(parent=par,id=-1)
				ger_frame.Centre()
				ger_frame.Show()

	def criarPlanilha( self,__nReg, _car, Tcom, Tcus, Tcum, Tven, pcom, pcus, pcum, mod, relacao, _DaTa, _Hoje, Tru, __Arq, filial ):

		alignment = xlwt.Alignment()
		alignment.horz = xlwt.Alignment.HORZ_RIGHT
		horz_style = xlwt.XFStyle() 
		horz_style.alignment = alignment
		
		wb = xlwt.Workbook(encoding='utf-8')
		ws0 = wb.add_sheet('0')
		
		if mod.upper() == 'DIA':	Tipo = "Sistema: Relatório Geral do Dia Anterior ao Arquivo"
		else:
			Tipo = "Usuario: "
			if par.pTodos.GetValue() == True:	Tipo += "{ Geral }"
			if par.pGrupo.GetValue() == True:	Tipo += "{ Grupo: "+str(par.selecao.GetValue())+" }"
			if par.psGru1.GetValue() == True:	Tipo += "{ Sub-Grupo [ 1 ]: "+str(par.selecao.GetValue())+" }"
			if par.psGru2.GetValue() == True:	Tipo += "{ Sub-Gripo [ 2 ]: "+str(par.selecao.GetValue())+" }"
			if par.pFabri.GetValue() == True:	Tipo += "{ Fabricante: "+str(par.selecao.GetValue())+" }"
			if par.pEnder.GetValue() == True:	Tipo += "{ Endereço: "+str(par.selecao.GetValue())+" }"

		if filial:	_mensagem = mens.showmsg("Não feche essa janela, aguarde ate o final do processo!!\n\nConstruindo relatorio de estoque fisico do dia anterior, Filial: [ "+str( filial )+" ]\n\nAguarde...")
		else:	_mensagem = mens.showmsg("Não feche essa janela, aguarde ate o final do processo!!\n\nConstruindo relatorio de estoque fisico do dia anterior!!\n\nAguarde...")
			
		ws0.write(0, 0, "Titulo",xlwt.easyxf("font: color Brown, bold on"))
		ws0.write(0, 1, "Valor do Estoque",xlwt.easyxf("font: color Brown, bold on; align: horiz right" ))
		ws0.write(0, 2, str(Tipo),xlwt.easyxf("font: color Brown, bold on; align: horiz right" ))
		ws0.write(1, 0, "Compra",xlwt.easyxf("font: color Black, bold on" ))
		ws0.write(2, 0, "Custo",xlwt.easyxf("font: color Black, bold on" ))
		ws0.write(3, 0, "Custo Medio",xlwt.easyxf("font: color Black, bold on" ))
		ws0.write(4, 0, "Venda",xlwt.easyxf("font: color Black, bold on" ))
		ws0.write(4, 2, u"Nº Registros: "+str(_car)+"  "+str(_Hoje)+"  "+login.usalogin,xlwt.easyxf("font: color Black, bold on" ))

		ws0.write(1, 1, "R$ "+format(Tcom,','),xlwt.easyxf("font: color blue, bold on; align: horiz right" ))
		ws0.write(2, 1, "R$ "+format(Tcus,','),xlwt.easyxf("font: color blue, bold on; align: horiz right" ))
		ws0.write(3, 1, "R$ "+format(Tcum,','),xlwt.easyxf("font: color blue, bold on; align: horiz right" ))
		ws0.write(4, 1, "R$ "+format(Tven,','),xlwt.easyxf("font: color green, bold on; align: horiz right" ))

		ws0.write(1, 2, str(pcom)+" %",xlwt.easyxf("font: color blue, bold on" ))
		ws0.write(2, 2, str(pcus)+" %",xlwt.easyxf("font: color blue, bold on" ))
		ws0.write(3, 2, str(pcum)+" %",xlwt.easyxf("font: color blue, bold on" ))

		ws0.write(6, 0, "Filial",xlwt.easyxf("font: color black, bold on" ))
		ws0.write(6, 1, "Código do Produto",xlwt.easyxf("font: color black, bold on" ))
		ws0.write(6, 2, u"Descrição dos Produtos",xlwt.easyxf("font: color black, bold on" ))
		ws0.write(6, 3, u"Código NCM",xlwt.easyxf("font: color black, bold on" ))
		ws0.write(6, 4, "Estoque Fisico",xlwt.easyxf("font: color black, bold on; align: horiz right" ))
		ws0.write(6, 5, "Unidade",xlwt.easyxf("font: color black, bold on; align: horiz right" ))
		ws0.write(6, 6, "Valor de Compra",xlwt.easyxf("font: color black, bold on; align: horiz right" ))
		ws0.write(6, 7, "Total Compra",xlwt.easyxf("font: color black, bold on; align: horiz right" ))
		ws0.write(6, 8, "Valor de Custo",xlwt.easyxf("font: color black, bold on; align: horiz right" ))
		ws0.write(6, 9, "Total Custo",xlwt.easyxf("font: color black, bold on; align: horiz right" ))
		ws0.write(6, 10, "Valor de Venda",xlwt.easyxf("font: color black, bold on; align: horiz right" ))
		ws0.write(6,11, "Total Venda",xlwt.easyxf("font: color black, bold on; align: horiz right" ))
		ws0.write(6,12, "Maregem de Lucro",xlwt.easyxf("font: color black, bold on; align: horiz right" ))
		
		Linhas = 7
		Indice = 0
		
		for r in range( __nReg ):

			if mod.upper() == 'DIA':	_rel = relacao.values()[r].split('|')
			else:	_rel = par.RLTprodutos.GetItem(r, 11).GetText().split('|')
			
			_sTcp = _sTcu = _sTcm = _sTvd = Decimal('0.0000')
			
			if _rel[2] !="" and Decimal( _rel[2] ) > 0 and _rel[3] !="" and Decimal( _rel[3] ) > 0:	_sTcp = Tru.trunca(5, ( Decimal( _rel[3] ) * Decimal( _rel[2] ) ) )
			if _rel[2] !="" and Decimal( _rel[2] ) > 0 and _rel[4] !="" and Decimal( _rel[4] ) > 0:	_sTcu = Tru.trunca(5, ( Decimal( _rel[4] ) * Decimal( _rel[2] ) ) )
			if _rel[2] !="" and Decimal( _rel[2] ) > 0 and _rel[5] !="" and Decimal( _rel[5] ) > 0:	_sTcm = Tru.trunca(5, ( Decimal( _rel[5] ) * Decimal( _rel[2] ) ) )
			if _rel[2] !="" and Decimal( _rel[2] ) > 0 and _rel[6] !="" and Decimal( _rel[6] ) > 0:	_sTvd = Tru.trunca(5, ( Decimal( _rel[6] ) * Decimal( _rel[2] ) ) )

			ws0.write(Linhas, 0 , _rel[0] )
			ws0.col(0).width = 160*20

			ws0.write(Linhas, 1 , _rel[14])
			ws0.col(1).width = 300*20

			ws0.write(Linhas, 2 , _rel[1] )
			ws0.col(2).width = 800*20

			ws0.write(Linhas, 3 , _rel[13])
			ws0.col(3).width = 200*20

			mfisico = mCompra = mCusTo = mVenda = margem = Decimal("0.00")
			if _rel[2] != "" and Decimal( _rel[2] ) != 0:	mfisico = Tru.trunca( 5, Decimal( _rel[2] ) )
			ws0.write(Linhas, 4 , mfisico,horz_style)
			ws0.col(4).width = 300*20

			""" Unidade """
			ws0.write(Linhas, 5 , _rel[16], horz_style)
			ws0.col(5).width = 250*20
			""" Compra """

			if _rel[3] != "" and Decimal( _rel[3] ) != 0:	mCompra = Tru.trunca( 5, Decimal( _rel[3] ) )
			ws0.write(Linhas, 6 , mCompra, horz_style)
			ws0.col(6).width = 250*20

			if _sTcp != "" and Decimal( _sTcp ) != 0:	_sTcp = Decimal( _sTcp )
			ws0.write(Linhas, 7 , _sTcp, horz_style)
			ws0.col(7).width = 250*20

			""" Custo """
			#if _rel[7] != "" and Decimal( _rel[7] ) != 0:	mCusTo = Decimal( _rel[7] )
			if _rel[4] and Decimal( _rel[4] ):	mCusTo = Decimal( _rel[4] )
			ws0.write(Linhas, 8 , mCusTo ,horz_style)
			ws0.col(8).width = 250*20

			if _sTcu != "" and Decimal( _sTcu ) != 0:	_sTcu = Decimal( _sTcu )
			ws0.write(Linhas, 9 , _sTcu ,horz_style)
			ws0.col(9).width = 250*20
			
			""" Venda """
			if _rel[6] != "" and Decimal( _rel[6] ) != 0:	mVenda = Decimal( _rel[6] )
			ws0.write(Linhas, 10 , mVenda ,horz_style)
			ws0.col(10).width = 250*20

			if _sTvd != "" and Decimal( _sTvd ) != 0:	_sTvd = Decimal( _sTvd )
			ws0.write(Linhas,11 , _sTvd ,horz_style)
			ws0.col(11).width = 250*20

			if _rel[15] != "" and Decimal( _rel[15] ) != 0:	margem = Decimal( _rel[15] )
			ws0.write(Linhas,12 , margem ,horz_style)
			ws0.col(12).width = 250*20

			Linhas +=1
			Indice +=1

			_rel[0]
			_rel[1]

		del _mensagem

		_rT = wb.save(__Arq)
		
		if mod.upper() == 'PRD':

			gerenciador.Anexar = __Arq
			gerenciador.imprimir = False
			gerenciador.Filial   = login.identifi
					
			ger_frame=gerenciador(parent=par,id=-1)
			ger_frame.Centre()
			ger_frame.Show()

		
class LerGrade(wx.Frame):

	
	def __init__(self, parent,id):
		
		self.p = parent
		self.t = truncagem()
		
		if id == 770:
			
			indice = self.p.list_compra.GetFocusedItem()
			cLisTa = self.p.list_compra.GetItem(indice, 26).GetText()
			cLisTa = cLisTa.split(";")

			lista = cLisTa[7]
			iTems = cLisTa[1]
			compr = cLisTa[2]
			venda = cLisTa[3]
			devol = cLisTa[4]
			saldo = cLisTa[5]
			media = cLisTa[8].split('|')
			
		else:
			
			indice= self.p.RLTprodutos.GetFocusedItem()
			lista = self.p.RLTprodutos.GetItem(indice, 7).GetText()
			iTems = self.p.RLTprodutos.GetItem(indice, 1).GetText()
			compr = self.p.RLTprodutos.GetItem(indice, 2).GetText()
			venda = self.p.RLTprodutos.GetItem(indice, 3).GetText()
			devol = self.p.RLTprodutos.GetItem(indice, 4).GetText()
			saldo = self.p.RLTprodutos.GetItem(indice, 5).GetText()

			media = self.p.RLTprodutos.GetItem(indice, 8).GetText().split('|')
			
		_cusMedio = _vndMedio = _marcacao = saldoCompra = ""
		__qC = __qV = __qD = __ea = Decimal('0.0000') 
		if compr !='':	__qC = Decimal(compr.replace(',',''))
		if venda !='':	__qV = Decimal(venda.replace(',',''))
		if devol !='':	__qD = Decimal(devol.replace(',',''))
		if media[3] !="" and Decimal(media[3]) > 0:	__ea = Decimal(media[3])
		
		saldoCompra = ( ( __qC + __qD + __ea ) - __qV )
			
		_qT = Decimal( media[0] )
		_cu = Decimal( media[1] )
		_vd = Decimal( media[2] )


		if _qT > 0 and _cu > 0:	_cusMedio = self.t.trunca( 1, ( _cu / _qT ) )
		if _qT > 0 and _vd > 0:	_vndMedio = self.t.trunca( 1, ( _vd / _qT ) )
		if _cu > 0 and _vd > 0:	_marcacao = self.t.trunca( 1, ( ( ( _vd / _cu ) - 1 ) * 100 ) )

		wx.Frame.__init__(self, parent, id, 'Produto: { '+ iTems +' }', size=(1087,460))
		panel = wx.Panel(self)

		myGrid = gridlib.Grid(panel)
		myGrid.CreateGrid(18, 8)
		myGrid.SetDefaultCellAlignment(wx. ALIGN_RIGHT , wx. ALIGN_RIGHT)

		cinza = 2
		for z in range(16):
			
			for coluna in range(5):
				myGrid.SetCellBackgroundColour(cinza, coluna, '#E5E5E5')
				if cinza == 15:	myGrid.SetCellBackgroundColour(cinza, coluna, '#E8EDE8')
			cinza +=1

		mCor = '#E3E8ED'
		for az in range(19):

			azul = 5
			if az > 15:	mCor = '#C7D2DD'
			
			for azz in range(3):
				myGrid.SetCellBackgroundColour(az, azul, mCor)
				myGrid.SetCellFont(az, azul, wx.Font(10, wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

				azul +=1

		for c in range(2):

			myGrid.SetCellBackgroundColour(c, 0, '#89AACB')
			myGrid.SetCellBackgroundColour(c, 1, '#D7B6BB')
			myGrid.SetCellBackgroundColour(c, 2, '#AAD3AA')
			myGrid.SetCellBackgroundColour(c, 3, '#D2D2AD')
			myGrid.SetCellBackgroundColour(c, 4, '#D7CCB1')

		myGrid.SetCellValue(0,0, "Total")
		myGrid.SetCellValue(0,1, compr)
		myGrid.SetCellValue(0,2, venda)
		myGrid.SetCellValue(0,3, devol)
		myGrid.SetCellValue(0,4, saldo)
		myGrid.SetCellTextColour(0, 0, '#7F7F7F')
		myGrid.SetCellTextColour(0, 1, '#7F7F7F')
		myGrid.SetCellTextColour(0, 2, '#7F7F7F')
		myGrid.SetCellTextColour(0, 3, '#7F7F7F')
		myGrid.SetCellTextColour(0, 4, '#7F7F7F')

		myGrid.SetCellValue(1,0, u"Més")
		myGrid.SetCellValue(1,1, "a) Quantidade de Compras")
		myGrid.SetCellValue(1,2, "b) Quantidade de Vendas")
		myGrid.SetCellValue(1,3, u"c) Quantidade de Devoluções")
		myGrid.SetCellValue(1,4, "d) Saldo de Vendas")
		myGrid.SetCellValue(0,5, u"Média")
		myGrid.SetCellValue(0,6, u"Média")
		myGrid.SetCellValue(0,7, u"Média")
		myGrid.SetCellValue(1,5, "Custo")
		myGrid.SetCellValue(1,6, "Venda")
		myGrid.SetCellValue(1,7, u"Marcação")

		myGrid.SetCellValue(17,0,u"Custo/Marcação")

		myGrid.SetCellBackgroundColour(16 ,0, '#89AACB')
		myGrid.SetCellBackgroundColour(16, 1, '#D7B6BB')
		myGrid.SetCellBackgroundColour(16, 2, '#AAD3AA')
		myGrid.SetCellBackgroundColour(16, 3, '#D2D2AD')
		myGrid.SetCellBackgroundColour(16, 4, '#D7CCB1')

		myGrid.SetCellValue(15,0, "e) Estoque Anterior")
		myGrid.SetCellValue(16,0, u"Média Vendas")
		
		for ff in range(19):
			
			for fff in range(8):
				myGrid.SetCellFont(ff, fff, wx.Font(10, wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			
		Linhas = 2
		mcom = mven = mdev = msal = 0
		for i in lista.split("\n"):

			_mes = i.split("|")
			if _mes[0] !="":

				qT = Decimal( _mes[5] )
				mc = Decimal( _mes[6] )
				mv = Decimal( _mes[7] )

				_cM = _vM = _mc = ""
				if qT > 0 and mc > 0:	_cM = str( self.t.trunca( 1, ( mc / qT ) ) )
				if qT > 0 and mv > 0:	_vM = str( self.t.trunca( 1, ( mv / qT ) ) )
				if mc > 0 and mv > 0:	_mc = str( self.t.trunca( 1, ( ( ( mv / mc ) - 1 ) * 100 ) ) )

				_cmp = _vnd = _dev = _slv = ""
				if Decimal( _mes[1].replace(',','') ) !=0:
					_cmp = _mes[1]
					mcom+=1

				if Decimal( _mes[2].replace(',','') ) !=0:
					_vnd = _mes[2]
					mven+=1
					msal+=1

				if Decimal( _mes[3].replace(',','') ) !=0:
					_dev = _mes[3]
					mdev+=1

				if Decimal( _mes[4].replace(',','') ) !=0:	_slv = _mes[4]
				myGrid.SetCellValue(Linhas,0,_mes[0])
				myGrid.SetCellValue(Linhas,1,_cmp)
				myGrid.SetCellValue(Linhas,2,_vnd)
				myGrid.SetCellValue(Linhas,3,_dev)
				myGrid.SetCellValue(Linhas,4,_slv)
				myGrid.SetCellValue(Linhas,5,_cM)
				myGrid.SetCellValue(Linhas,6,_vM)
				myGrid.SetCellValue(Linhas,7,_mc+"%")
				
				_cor = 0
				for cor in range(8):
					myGrid.SetCellBackgroundColour(Linhas ,_cor, '#C2D8C2')
					_cor +=1

			Linhas +=1		

		if compr != "" and Decimal( compr.replace(",",'') ) > 0 and mcom > 1:
			mc = self.t.trunca( 5, ( Decimal( compr.replace(",",'') ) / mcom ) )
			mcom = "{ "+str(mcom)+" } "+format(mc,',')

		if venda != "" and Decimal( venda.replace(",",'') ) > 0 and mven > 1:
			mv = self.t.trunca( 5, ( Decimal( venda.replace(",",'') ) / mven ) )
			mven = "{ "+str(mven)+" } "+format(mv,',')

		if devol != "" and Decimal( devol.replace(",",'') ) > 0 and mdev > 1:
			md = self.t.trunca( 5, ( Decimal( devol.replace(",",'') ) / mdev ) )
			mdev = "{ "+str(mdev)+" } "+format(md,',')

		if saldo != "" and Decimal( saldo.replace(",",'') ) > 0 and msal > 1:
			ms = self.t.trunca( 5, ( Decimal( saldo.replace(",",'') ) / msal ) )
			msal = "{ "+str(msal)+" } "+format(ms,',')

		daTa = ""
		if media[4] !="":	daTa = format(datetime.datetime.strptime(media[4], "%Y-%m-%d"),"%d/%m/%Y")
		myGrid.SetCellValue(15,1, str(media[3]))
		myGrid.SetCellValue(15,2, daTa)
		myGrid.SetCellValue(15,3, u"Apuração: "+str(media[5]))
		myGrid.SetCellValue(15,4, "Atual: "+str(media[6]))

		myGrid.SetCellValue(16,1, str(mcom))
		myGrid.SetCellValue(16,2, str(mven))
		myGrid.SetCellValue(16,3, str(mdev))
		myGrid.SetCellValue(16,4, str(msal))

		myGrid.SetCellValue(17,1, "Custo: "+   str(_cusMedio))
		myGrid.SetCellValue(17,2, "Venda: "+   str(_vndMedio))
		myGrid.SetCellValue(17,3, u"Marcação: "+str(_marcacao)+"%")
		myGrid.SetCellValue(17,4, "Saldo (a+e-d): "+format(saldoCompra,','))

		myGrid.SetCellTextColour(17, 4, '#2F6AA3')
		if saldoCompra < 0:	myGrid.SetCellTextColour(17, 4, '#D01A1A')

		myGrid.AutoSizeColumns()
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(myGrid, flag=wx.EXPAND)
		panel.SetSizer(sizer)

class OutrosRelatorios:
    
    def contasPagas(self,par, p):

	self.p = par
	
	Tru   = truncagem()
	_DaTa = datetime.datetime.now().strftime("%d%m%Y")
	_Hoje = datetime.datetime.now().strftime("%d/%m/%Y %T")
	__Arq = diretorios.fsPasta+login.emfantas+'_contasPagas_'+_DaTa+'.xls'

	alignment = xlwt.Alignment()
	alignment.horz = xlwt.Alignment.HORZ_RIGHT
	horz_style = xlwt.XFStyle()
	style2 = xlwt.XFStyle()
	style2.num_format_str = 'R$ #,##0.00'
	style2.alignment = alignment
	horz_style.alignment = alignment
		
	wb = xlwt.Workbook(encoding='utf-8')
	ws0 = wb.add_sheet('0')

	ws0.write(0, 0, "Contas Apagar",xlwt.easyxf("font: color Brown, bold on"))
	ws0.write(0, 1, "Contas pagas",xlwt.easyxf("font: color Brown, bold on"))
	ws0.write(1, 0, "Periodo",xlwt.easyxf("font: color Brown, bold on"))
	ws0.write(1, 1, str(p), xlwt.easyxf("font: color Brown, bold on"))
	ws0.col(0).width = 220*20

	ws0.write(0, 3, "Total de contas pagas",xlwt.easyxf("font: color Blue, bold on"))
	ws0.write(1, 3, "Total de juros",xlwt.easyxf("font: color Blue, bold on"))
	ws0.write(2, 3, "Total de descontos",xlwt.easyxf("font: color Blue, bold on"))

	if par._sTPg:	ws0.write(0, 4, par._sTPg, style2)
	if par._sJur:	ws0.write(1, 4 , par._sJur, style2)
	if par._sDes:	ws0.write(2, 4 , par._sDes, style2)


	ws0.write(3, 0, "Hoje: "+str(_Hoje)+"  "+login.usalogin,xlwt.easyxf("font: color Blue, bold on" ))
	ws0.write(4, 0, "ID-Filial",xlwt.easyxf("font: color Black, bold on" ))
	ws0.write(4, 1, "Numero Lancamento",xlwt.easyxf("font: color Black, bold on" ))
	ws0.col(1).width = 240*20
	ws0.write(4, 2, "Duplicata/Cheque",xlwt.easyxf("font: color Black, bold on" ))
	ws0.col(2).width = 240*20

	ws0.write(4, 3, "Emissao",xlwt.easyxf("font: color Black, bold on" ))
	ws0.col(3).width = 300*20

	ws0.write(4, 4, "Vencimento",xlwt.easyxf("font: color Black, bold on" ))
	ws0.col(4).width = 200*20

	ws0.write(4, 5, "Pagamento",xlwt.easyxf("font: color Black, bold on" ))
	ws0.col(5).width = 300*20

	ws0.write(4, 6, "Juros",xlwt.easyxf("font: color Black, bold on; align: horiz right" ))
	ws0.write(4, 7, "Descontos",xlwt.easyxf("font: color Black, bold on; align: horiz right" ))

	ws0.write(4, 8, "Valor",xlwt.easyxf("font: color Black, bold on; align: horiz right" ))
	ws0.write(4, 9, "Descricao do fornecedor",xlwt.easyxf("font: color Black, bold on" ))
	ws0.col(9).width = 600*30

	ws0.write(4, 10, "Banco",xlwt.easyxf("font: color Black, bold on" ))
	ws0.col(10).width = 600*30

	linhas=5
	for i in range(par.APAContas.GetItemCount()):

	    _rel=par.APAContas.GetItem(i, 13).GetText().split('|')
	    _emi = _rel[2]+" "+_rel[4]
	    _ven = _rel[5]
	    _pag = _rel[8]+" "+_rel[11]

	    _jur=Decimal( format( Decimal( _rel[17].replace(',','') ),'.2f' ) ) if Decimal( _rel[17].replace(',','') ) else ''
	    _des=Decimal( format( Decimal( _rel[18].replace(',','') ),'.2f' ) ) if Decimal( _rel[18].replace(',','') ) else ''
	    _vlr=Decimal( format( Decimal( _rel[10].replace(',','') ),'.2f' ) ) if Decimal( _rel[10].replace(',','') ) else ''

	    ws0.write(linhas, 0, _rel[12])
	    ws0.write(linhas, 1, _rel[1]+"-"+_rel[6])
	    ws0.write(linhas, 2, _rel[15])
	    ws0.write(linhas, 3, _emi)
	    ws0.write(linhas, 4, _ven)
	    ws0.write(linhas, 5, _pag)
	    ws0.write(linhas, 6 , _jur, style2)
	    ws0.write(linhas, 7 , _des, style2)
	    ws0.write(linhas, 8 , _vlr, style2)
	    ws0.write(linhas, 9 , _rel[0])
	    ws0.write(linhas, 10 , _rel[19])

	    linhas+=1

	_rT = wb.save(__Arq)
	if not _rT:	self.gerenciador_impressao(__Arq)
	    
    def plano_contas(self,parent, periodo):

	self.p = parent
	_hoje = datetime.datetime.now().strftime("%d/%m/%Y %T")
	_arq = diretorios.fsPasta+login.emfantas+'plano_contas.xls'

	alignment = xlwt.Alignment()
	alignment.horz = xlwt.Alignment.HORZ_RIGHT
	horz_style = xlwt.XFStyle()
	style2 = xlwt.XFStyle()
	style2.num_format_str = 'R$ #,##0.00'
	style2.alignment = alignment
	horz_style.alignment = alignment
		
	wb = xlwt.Workbook(encoding='utf-8')
	ws0 = wb.add_sheet('0')

	ws0.write(0, 0, "Plano de contas",xlwt.easyxf("font: color green, bold on, height 260"))
	ws0.write(0, 1, u"Usuário: "+login.usalogin+' '+_hoje,xlwt.easyxf("font: color green, bold on, height 200"))
	ws0.write(1, 0, "Periodo",xlwt.easyxf("font: color black, bold on, height 180"))
	ws0.write(1, 1, str(periodo), xlwt.easyxf("font: color black, bold on, height 180"))
	ws0.col(0).width = 320*20
	ws0.col(1).width = 320*20

	ws0.write(3, 0, "Numero da conta principal",xlwt.easyxf("font: color blue, bold on, height 200" ))
	ws0.write(3, 1, "Constas secundarias",xlwt.easyxf("font: color blue, bold on, height 200" ))
	ws0.col(0).width = 350*20
	ws0.col(1).width = 300*20
	
	alignment = xlwt.Alignment()
	alignment.horz = xlwt.Alignment.HORZ_RIGHT
	horz_style = xlwt.XFStyle()
	horz_style.alignment = alignment

	linhas=4
	for i in self.p.pcontas:

	    style1 = xlwt.XFStyle()
	    style1.num_format_str = 'R$ ###,###,##0.00'
	    coluna, conta, valor = i.split('|')
	    nconta=conta.split(' ')[0]
	    qconta=0

	    for x in self.p.pcontas:
		xconta=x.split('|')[1].split(" ")[0]
		if nconta==xconta[:len(nconta)]:	qconta+=1
	    
	    coluna1, coluna2 =  int(coluna)-1, int(coluna)
	    _valor = Decimal(valor.replace(',','')) if valor else ""
	    estilo = style1 if valor else horz_style
	    
	    if qconta>1:
		ws0.write(linhas, coluna1, conta,xlwt.easyxf("font: color dark_green, bold on, height 220"))
		ws0.write(linhas, coluna2, _valor, xlwt.easyxf("font: color dark_green, bold on, height 220; align: horiz right",num_format_str='R$ ###,###,##0.00'))
	    else:
		ws0.write(linhas, coluna1, conta)
		ws0.write(linhas, coluna2, _valor,estilo)
		
	    ws0.col(coluna1).width = 500*20
	    ws0.col(coluna2).width = 250*20
	    linhas+=1

	_rT = wb.save(_arq)
	if not _rT:	self.gerenciador_impressao(_arq)
	

    def cliente_littus(self,parent):

	self.p = parent
	_hoje = datetime.datetime.now().strftime("%d/%m/%Y %T")
	_arq = diretorios.fsPasta+login.emfantas+'clientes_littus.xls'

	alignment = xlwt.Alignment()
	alignment.horz = xlwt.Alignment.HORZ_RIGHT
	horz_style = xlwt.XFStyle()
	style2 = xlwt.XFStyle()
	style2.num_format_str = 'R$ #,##0.00'
	style2.alignment = alignment
	horz_style.alignment = alignment
		
	wb = xlwt.Workbook(encoding='utf-8')
	ws0 = wb.add_sheet('0')

	ws0.write(0, 0, "Relatorio de controle Littus",xlwt.easyxf("font: color green, bold on, height 260"))
	ws0.write(0, 1, u"Usuário: "+login.usalogin+' '+_hoje,xlwt.easyxf("font: color green, bold on, height 200"))
	ws0.write(1, 0, "Hoje:",xlwt.easyxf("font: color black, bold on, height 180"))
	ws0.write(1, 1, str(_hoje), xlwt.easyxf("font: color black, bold on, height 180"))
	ws0.col(0).width = 520*20
	ws0.col(1).width = 320*20

	ws0.write(3, 0, "Codigo do cliente",xlwt.easyxf("font: color blue, bold on, height 250" ))
	ws0.write(3, 1, "Fantasia",xlwt.easyxf("font: color blue, bold on, height 250" ))
	ws0.write(3, 2, "Descricao do clietne",xlwt.easyxf("font: color blue, bold on, height 250" ))
	ws0.write(3, 3, "E R P",xlwt.easyxf("font: color blue, bold on, height 250;align: horiz right" ))
	ws0.write(3, 4, "Manutencao",xlwt.easyxf("font: color blue, bold on, height 250;align: horiz right" ))
	ws0.write(3, 5, "Backup-Cloud",xlwt.easyxf("font: color blue, bold on, height 250;align: horiz right" ))
	ws0.write(3, 6, "Outros",xlwt.easyxf("font: color blue, bold on, height 250;align: horiz right" ))
	ws0.col(0).width = 500*20
	ws0.col(1).width = 500*20
	ws0.col(2).width = 700*20
	ws0.col(3).width = 250*20
	ws0.col(4).width = 250*20
	ws0.col(5).width = 250*20
	ws0.col(6).width = 250*20

	alignment = xlwt.Alignment()
	alignment.horz = xlwt.Alignment.HORZ_RIGHT
	horz_style = xlwt.XFStyle()
	horz_style.alignment = alignment

	linhas=4
	for i in range(self.p.CLTContas.GetItemCount()):

	    style1 = xlwt.XFStyle()
	    style1.num_format_str = 'R$ ###,###,##0.00'
	    documento = self.p.CLTContas.GetItem(i,1).GetText()
	    fantasia = self.p.CLTContas.GetItem(i,2).GetText()
	    nome_cliente = self.p.CLTContas.GetItem(i,3).GetText()
	    dados = self.p.CLTContas.GetItem(i,10).GetText()
	    erp = Decimal(dados.split('|')[0].replace(',','')) if len(dados.split('|'))>=1 and dados.split('|')[0] else ""
	    man = Decimal(dados.split('|')[1].replace(',','')) if len(dados.split('|'))>=2 and dados.split('|')[1] else ""
	    bak = Decimal(dados.split('|')[2].replace(',','')) if len(dados.split('|'))>=3 and dados.split('|')[2] else ""
	    out = Decimal(dados.split('|')[3].replace(',','')) if len(dados.split('|'))>=4 and dados.split('|')[3] else ""
	    
	    ws0.write(linhas, 0, documento,xlwt.easyxf("font: color black, height 200"))
	    ws0.write(linhas, 1, fantasia, xlwt.easyxf("font: color black, height 200"))
	    ws0.write(linhas, 2, nome_cliente, xlwt.easyxf("font: color black, height 200"))
	    if erp:	ws0.write(linhas, 3, erp, xlwt.easyxf("font: color dark_green, bold on, height 220; align: horiz right",num_format_str='R$ ###,###,##0.00'))
	    if man:	ws0.write(linhas, 4, man, xlwt.easyxf("font: color dark_green, bold on, height 220; align: horiz right",num_format_str='R$ ###,###,##0.00'))
	    if bak:	ws0.write(linhas, 5, bak, xlwt.easyxf("font: color dark_green, bold on, height 220; align: horiz right",num_format_str='R$ ###,###,##0.00'))
	    if out:	ws0.write(linhas, 6, out, xlwt.easyxf("font: color dark_green, bold on, height 220; align: horiz right",num_format_str='R$ ###,###,##0.00'))

	    linhas+=1

	_rT = wb.save(_arq)
	if not _rT:	self.gerenciador_impressao(_arq)

    def gerenciador_impressao(self,__Arq):

	gerenciador.Anexar = __Arq
	gerenciador.imprimir = False
	gerenciador.Filial   = login.identifi
						
	ger_frame=gerenciador(parent=self.p,id=-1)
	ger_frame.Centre()
	ger_frame.Show()

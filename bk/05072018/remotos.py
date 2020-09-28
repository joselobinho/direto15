#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Jose de Almeida Lobinho
# 08.11.2015 19:33:31

# Faz a atualizacao remota dos dados, produtos,clientes, etc

import datetime
import time

from decimal   import *
from conectar  import sqldb,login,configuraistema,diretorios

dTa = datetime.datetime.now().strftime("%d%m%Y")
arQ = diretorios.logsPsT+"recebimento_"+dTa+'.txt'
err = diretorios.logsPsT+"erro_recebimento_"+dTa+'.txt'


class TraTrarDados:
	
	def aTualizaDados(self):

		conn = sqldb()
		sql  = conn.dbc( "", sm = False, janela = "" )

		if sql[0] == True:


			""" Relacao Geral de Lojas-Filiais """
			rlF = sql[2].execute("SELECT * FROM cia ORDER BY ep_inde")
			rsF = sql[2].fetchall()

			if rlF !=0:

				""" Relacionar Filias """
				Filiais = {}
				remoTos = []
				RFilial = []
				FlLocal = []
				FlRemot = ['']
				
				for fl in rsF:

					""" Filiais Remotas e Locais """
					if fl[30] !=None and fl[30] !='' and len( fl[30].split(";") ) > 1 and fl[30].split(";")[1] == "T":	FlRemot.append(fl[16]+'-'+fl[14])
					else:	FlLocal.append(fl[16]+'-'+fl[14])
					
					Filiais[fl[16]] = fl
					RFilial.append(fl[16]+'-'+fl[14])
					
					if fl[37] != None and fl[37].split("|")[0] !='':
						
						
						if len( fl[37].split("|") ) == 2:	remoTos.append( fl[37].split("|")[0].split(";") )
						if len( fl[37].split("|") ) == 3:

							remoTos.append( fl[37].split("|")[0].split(";") )
							remoTos.append( fl[37].split("|")[1].split(";") )
				
				print remoTos		
				login.ciaRelac = RFilial
				login.filialLT = Filiais
				login.ciaLocal = FlLocal
				login.ciaRemot = FlRemot

				for lsT in remoTos:
					
					esQ = []
					esQ.append( lsT[0] )
					esQ.append( lsT[2] )
					esQ.append( lsT[3].split("-")[0] )
					
					if esQ[0] == "ATP":	self.RecebiProdutos( esq = esQ )

					time.sleep(10) #-:Aguarda 10-Segundos
					if esQ[0] == "ATC":	self.RecebiClientes( esq = esQ )
					
					time.sleep(10) #-:Aguarda 10-Segundos

	
			conn.cls(sql[1])
				
				
	def RecebiProdutos(self, esq = [''] ):


			
		if len( esq ) == 3:
		
			dia = ( datetime.datetime.now() - datetime.timedelta(days=5) ).strftime("%Y/%m/%d")
			conn = sqldb()
			sql  = conn.dbc("", fil = esq[1], sm = False, janela = "" )
			lsT  = ""	

			fvin = ""
			if login.filialLT[ esq[1] ][35].split(";")[4] == "T":	fvin == "T" #-: Estoque Unificado

			filia = str( esq[0] )+"-"+str( esq[1] )+' {'+str( esq[2])+'}'

			if sql[0] != True:	open(err,"a").write("Erro-Abertura: "+str(datetime.datetime.now().strftime("%d/%m/%Y %T"))+" { Nao Consigo Conexao com o servidor } Atualizacao de Produtos Atraves da Filial: "+filia+"\n")

			if sql[0] == True:
						
				if sql[2].execute("SELECT * FROM produtos WHERE pd_dtal>='"+str( dia )+"' ORDER BY pd_nome") !=0:
							
					lsT = sql[2].fetchall()
					
				conn.cls(sql[1])

				""" Atualiza Produtos  """
				if lsT !="":
							
					grv  = False
					sql  = conn.dbc("", fil = esq[2], sm = False, janela = "" )

					if sql[0] == True:

						try:
								
							for i in lsT:

								achaPro = sql[2].execute("SELECT pd_codi,pd_nome,pd_dtal,pd_hcal,pd_salt FROM produtos WHERE pd_codi='"+str( i[2] )+"'")
								if achaPro != 0:

									"""  Se a filial tiver estoque unificado e/ou vinculo automatico  { Verifica se ja tem vinculo no fisico }   """
									if fvin == "T" and sql[2].execute("SELECT ef_idfili,ef_codigo FROM estoque WHERE ef_idfili='"+str( esq[2] )+"' and ef_codigo='"+str( i[2] )+"'") !=0:	fvin = ""

									lsTL = sql[2].fetchall()[0]

									if str( i[85] ) != str( lsTL[3] ):

										alT = "UPDATE produtos SET pd_nome=%s,pd_cara=%s,pd_refe=%s,pd_barr=%s,pd_unid=%s,pd_nmgr=%s,pd_fabr=%s,pd_intc=%s,pd_ende=%s,pd_gara=%s,\
										pd_pesb=%s,pd_pesl=%s,pd_estf=%s,pd_estm=%s,pd_estx=%s,pd_estt=%s,pd_virt=%s,pd_marg=%s,pd_mrse=%s,pd_mfin=%s,\
										pd_pcom=%s,pd_pcus=%s,pd_cusm=%s,pd_mdun=%s,pd_coms=%s,pd_tpr1=%s,pd_tpr2=%s,pd_tpr3=%s,pd_tpr4=%s,pd_tpr5=%s,\
										pd_tpr6=%s,pd_vdp1=%s,pd_vdp2=%s,pd_vdp3=%s,pd_vdp4=%s,pd_vdp5=%s,pd_vdp6=%s,pd_cont=%s,pd_nimp=%s,pd_prom=%s,\
										pd_pdsc=%s,pd_prod=%s,pd_bene=%s,pd_cupf=%s,pd_cfis=%s,pd_has1=%s,pd_has2=%s,pd_has3=%s,pd_canc=%s,pd_idfi=%s,\
										pd_cfir=%s,pd_esrf=%s,pd_mark=%s,pd_ula1=%s,pd_ula2=%s,pd_funa=%s,pd_frac=%s,pd_docf=%s,pd_sug1=%s,pd_sug2=%s,\
										pd_ulcm=%s,pd_ulac=%s,pd_simi=%s,pd_agre=%s,pd_marc=%s,pd_cfor=%s,pd_acds=%s,pd_fbar=%s,pd_pdof=%s,pd_marp=%s,\
										pd_stcm=%s,pd_qtem=%s,pd_altp=%s,pd_ultr=%s,pd_alte=%s,pd_kitc=%s,pd_codk=%s,pd_cokt=%s,pd_cfsc=%s,pd_imag=%s,\
										pd_dtal=%s,pd_hcal=%s,pd_salt=%s WHERE pd_codi=%s"


										Alterar = sql[2].execute( alT, (i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10],i[11],i[12],
																	   i[13],i[14],i[15],i[16],i[17],i[18],i[19],i[20],i[21],i[22],
																	   i[23],i[24],i[25],i[26],i[27],i[28],i[29],i[30],i[31],i[32],
																	   i[33],i[34],i[35],i[36],i[37],i[38],i[39],i[40],i[41],i[42],
																	   i[43],i[44],i[45],i[46],i[47],i[48],i[49],i[50],i[51],esq[1],
																	   i[53],i[54],i[55],i[56],i[57],i[58],i[59],i[60],i[61],i[62],
																	   i[64],i[65],i[66],i[67],i[68],i[69],i[70],i[71],i[72],i[73],
																	   i[74],i[75],i[76],i[77],i[78],i[79],i[80],i[81],i[82],i[83],
																	   i[84],i[85],i[86], i[2] ) )

										grv = True
												
										open(arQ,"a").write( str( datetime.datetime.now().strftime("%d/%m/%Y %T") )+" "+filia+" Produto Atualizado: "+str( i[2] )+" "+str( i[3] )+"\n" )

								if achaPro == 0:

									inC = "INSERT INTO produtos (pd_codi,pd_nome, pd_cara, pd_refe, pd_barr, pd_unid, pd_nmgr, pd_fabr, pd_intc, pd_ende, pd_gara,\
									pd_pesb, pd_pesl, pd_estf, pd_estm, pd_estx, pd_estt, pd_virt, pd_marg, pd_mrse, pd_mfin,\
									pd_pcom, pd_pcus, pd_cusm, pd_mdun, pd_coms, pd_tpr1, pd_tpr2, pd_tpr3, pd_tpr4, pd_tpr5,\
									pd_tpr6, pd_vdp1, pd_vdp2, pd_vdp3, pd_vdp4, pd_vdp5, pd_vdp6, pd_cont, pd_nimp, pd_prom,\
									pd_pdsc, pd_prod, pd_bene, pd_cupf, pd_cfis, pd_has1, pd_has2, pd_has3, pd_canc, pd_idfi,\
									pd_cfir, pd_esrf, pd_mark, pd_ula1, pd_ula2, pd_funa, pd_frac, pd_docf, pd_sug1, pd_sug2,\
									pd_ulcm, pd_ulac, pd_simi, pd_agre, pd_marc, pd_cfor, pd_acds, pd_fbar, pd_pdof, pd_marp,\
									pd_stcm, pd_qtem, pd_altp, pd_ultr, pd_alte, pd_kitc, pd_codk, pd_cokt, pd_cfsc, pd_imag,\
									pd_dtal, pd_hcal, pd_salt) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
																	  %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
																	  %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
																	  %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
																	  %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
																	  %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
																	  %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
																	  %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
																	  %s,%s,%s)"

									Incluir = sql[2].execute( inC, (i[2],i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10],i[11],i[12],
																   i[13],i[14],i[15],i[16],i[17],i[18],i[19],i[20],i[21],i[22],
																   i[23],i[24],i[25],i[26],i[27],i[28],i[29],i[30],i[31],i[32],
																   i[33],i[34],i[35],i[36],i[37],i[38],i[39],i[40],i[41],i[42],
																   i[43],i[44],i[45],i[46],i[47],i[48],i[49],i[50],i[51],esq[1],
																   i[53],i[54],i[55],i[56],i[57],i[58],i[59],i[60],i[61],i[62],
																   i[64],i[65],i[66],i[67],i[68],i[69],i[70],i[71],i[72],i[73],
																   i[74],i[75],i[76],i[77],i[78],i[79],i[80],i[81],i[82],i[83],
																   i[84],i[85],i[86] ) )


									open(arQ,"a").write( str( datetime.datetime.now().strftime("%d/%m/%Y %T") )+" "+filia+" Produto Incluido..: "+str( i[2] )+" "+str( i[3] )+"\n" )
											
									inE = "INSERT INTO estoque (ef_idfili,ef_codigo) VALUES (%s,%s)"
											
									incFisio = sql[2].execute( inE, ( esq[2], i[2] ) )
									open(arQ,"a").write("Incluido no Estoque Fisico: "+str( i[2] )+" "+str( i[3] )+" "+filia+"\n")
											
									grv = True

							if grv == True:	sql[1].commit()
							
						except Exception, _reTornos:				

							open(arQ,"a").write("Erro na Gravacao do Produto: "+str( _reTornos )+"\n")
							open(err,"a").write("Erro-gravacao: "+str(datetime.datetime.now().strftime("%d/%m/%Y %T"))+" { Nao Consigo gravar o produto: "+filia+"\nErro: "+str( _reTornos ) + "\n")
										
						conn.cls(sql[1])


	def RecebiClientes(self, esq = [] ):

		if len( esq ) == 3:
		
			dia = ( datetime.datetime.now() - datetime.timedelta(days=5) ).strftime("%Y/%m/%d")
			conn = sqldb()
			sql  = conn.dbc("", fil = esq[1], sm = False, janela = "" )
			lsT  = ""	

			filia = str( esq[0] )+"-"+str( esq[1] )+' {'+str( esq[2])+'}'
			if sql[0] != True:	open(err,"a").write("Erro-Abertura: "+str(datetime.datetime.now().strftime("%d/%m/%Y %T"))+" { Nao Consigo Conexao com o servidor } Atualizacao de Clientes Atraves da Filial: "+filia+"\n")
				

			if sql[0] == True:


				if sql[2].execute("SELECT * FROM clientes WHERE cl_dtincl>='"+str( dia )+"' and cl_docume!='' ORDER BY cl_nomecl") !=0:
						
					lsT = sql[2].fetchall()
				
				conn.cls(sql[1])

				""" Atualiza Clientes  """
				if lsT !="":
						
					grv  = False
					sql  = conn.dbc( "", sm = esq[2], janela = "" )

					if sql[0] == True:

						try:
							
							for i in lsT:

								achaDocume = sql[2].execute("SELECT cl_codigo,cl_nomecl,cl_docume,cl_dtincl,cl_hrincl,cl_incalt FROM clientes WHERE cl_docume='"+str( i[3] )+"'")
							
								if achaDocume != 0:

									lsTL = sql[2].fetchall()[0]

									if str( i[48] ) != str( lsTL[4] ):

										alT = "UPDATE clientes SET cl_nomecl=%s,cl_fantas=%s,cl_iestad=%s,cl_pessoa=%s,cl_fundac=%s,cl_cadast=%s,cl_endere=%s,cl_bairro=%s,cl_cidade=%s,cl_cdibge=%s,\
										cl_cepcli=%s,cl_compl1=%s,cl_compl2=%s,cl_estado=%s,cl_emailc=%s,cl_telef1=%s,cl_telef2=%s,cl_telef3=%s,cl_eender=%s,cl_ebairr=%s,\
										cl_ecidad=%s,cl_ecdibg=%s,cl_ecepcl=%s,cl_ecomp1=%s,cl_ecomp2=%s,cl_eestad=%s,cl_indefi=%s,cl_imunic=%s,cl_revend=%s,cl_seguim=%s,\
										cl_refere=%s,cl_redeso=%s,cl_emails=%s,cl_pgfutu=%s,cl_limite=%s,cl_refeco=%s,cl_cdsimm=%s,cl_clmarc=%s,cl_rgparc=%s,cl_dtcomp=%s,\
										cl_dadosc=%s,cl_pgtofu=%s,cl_blcred=%s,cl_compra=%s,cl_codigo=%s,cl_dtincl=%s,cl_hrincl=%s,cl_incalt=%s WHERE cl_docume=%s"


										sql[2].execute( alT, ( i[1],i[2],i[4],i[5],i[6],i[7],i[8],i[9],i[10],i[11],\
										i[12],i[13],i[14],i[15],i[16],i[17],i[18],i[19],i[20],i[21],\
										i[22],i[23],i[24],i[25],i[26],i[27],i[28],i[29],i[30],i[31],\
										i[32],i[33],i[34],i[35],i[36],i[37],i[38],i[39],i[40],i[41],\
										i[42],i[43],i[44],i[45],i[46],i[47],i[48],i[49], i[3] ) )

										grv = True
											
										open(arQ,"a").write( str( datetime.datetime.now().strftime("%d/%m/%Y %T") )+" "+filia+" Cliente Atualizado: "+str( i[3] )+" "+str( i[1] )+"\n")

								if achaDocume == 0:

									inC = "INSERT INTO clientes (cl_nomecl,cl_fantas,cl_docume,cl_iestad,cl_pessoa,cl_fundac,cl_cadast,cl_endere,cl_bairro,cl_cidade,\
									cl_cdibge,cl_cepcli,cl_compl1,cl_compl2,cl_estado,cl_emailc,cl_telef1,cl_telef2,cl_telef3,cl_eender,\
									cl_ebairr,cl_ecidad,cl_ecdibg,cl_ecepcl,cl_ecomp1,cl_ecomp2,cl_eestad,cl_indefi,cl_imunic,cl_revend,\
									cl_seguim,cl_refere,cl_redeso,cl_emails,cl_pgfutu,cl_limite,cl_refeco,cl_cdsimm,cl_clmarc,cl_rgparc,\
									cl_dtcomp,cl_dadosc,cl_pgtofu,cl_blcred,cl_compra,cl_codigo,cl_dtincl,cl_hrincl,cl_incalt)\
									VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
									%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
									%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
									%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
									%s,%s,%s,%s,%s,%s,%s,%s,%s)"

									sql[2].execute( inC, ( i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9],i[10],\
									i[11],i[12],i[13],i[14],i[15],i[16],i[17],i[18],i[19],i[20],\
									i[21],i[22],i[23],i[24],i[25],i[26],i[27],i[28],i[29],i[30],\
									i[31],i[32],i[33],i[34],i[35],i[36],i[37],i[38],i[39],i[40],\
									i[41],i[42],i[43],i[44],i[45],i[46],i[47],i[48],i[49] ) )

								
									grv = True
									open(arQ,"a").write( str( datetime.datetime.now().strftime("%d/%m/%Y %T") )+" "+filia+" Cliente Incluido..: "+str( i[3] )+" "+str( i[1] )+"\n")

							if grv == True:	sql[1].commit()
							
						except Exception, _reTornos:				

							open(arQ,"a").write("Erro na Gravacao do Clientes: "+str( _reTornos )+"\n")
							open(err,"a").write("Erro-gravacao: "+str(datetime.datetime.now().strftime("%d/%m/%Y %T"))+" { Nao Consigo gravar o cliente: "+filia+"\nErro: "+str( _reTornos ) + "\n")
		
							
						conn.cls(sql[1])
		
if __name__ == '__main__':
	
	__srv = configuraistema()
	__srv.dbserver()
	
	aTT = TraTrarDados()
	aTT.aTualizaDados()
	

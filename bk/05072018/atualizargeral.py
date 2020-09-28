#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 14-11-2015
# Alterar os codigos do clientes de 8 digitos para 14
# Devido a atualizacao remota os codigos do cliente agora leva o id + id-filial  


import wx
import os
import datetime

from decimal   import *
from conectar  import sqldb,dialogos,login,MostrarHistorico,configuraistema,diretorios

alertas = dialogos()
	
class prn:
	
	def continua(self):

		enTra = input("1-Cliente\n\n2-Idavs\n\n3-DIdavs\n\n4-Cdavs\n\n5-DCdavs\n\n6-Receber\n\n7-Conta Corrente\n\n8-Notas Fiscais\n\n9-Atualizar Imagens\n\n10-Adicionar codigos fiscais em NFCe\n\n11-Adicionar codigos fiscais no cadastro de codigos fiscais\n\n12-Ajustar icms p/2Decimais no cadastro de codigos fiscais\n\n13-Ajustar codigos fiscais p/ME\n\n14-Ajustar codigos 5403 fiscais Adicionar no CFIR 5405\n\n\nSua Opcao: ")

		conn = sqldb()
		sql  = conn.dbc( "", sm = False, janela = "" )

		if sql[0] == True:
			
			pos = {}
			c1 = sql[2].execute("SELECT cl_regist,cl_indefi FROM clientes ORDER BY cl_regist")
			if c1 !=0:

				rsc = sql[2].fetchall()
				for ps in rsc:
					
					pos[str(ps[0])] = ps[1]

#-------------: Cliente

				if enTra == 1:
					
					for i in rsc:
					
					
						nC = str(i[0])+"-"+str(i[1])
						aT = sql[2].execute("UPDATE clientes SET cl_codigo='"+str( nC )+"' WHERE cl_regist='"+str( i[0] )+"'")
						print( i[0],i[1],nC )
						
					sql[1].commit()	


#--------------: IDAVS
				if enTra == 2:
					
					c2 = sql[2].execute("SELECT cr_cdcl,cr_ndav FROM cdavs ORDER BY cr_ndav")
					rsi = sql[2].fetchall()
					
					if c2 !=0:
						nn = 1
						for i in rsi:
							
							if i[0] !='':

								cm = str( i[1] )
								
								nc = str( i[0] ) #+'-'+str( pos[ i[0] ] )
								
								aT = sql[2].execute("UPDATE idavs SET it_cdcl='"+str( nc )+"' WHERE it_ndav='"+cm+"'")
								print( nc,cm,nn )
								nn +=1
					
						sql[1].commit()
			

#--------------: DIDAVS
				if enTra == 3:
					
					c3 = sql[2].execute("SELECT it_cdcl,it_item,it_ndav,it_codi FROM didavs")
					rsi = sql[2].fetchall()
					
					if c3 !=0:
						
						for i in rsi:
							
							if i[0] !='':

								iT = str( i[1] )
								cm = str( i[2] )
								cp = str( i[3] )
								
								
								fl = pos[ i[0] ]
								nc = str( i[0] )+'-'+str( pos[ i[0] ] )
								
								aT = sql[2].execute("UPDATE didavs SET it_cdcl='"+str( nc )+"' WHERE it_item='"+iT+"' and it_ndav='"+cm+"' and it_codi='"+cp+"'")
								print( nc,iT,cm,cp )
					
						sql[1].commit()


#--------------: CDAVS
				if enTra == 4:
					
					c4 = sql[2].execute("SELECT cr_ndav,cr_cdcl FROM cdavs")
					rsc = sql[2].fetchall()
					
					if c4 !=0:
						nn = 1 
						for i in rsc:
							
							if i[1] !='':

								dav = str( i[0] )
								
								fl = pos[ i[1] ]
								nc = str( i[1] )+'-'+str( pos[ i[1] ] )
								
								aT = sql[2].execute("UPDATE cdavs SET cr_cdcl='"+str( nc )+"' WHERE cr_ndav='"+str( dav )+"'")
								print( nc,dav,nn )
								nn +=1
					
						sql[1].commit()

#--------------: DCDAVS
				if enTra == 5:
					
					c5 = sql[2].execute("SELECT cr_ndav,cr_cdcl FROM dcdavs")
					rsd = sql[2].fetchall()
					
					if c5 !=0:
						
						for i in rsd:
							
							if i[1] !='':

								dav = str( i[0] )
								
								fl = pos[ i[1] ]
								nc = str( i[1] )+'-'+str( pos[ i[1] ] )
								
								aT = sql[2].execute("UPDATE dcdavs SET cr_cdcl='"+str( nc )+"' WHERE cr_ndav='"+str( dav )+"'")
								print( nc,dav )
					
						sql[1].commit()

#--------------: Contas ARECEBER
				if enTra == 6:
					
					c6 = sql[2].execute("SELECT rc_regist,rc_clcodi FROM receber")
					rsr = sql[2].fetchall()
					
					if c6 !=0:
						
						for i in rsr:
							
							if i[1] !='':

								reg = str( i[0] )
								
								fl = pos[ i[1] ]
								nc = str( i[1] )+'-'+str( pos[ i[1] ] )
								
								aT = sql[2].execute("UPDATE receber SET rc_clcodi='"+str( nc )+"' WHERE rc_regist='"+str( reg )+"'")
								print( nc,reg,i[1] )
					
						sql[1].commit()

#--------------: Conta Corrente
				if enTra == 7:
					
					c7 = sql[2].execute("SELECT cc_regist,cc_cdclie FROM conta")
					rcc = sql[2].fetchall()
					
					if c7 !=0:
						
						for i in rcc:
							
							if i[1] !='':

								reg = str( i[0] )
								
								fl = pos[ i[1] ]
								nc = str( i[1] )+'-'+str( pos[ i[1] ] )
								
								aT = sql[2].execute("UPDATE conta SET cc_cdclie='"+str( nc )+"' WHERE cc_regist='"+str( reg )+"'")
								print( nc,reg,i[1] )
					
						sql[1].commit()


#--------------: Nota Fiscias
				if enTra == 8:
					
					c8 = sql[2].execute("SELECT nf_regist,nf_codigc FROM nfes")
					rnf = sql[2].fetchall()
					
					if c8 !=0:
						
						for i in rnf:
							
							if i[1] !='':

								reg = str( i[0] )
								try:
									
									fl = pos[ i[1] ]
									nc = str( i[1] )+'-'+str( pos[ i[1] ] )
									
									aT = sql[2].execute("UPDATE nfes SET nf_codigc='"+str( nc )+"' WHERE nf_regist='"+str( reg )+"'")
									print( nc,reg,i[1] )

								except Exception as _reTornos:	pass
								
						sql[1].commit()
			

#--------------: Nota Fiscias
				if enTra == 9:
						
					c9 = sql[2].execute("SELECT pd_regi,pd_imag FROM produtos")
					prd = sql[2].fetchall()
						
					if c9 !=0:

						EMD = datetime.datetime.now().strftime("%Y/%m/%d")
						DHO = datetime.datetime.now().strftime("%T")

							
						for i in prd:
								
							if i[1] !='' and i[1] !=None:

								reg = str( i[0] )
								try:
										
										
									aT = sql[2].execute("UPDATE produtos SET pd_dtal='"+str( EMD )+"',pd_hcal='"+str( DHO )+"',pd_salt='A' WHERE pd_regi='"+str( reg )+"'")
									print( reg ,EMD,DHO,i[1] )

								except Exception as _reTornos:	pass
									
						sql[1].commit()


#--------------: Codigos Fiscais
				if enTra == 10:
						
					c9 = sql[2].execute("SELECT pd_regi,pd_cfis,pd_cfir,pd_cfsc FROM produtos")
					prd = sql[2].fetchall()
						
					if c9 !=0:

						EMD = datetime.datetime.now().strftime("%Y/%m/%d")
						DHO = datetime.datetime.now().strftime("%T")
						QTD = 0
							
						for i in prd:
								
							if i[2] !='' and i[2] !=None:
				
								QTD +=1
								ncm,cfo,cst,icm = i[2].split(".")
								
								
								if cfo == "5405" or cfo == "5102" or cfo == "5403":
									if cfo == "5405":
										cst="0500"
										icm="0000"
									if cfo=="5102":
										cst="0101"
										icm="0000"	
									if cfo=="5403":
										cst="0500"
										icm="0000"	
									ncfis = ncm+"."+cfo+"."+cst+"."+icm
									reg = str( i[0] )
									try:
											
											
										#aT = sql[2].execute("UPDATE produtos SET pd_dtal='"+str( EMD )+"',pd_hcal='"+str( DHO )+"',pd_salt='A' WHERE pd_regi='"+str( reg )+"'")
										#aT = sql[2].execute("UPDATE produtos SET pd_cfir='"+str( ncfis )+"' WHERE pd_regi='"+str( reg )+"'")
										aT = sql[2].execute("UPDATE produtos SET pd_cfir='"+str( ncfis )+"',pd_cfsc='' WHERE pd_regi='"+str( reg )+"'")
										print( reg ,EMD,DHO,i[1],QTD,ncfis )

									except Exception as _reTornos:	pass
									
						sql[1].commit()

#--------------: Codigos Fiscais Inserir no cadastro
				if enTra == 11:
						
					c9 = sql[2].execute("SELECT pd_cfis FROM produtos ORDER BY pd_cfir")
					prd = sql[2].fetchall()
					cod = ""
						
					if c9 !=0:

						EMD = datetime.datetime.now().strftime("%Y/%m/%d")
						DHO = datetime.datetime.now().strftime("%T")
						QTD = 0
							
						for i in prd:
							
							if i[0] !='' and i[0] !=None and i[0] != cod:

								print( "__________: ",len(i[0]),len(i[0].strip() ),i[0] )
								if sql[2].execute("SELECT * FROM tributos WHERE cd_codi='"+str( i[0].strip() )+"'") == 0:
									
									try:

										ncm,cfo,cst,icm = i[0].split('.')
										TB = "INSERT INTO tributos (cd_cdpd,cd_codi,cd_cdt1,cd_cdt2,cd_cdt3,cd_icms) VALUES(%s,%s,%s,%s,%s,%s)"
										gv = sql[2].execute( TB, ( '2',i[0],ncm,cfo,cst,icm ) )
										QTD +=1
										print( i[0],QTD )


									except Exception as _reTornos:	pass
							
							cod = i[0]
									
						sql[1].commit()

#--------------: aJSUTAR icms NO CADASTRO DE TRIBUTOS
				if enTra == 12:
						
					c9 = sql[2].execute("SELECT cd_regi,cd_icms FROM tributos")
					prd = sql[2].fetchall()
					cod = ""
						
					if c9 !=0:

						QTD = 0
							
						for i in prd:
							
							print( i[0],i[1] )
							#if i[0] !='' and i[0] !=None:
								
							if str(i[1]).split(".")[0] == "1900" :
									
								print( i[1] )
								try:
									aT = sql[2].execute("UPDATE tributos SET cd_icms='19.00' WHERE cd_regi='"+str( i[0] )+"'")
								except Exception as _reTornos:
									
									print( "Erro: ",_reTornos)

									
						sql[1].commit()
			

#--------------: Ajuste codigo fiscal p-me
				if enTra == 13:

#00-Registro ID       create table tributos (cd_regi int(8) not null auto_increment primary key,
#01-ID Tributo        cd_cdpd varchar(1)    default '',
#02-Codigo            cd_codi varchar(30)   default '',
#03-NCM               cd_cdt1 varchar(12)   default '',
#04-CFOP              cd_cdt2 varchar(12)   default '',
#05-CST               cd_cdt3 varchar(12)   default '',
						
					c13 = sql[2].execute("SELECT cd_regi,cd_icms,cd_codi,cd_cdt1,cd_cdt2,cd_cdt3 FROM tributos")
					prd = sql[2].fetchall()
					cod = ""
						
					if c13 !=0:
							
						for i in prd:
							
							ncm,cfo,cst,icm = i[2].split(".")

							icm="0000"
							if cst=="060":	cst="0500"
							if cst=="000":	cst="0101"
							
							cf = ncm+"."+cfo+"."+cst+"."+icm
							print( i[2].split('.'),ncm,cfo,cst,icm,cf)
							#if i[0] !='' and i[0] !=None:
								
							
							try:
								aT = sql[2].execute("UPDATE tributos SET cd_codi='"+str(cf)+"',cd_cdt3='"+str(cst)+"',cd_icms='0000' WHERE cd_regi='"+str( i[0] )+"'")
							except Exception as _reTornos:
									
								print( "Erro: ",_reTornos)

									
						sql[1].commit()

#--------------: Codigos Fiscais
				if enTra == 14:
						
					c9 = sql[2].execute("SELECT pd_regi,pd_cfis,pd_cfir,pd_cfsc FROM produtos")
					prd = sql[2].fetchall()
						
					if c9 !=0:
							
						for i in prd:
								
							if i[1] !='' and i[1] !=None:
				
								ncm,cfo,cst,icm = i[1].split(".")
								
								if cst == "0060" or cst=="060":

									ncfis = ncm+"."+cfo+".0500."+icm
									reg = str( i[0] )
									try:
											
											
										#aT = sql[2].execute("UPDATE produtos SET pd_dtal='"+str( EMD )+"',pd_hcal='"+str( DHO )+"',pd_salt='A' WHERE pd_regi='"+str( reg )+"'")
										#aT = sql[2].execute("UPDATE produtos SET pd_cfir='"+str( ncfis )+"' WHERE pd_regi='"+str( reg )+"'")
										aT = sql[2].execute("UPDATE produtos SET pd_cfis='"+str( ncfis )+"' WHERE pd_regi='"+str( reg )+"'")
										print( reg, i[1],ncfis)

									except Exception as _reTornos:	pass
									
						sql[1].commit()

			conn.cls(sql[1])

if __name__ == '__main__':

	os.system("clear")
	
	__srv = configuraistema()
	__srv.dbserver()
	
	aTT = prn()
	aTT.continua()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lobo import *
import datetime
import os
from decimal import *

os.system("clear")


conn = sqldb()
sql  = conn.dbc("Produtos, Alterar Estoque Fisico",1)
grv  = True
saida = input("1-Produto\n2-Clientes\n3-Codigo Fiscal\n4-Contas Areceber { Fazer o Cliente Antes para pegar o cpf,cnpj }\n5-Atualizar dados dos clientes\
\n6-Gravar Codigo em Codigo do produto em controle interno\n7-Plano de Contas\n8-Fornecedor\n\nOpção: ")

codigoFiscal = []
fl = ""
	
if sql[0] == True:

	if saida == 1 or saida == 3:

		arquivo = open("produto.txt")
		rpl = 1
		for i in arquivo.readlines():

			campos = i.split("|")
		
			#cd = campos[3].decode("windows-1252",errors='ignore').strip() #--: Codigo do Produto
			cd = str( rpl ).zfill(14) #campos[3].decode("windows-1252",errors='ignore').strip() #--: Codigo do Produto
			nm = campos[0].decode("windows-1252",errors='ignore').strip() #--: Descricao do Produto
			#cr = campos[2].decode("windows-1252",errors='ignore').strip() #--: Caracteristca do produto
			#rf = campos[3].decode("windows-1252",errors='ignore').strip() #--: Codigo de Referencia
			#br = campos[4].decode("windows-1252",errors='ignore').strip() #--: Codigo de Barras
			un = campos[4].decode("windows-1252",errors='ignore').strip()[:2] #--: Unidade
			gr = campos[1].decode("windows-1252",errors='ignore').strip() #--: Descricao do grupo
			ft = campos[2].decode("windows-1252",errors='ignore').strip() #--: Fabricante
			pv = campos[7].decode("windows-1252",errors='ignore').strip().replace(',','.') #--: Preco de Venda 
			#ef = campos[9].decode("windows-1252",errors='ignore').strip() #--: Estoque Fisico
			uc = '1' #campos[10].decode("windows-1252",errors='ignore').strip() #-: Controle de Baixa 1-Unidde 2-ML 3-M2 4-M3
			#p6 = campos[11].decode("windows-1252",errors='ignore').strip() #-: Preco 6  
			#cm = campos[12].decode("windows-1252",errors='ignore').strip() #-: Comissao de vendas
			mg = campos[6].decode("windows-1252",errors='ignore').strip().replace(',','.') #-: Margem de Lucro
			#pb = campos[14].decode("windows-1252",errors='ignore').strip() #-: Peso Bruto
			#pl = campos[15].decode("windows-1252",errors='ignore').strip() #-: Peso Liquido
			#en = campos[16].decode("windows-1252",errors='ignore').strip() #-: Endereco
			ci = campos[3].decode("windows-1252",errors='ignore').strip() #-: Codigo de Controle Interno
			#p2 = campos[18].decode("windows-1252",errors='ignore').strip() #-: Preco 2
			#p3 = campos[19].decode("windows-1252",errors='ignore').strip() #-: Preco 3
			#p4 = campos[20].decode("windows-1252",errors='ignore').strip() #-: Preco 4
			#p5 = campos[21].decode("windows-1252",errors='ignore').strip() #-: Preco 5
			#u5 = campos[22].decode("windows-1252",errors='ignore').split("|") #-: Ultimas Compras 5
			#u4 = campos[23].decode("windows-1252",errors='ignore').split("|") #-: Ultimas Comrpas 4
			#u3 = campos[24].decode("windows-1252",errors='ignore').split("|") #-: Ultimas Compras 3
			#ms = campos[25].decode("windows-1252",errors='ignore').strip() #-: Margem de Seguranca
			cu = campos[5].decode("windows-1252",errors='ignore').strip().replace(',','.') #-: Preco de Custo 
			pc = campos[5].decode("windows-1252",errors='ignore').strip().replace(',','.') #-: Preco de Compra
			#um = campos[28].decode("windows-1252",errors='ignore').strip() #-: Custo Medio 

			#ec = campos[29].decode("windows-1252",errors='ignore').strip() #-: Codigo do ECF
			#ic = campos[30].decode("windows-1252",errors='ignore').strip() #--: ICMS
			#cs = campos[32].decode("windows-1252",errors='ignore').strip() #--: CST
			#ff = campos[33].decode("windows-1252",errors='ignore').strip() #--: CFOP
			mc = campos[10].decode("windows-1252",errors='ignore').strip() #--: MCN

			#mc = mc.replace('.','').strip()
			#ic = ic.replace('.','').strip()
			#cs = '0'+cs.strip()
			#ic = ic.replace('.','').strip()
			#ff = ff.replace('.','').strip()
            #
			#lb = ""
			#if mc.strip() !='':	lb = mc.strip()+'.'+ff.strip()+'.'+cs.strip()+".0000"
			#if lb !="":
			#	al = lb,mc,ff,cs
			#	codigoFiscal.append(al)
			#	
			#pr2 = pr3 = pr4 = pr5 = "0.00"
			#pc2 = pc2 = pc4 = pc5 = "0.0000"
            #
			#""" Desconto """
			#ad = "D"
			#if Decimal( p2 ) > 0 and Decimal( pv ) > 0 and Decimal( p2 ) < Decimal( pv ):
			#	pr2 = format( ( ( Decimal( pv ) - Decimal( p2 ) ) / Decimal( pv ) * 100 ), '.2f' )
            #
			#if Decimal( p3 ) > 0 and Decimal( pv ) > 0 and Decimal( p3 ) < Decimal( pv ):
			#	pr3 = format( ( ( Decimal( pv ) - Decimal( p3 ) ) / Decimal( pv ) * 100 ), '.2f' )
			#	
			#if Decimal( p4 ) > 0 and Decimal( pv ) > 0 and Decimal( p4 ) < Decimal( pv ):
			#	pr4 = format( ( ( Decimal( pv ) - Decimal( p4 ) ) / Decimal( pv ) * 100 ), '.2f' )
            #
			#if Decimal( p5 ) > 0 and Decimal( pv ) > 0 and Decimal( p5 ) < Decimal( pv ):
			#	pr5 = format( ( ( Decimal( pv ) - Decimal( p5 ) ) / Decimal( pv ) * 100 ), '.2f' )
            #
			#""" Acrescimo """
            #
			#if Decimal( p2 ) > 0 and Decimal( pv ) > 0 and Decimal( p2 ) > Decimal( pv ):
			#	pr2 = format( ( ( Decimal( p2 ) - Decimal( pv ) ) / Decimal( pv ) * 100 ), '.2f' )
			#	ad = "A"
			#	
			#if Decimal( p3 ) > 0 and Decimal( pv ) > 0 and Decimal( p3 ) > Decimal( pv ):
			#	pr3 = format( ( ( Decimal( p3 ) - Decimal( pv ) ) / Decimal( pv ) * 100 ), '.2f' )
			#	ad = "A"
			#	
			#if Decimal( p4 ) > 0 and Decimal( pv ) > 0 and Decimal( p4 ) > Decimal( pv ):
			#	pr4 = format( ( ( Decimal( p4 ) - Decimal( pv ) ) / Decimal( pv ) * 100 ), '.2f' )
			#	ad = "A"
            #
			#if Decimal( p5 ) > 0 and Decimal( pv ) > 0 and Decimal( p5 ) > Decimal( pv ):
			#	pr5 = format( ( ( Decimal( p5 ) - Decimal( pv ) ) / Decimal( pv ) * 100 ), '.2f' )
			#	ad = "A"
            #
			#if Decimal( pr2 )+Decimal( pr3 )+Decimal( pr4 )+Decimal( pr5 ) > 0:
			#	print ad," >-> _____________________: ",pr2,pr3,pr4,pr5
			#
            #
			#m6 = "0.000" #-: Magem 6
			#if len(pv) > 11:	pv = "0.000"
			#if saida == 1:	print "Produto: ",lb,nm
			#if saida == 3:	print "Codigo Fiscal: ",lb,nm
			#
			#_con = "T" #-: Controlar
			#_des = "T" #-: Permitir desconto
			#_fra = "F" #-: Fracionar
			#
			#if uc == "1":	_fra = "T"
			#
			
			controle = '1'
			if un == 'ML':	controle = '2'
			if un == 'M2':	controle = '3'
			if un == 'M3':	controle = '4'
			
			voltar = "INSERT INTO tributos (cd_cdpd,cd_codi,cd_cdt1,cd_cdt2,cd_cdt3) VALUES(%s,%s,%s,%s,%s)"
			
			gravar = "INSERT INTO produtos (pd_codi,pd_nome,pd_unid,pd_pcom,pd_pcus,pd_marg,pd_fabr,pd_tpr1,pd_nmgr,pd_mdun,pd_intc)\
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
			if saida == 1:	sql[2].execute(gravar,(cd,nm,un,pc,cu,mg,ft,pv,gr,controle,ci))
			rpl +=1
			arquivo.close()
    
		#mmm = ""
		#num = 1
		#cod = 1
		#for ccf in sorted( codigoFiscal ):
			
		#	if mmm !=ccf:

		#		if saida == 3 and lb != ccf:	sql[2].execute(voltar,( "2", ccf[0], ccf[1], ccf[2], ccf[3] ))


		#		if saida == 3:	print ccf,cod
		#		cod +=1
		#	mmm = ccf
		#	if saida == 3:	print num
		#	num +=1
		
	elif saida == 2 or saida == 5:
		""" Clientes  """	
		clientes = open("clientes.txt")
		rcl = 1

		for i in clientes.readlines():

			camposs = i.split("|")
			
			cnm = camposs[1].decode("windows-1252",errors='ignore').strip()[:50] #--: Nome]
			cft = camposs[0].decode("windows-1252",errors='ignore').strip() #--: Fantasia
			cdc = camposs[5].decode("windows-1252",errors='ignore').strip() #--: documento -cpf
			doc = camposs[6].decode("windows-1252",errors='ignore').strip() #--: documento - cnpj
			cen = camposs[8].decode("windows-1252",errors='ignore').strip() #--: endereco
			cba = camposs[11].decode("windows-1252",errors='ignore').strip()[:20] #--: bairro
			cid = camposs[12].decode("windows-1252",errors='ignore').strip()[:20] #--: cidade
			est = camposs[13].decode("windows-1252",errors='ignore').strip() #--: estado
			cep = camposs[14].decode("windows-1252",errors='ignore').strip() #--: cep
			#ibg = camposs[8].decode("windows-1252",errors='ignore').strip() #--: ibge
			cm1 = camposs[9].decode("windows-1252",errors='ignore').strip()[:5] #--: complemenot1
			cm2 = camposs[10].decode("windows-1252",errors='ignore').strip()[:20] #-: complemento2
			ies = camposs[7].decode("windows-1252",errors='ignore').strip() #-: Email 
			te1 = camposs[2].decode("windows-1252",errors='ignore').strip() #--: TEl1
			te2 = camposs[1].decode("windows-1252",errors='ignore').strip() #--: Tel2
			#te3 = camposs[14].decode("windows-1252",errors='ignore').strip() #--: Tel3
			#em1 = camposs[15].decode("windows-1252",errors='ignore').strip() #--: Email 1
			#em2 = camposs[16].decode("windows-1252",errors='ignore').strip() #--: Email 2
			#fac = camposs[17].decode("windows-1252",errors='ignore').strip() #--: Face Book
			#twi = camposs[18].decode("windows-1252",errors='ignore').strip() #--: Twiter
			#lim = camposs[19].decode("windows-1252",errors='ignore').strip() #--: Limite de Credito
			#tab = camposs[20].decode("windows-1252",errors='ignore').strip() #--: Tabela
			#cod = camposs[21].decode("windows-1252",errors='ignore').strip() #--: Codigo
			
			#if len( cep.split('-') ) == 2:	cep = cep.split('-')[0]+cep.split('-')[1]

			#cnm #--: Nome]
			#cft #--: Fantasia
			#cdc #--: documento -cpf
			#doc #--: documento - cnpj
			#cen #--: endereco
			#cba #--: bairro
			#cid #--: cidade
			#est #--: estado
			#cep #--: cep
			#cm1 #--: complemenot1
			#cm2 #-: complemento2
			#ies #-: Email 
			#te1 #--: TEl1
			#te2 #--: Tel2
			#te3 #--: Tel3


			#cnm,cft,cdc,doc,cen,cba,cid,est,cep,cm1,cm2,ies,te1,te2,te3
			_cdoc = cdc if cdc.strip() else doc
			_tel1 = te1 if len( te1 )<=10 else ''
			_tel2 = te2 if len( te2 )<=10 else ''
			_iest = ies if ies.isdigit() else ''

			_rdes = ''
			if len( te1 ) > 10:	_rdes +=te1+'\n'
			if len( te2 ) > 10:	_rdes +=te2+'\n'
			
			print "Nome......: ",cnm
			print "Fantisia..: ",cft
			print "CPF.......: ",cdc
			print "CNPJ......: ",doc
			print "Documento.: ",_cdoc
			print "Endereço..: ",cen
			print "Bairro....: ",cba
			print "Cidade....: ",cid
			print "Estado....: ",est
			print "CEP.......: ",cep
			print "CPL_1.....: ",cm1
			print "CPL_2.....: ",cm2
			print "I.E.......: ",ies
			print "Telefone_1: ",te1
			print "Telefone_2: ",te2
			print("-"*200)

                
			codigo = str( rcl )+'-MATRX'
			_grva = "INSERT INTO clientes (cl_nomecl,cl_fantas,cl_docume,cl_endere,cl_bairro,cl_cidade,cl_cepcli,cl_estado,cl_telef1,cl_telef2,cl_indefi,cl_compl1,cl_compl2,cl_iestad,cl_redeso,cl_codigo)\
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

			sql[2].execute( _grva, ( cnm,cft,_cdoc,cen,cba,cid,cep,est,_tel1,_tel2,'MATRX',cm1,cm2,_iest,_rdes,codigo ) )
			
			
			#ibg = ibg.encode("UTF-8").replace('/',' ')
			#cm1 = cm1.encode("UTF-8").replace('/',' ')
			#cm2 = cm2.encode("UTF-8").replace('/',' ')

			#ibg = ibg.split("\ ")[0]
			#cm1 = cm1.split("\ ")[0]
			#cm2 = cm2.split("\ ")[0]


			#print ibg,len(ibg)
			#print cm1,len(cm1)
			#print cm2,len(cm2)

			#_aTua = "UPDATE clientes SET cl_cepcli='"+str( cep )+"',cl_cdibge='"+str( ibg )+"',cl_compl1='"+str( cm1 )+"',cl_compl2='"+str( cm2 )+"' WHERE cl_cdsimm='"+str( cod )+"'"

			#if saida == 2:	sql[2].execute(_grva,(cnm,cft,cdc,cen,cba[:20],cid[:20],cep,est[:2],ema,te1[:13],te2[:13],fl,cod,ibg,cm1,cm2))
			#if saida == 5:	sql[2].execute(_aTua)
			
			#print "Cliente: ",rcl,cnm,len(camposs)

			
			rcl +=1

	elif saida == 4:
	
		""" Contas Areceber """
		b='select count(*) from receber'
		a = open('recebers.txt')
		sql[2].execute(b)		
		_nregs1=sql[2].fetchone()[0]

		bla=0
		for i in a.readlines():

			b = i.split('|')
			c = [x.strip() for x in b]

			_docu = c[0][:12].strip()
			_nont = c[1].strip()
			_valr = c[2]
			_vapa = c[3]
			_usla = c[4].split(' ')[0] .strip()
			_dtla = datetime.datetime.strptime(c[5][:6]+"20"+c[5][6:],'%d-%m-%Y').strftime("%Y-%m-%d")
			_dtvc = datetime.datetime.strptime(c[6][:6]+"20"+c[6][6:],'%d-%m-%Y').strftime("%Y-%m-%d")
			_clcd = c[7] #str(int(c[7])).strip()
			_clnm = c[8].decode("windows-1252",errors='ignore').strip()
			_clnm = _clnm.encode('utf-8').strip()
			_parc = c[0].split('/')[1].strip()
			_hora = c[4][len(c[4])-8:].strip()
			_form = c[9].zfill(2)+"-"+c[10].strip()
			_cpfc = c[11]
			_cnpj = c[12] 
			dc = ""
			if _clcd !="" and sql[2].execute("SELECT cl_docume FROM clientes WHERE cl_cdsimm='"+str( _clcd )+"'") !=0:	dc = sql[2].fetchall()[0][0]
			if dc == "" and _cpfc !="":	dc = _cpfc	
			if dc == "" and _cnpj !="":	dc = _cnpj	
				 
			print "______________CPF,CNPJ: ",dc,_clcd
		
			if _clcd !="":	_clcd = str( int( _clcd ) )
	
			
			gravar = "INSERT INTO receber (rc_ndocum,rc_nparce,rc_vlorin,rc_apagar,rc_formap,rc_dtlanc,rc_hslanc,rc_loginc,rc_clcodi,rc_clnome,rc_vencim,rc_cpfcnp,rc_indefi)\
			values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
			
			sql[2].execute(gravar,(_docu,_parc,_valr,_vapa,_form,_dtla,_hora,_usla,_clcd,_clnm,_dtvc,dc,fl))
			
			bla +=1


	elif saida == 6: #-: Gravar codigo do produto em codigo de controle interno
	
		""" produtos """
		if sql[2].execute("select pd_regi,pd_codi from produtos") !=0:
			
			rPro = sql[2].fetchall()
			nRgs = 1
			
			for i in rPro:
				
				
				print nRgs,i[0],i[1]
				
				auTo = "UPDATE produtos SET pd_intc='"+str( i[1] )+"' WHERE pd_regi='"+str( i[0] )+"'"
				#sql[2].execute(auTo)
				nRgs +=1

	elif saida == 7: #-: Plano de Contas

		if sql[2].execute("select * from plcontas") !=0:
			
			rPro = sql[2].fetchall()
			nRgs = 1
			
			for i in rPro:
		
				conta = ""
				regis = i[0]
				if len( i[1].split('.') ) == 3:
					
					a1 = i[1].split('.')[0]
					a2 = i[1].split('.')[1]
					a3 = i[1].split('.')[2].zfill(2)
					conta = a1+"."+a2+"."+a3

				if len( i[1].split('.') ) == 4:
					
					a1 = i[1].split('.')[0]
					a2 = i[1].split('.')[1]
					a3 = i[1].split('.')[2].zfill(2)
					a4 = i[1].split('.')[3]
					conta = a1+"."+a2+"."+a3+"."+a4
				
				if conta !="":
					
					cnT = "UPDATE plcontas SET pl_nconta='"+str( conta )+"' WHERE pl_regist='"+str( regis )+"'"
					sql[2].execute(cnT)
					print regis,conta


	elif saida == 8:
		""" fornecedor  """	
		clientes = open("fornecedor.txt")
		rcl = 1

		for i in clientes.readlines():

			camposs = i.split("|")

			cod = camposs[0].decode("windows-1252",errors='ignore').strip() #--: Nome]
			nom = camposs[1].decode("windows-1252",errors='ignore').strip() #--: Nome]
			fan = camposs[2].decode("windows-1252",errors='ignore').strip() #--: Nome]
 			doc = camposs[5].decode("windows-1252",errors='ignore').strip() #--: Nome]
			ies = camposs[6].decode("windows-1252",errors='ignore').strip().replace(".","") #--: Nome]
			end = camposs[8].decode("windows-1252",errors='ignore').strip() #--: Nome]
			bai = camposs[9].decode("windows-1252",errors='ignore').strip() #--: Nome]
			cid = camposs[10].decode("windows-1252",errors='ignore').strip() #--: Nome]
			ibg = camposs[11].decode("windows-1252",errors='ignore').strip() #--: Nome]
			cep = camposs[12].decode("windows-1252",errors='ignore').strip().replace('-','') #--: Nome]
			cp1 = camposs[13].decode("windows-1252",errors='ignore').strip() #--: Nome]
			cp2 = camposs[14].decode("windows-1252",errors='ignore').strip() #--: Nome]
			est = camposs[15].decode("windows-1252",errors='ignore').strip() #--: Nome]
			ema = camposs[16].decode("windows-1252",errors='ignore').strip() #--: Nome]
			tl1 = camposs[17].decode("windows-1252",errors='ignore').strip().replace(" ","") #--: Nome]
			tl2 = camposs[18].decode("windows-1252",errors='ignore').strip().replace(" ","") #--: Nome]
			tl3 = camposs[19].decode("windows-1252",errors='ignore').strip().replace(" ","") #--: Nome]

			print "Codigo...: ",cod
			print "Nome.....: ",nom
			print "Fantasia.: ",fan
			print "Documento: ",doc
			print "I.E......: ",ies
			print "Endreco..: ",end
			print "Bairro...: ",bai
			print "Cidade...: ",cid
			print "Ibge.....: ",ibg
			print "CEP......: ",cep
			print "Compl-1..: ",cp1
			print "Compl-2..: ",cp2
			print "Estado...: ",est
			print "Email....: ",ema
			print "Telefone1: ",tl1
			print "Telefone2: ",tl2
			print "Telefone3: ",tl3

			_grva = "INSERT INTO fornecedor (fr_docume,fr_insces,fr_nomefo,fr_fantas,fr_endere,fr_numero,fr_comple,fr_bairro,fr_cidade,fr_cepfor,fr_estado,fr_cmunuc,fr_telef1,fr_telef2,fr_telef3,fr_emails,fr_idfila,fr_tipofi)\
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

			sql[2].execute( _grva, ( doc,ies,nom,fan,end,cp1,cp2,bai,cid,cep,est,ibg,tl1,tl2,tl3,ema,'MCFIX','1' ) )
				
	sql[1].commit()
    

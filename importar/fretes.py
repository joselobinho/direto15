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

		arquivo = open("fretesmonfardini.csv")
		rpl = 1
		for i in arquivo.readlines():

			campos = i.split("|")
		
			br = campos[0] #.decode("windows-1252",errors='ignore')
			mu = campos[1] #.decode("windows-1252",errors='ignore')
			vl = campos[2] #.decode("windows-1252",errors='ignore')
			es = "RJ"
			print br,mu,vl,es

			#00-ID Lancamento   create table fretes (ft_regist int(10) not null auto_increment primary key,
			#01-Estado          ft_estado varchar(2) default '',
			#02-Municipio       ft_munici varchar(60) default '',
			#03-Bairro          ft_bairro varchar(60) default '',
			#04-Valor           ft_valorf decimal(15,2)  not null default 0,
			#05-CadastroAltera  ft_ajuste text);



			




			
			#print("Saida: ",cu)
			#if not pc:	pc = "0.00"
			#if not cu:	cu = "0.00"
			#voltar = "INSERT INTO tributos (cd_cdpd,cd_codi,cd_cdt1,cd_cdt2,cd_cdt3) VALUES(%s,%s,%s,%s,%s)"
			gravar = "INSERT INTO fretes (ft_estado,ft_munici,ft_bairro,ft_valorf)\
			VALUES(%s,%s,%s,%s)"
			sql[2].execute(gravar,(es, mu, br, vl))

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
			
			cnm = camposs[0].decode("windows-1252",errors='ignore').strip() #--: Nome]
			cft = camposs[1].decode("windows-1252",errors='ignore').strip() #--: Fantasia
			cdc = camposs[2].decode("windows-1252",errors='ignore').strip() #--: documento
			cen = camposs[3].decode("windows-1252",errors='ignore').strip() #--: endereco
			cba = camposs[4].decode("windows-1252",errors='ignore').strip() #--: bairro
			cid = camposs[5].decode("windows-1252",errors='ignore').strip() #--: cidade
			est = camposs[6].decode("windows-1252",errors='ignore').strip() #--: estado
			cep = camposs[7].decode("windows-1252",errors='ignore').strip() #--: cep
			ibg = camposs[8].decode("windows-1252",errors='ignore').strip() #--: ibge
			cm1 = camposs[9].decode("windows-1252",errors='ignore').strip() #--: complemenot1
			cm2 = camposs[10].decode("windows-1252",errors='ignore').strip() #-: complemento2
			ema = camposs[11].decode("windows-1252",errors='ignore').strip() #-: Email 
			te1 = camposs[12].decode("windows-1252",errors='ignore').strip() #--: TEl1
			te2 = camposs[13].decode("windows-1252",errors='ignore').strip() #--: Tel2
			te3 = camposs[14].decode("windows-1252",errors='ignore').strip() #--: Tel3
			em1 = camposs[15].decode("windows-1252",errors='ignore').strip() #--: Email 1
			em2 = camposs[16].decode("windows-1252",errors='ignore').strip() #--: Email 2
			fac = camposs[17].decode("windows-1252",errors='ignore').strip() #--: Face Book
			twi = camposs[18].decode("windows-1252",errors='ignore').strip() #--: Twiter
			lim = camposs[19].decode("windows-1252",errors='ignore').strip() #--: Limite de Credito
			tab = camposs[20].decode("windows-1252",errors='ignore').strip() #--: Tabela
			cod = camposs[21].decode("windows-1252",errors='ignore').strip() #--: Codigo
			ies = camposs[22].decode("windows-1252",errors='ignore').strip().replace(".","").replace("ISENTO","") #--: Codigo
			
			if len( cep.split('-') ) == 2:	cep = cep.split('-')[0]+cep.split('-')[1]


				
			_grva = "INSERT INTO clientes (cl_nomecl,cl_fantas,cl_docume,cl_endere,cl_bairro,cl_cidade,cl_cepcli,cl_estado,cl_emailc,cl_telef1,cl_telef2,cl_indefi,cl_cdsimm,\
			cl_cdibge,cl_compl1,cl_compl2,cl_iestad)\
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
			%s,%s,%s,%s)"
			
			ibg = ibg.encode("UTF-8").replace('/',' ')
			cm1 = cm1.encode("UTF-8").replace('/',' ')
			cm2 = cm2.encode("UTF-8").replace('/',' ')

			#ibg = ibg.split("\ ")[0]
			#cm1 = cm1.split("\ ")[0]
			#cm2 = cm2.split("\ ")[0]


			print ibg,len(ibg)
			print cm1,len(cm1)
			print cm2,len(cm2)

			_aTua = "UPDATE clientes SET cl_cepcli='"+str( cep )+"',cl_cdibge='"+str( ibg )+"',cl_compl1='"+str( cm1 )+"',cl_compl2='"+str( cm2 )+"' WHERE cl_cdsimm='"+str( cod )+"'"

			if saida == 2:	sql[2].execute(_grva,(cnm,cft,cdc,cen,cba[:20],cid[:20],cep,est[:2],ema,te1[:13],te2[:13],fl,cod,ibg,cm1,cm2,ies))
			if saida == 5:	sql[2].execute(_aTua)
			
			print "Cliente: ",rcl,cnm,len(camposs)
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
    

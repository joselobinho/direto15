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

#		arquivo = open("mesquita.csv")
		arquivo = open("produtos.csv")
		rpl = 1
		aa = 1
		codigos = 1
		for i in arquivo.readlines():
			if i:

			    s = i.replace("\n","").split("|")
			    #print len(s),s
			    
			    nome,codigo,unidade,compra,venda,venda2,mestoque, estoque = s
			    nome=nome.replace(',',' ').replace("'",' ')
			    if '-' in estoque:	estoque='0.0000'
			    print nome,codigo,unidade,compra,venda,venda2,mestoque,estoque
			    
			    #['"PRODUTOS"', '"COD.BARRA"', '"UNIDADE"', '"vr_compra"', '"vr_venda"', '"vr_venda_2"', '"min_estoque"', '"estoque"\n']
			    #print ('-'*100)
			    #print nome,codigo,unidade,compra,venda,venda2,mestoque,estoque
			    #print len(i.split('}'))
			    #codigo,nome,un,ncm,cfop,cst,icms,QT,custo,margem,vendas = i.replace("\n","")
			    #nome = nome.replace('|','').replace("]","").decode("windows-1252",errors='ignore').strip()
			    #cest = cest.replace('.','')
			    #vendas = vendas.replace(',','.')
			    #custo = custo.replace(',','.')
			    #margem = margem.replace(' %','').replace(',','.')
			    #cfis = ncm+'.'+cfop+'.'+cst.zfill(4)+'.0000'
			    #if codigo[:1]=="7":	barra=codigo
			    #else:	barra=""
			    
			    #if un=='PÃƒ':	un='PA'
			    #if un=='P€':	un='PC'
			    #print cfis,nome,custo,margem,vendas
			    #if len(un) > 2:
			#	print un,'**********************************************************************'
			    
#			    if not ncm.strip():	ncm='00000000'
#			    cf = ncm.replace('.','')+'.'+cfop.replace('.','')+'.0'+cst+'.0000' if cfop.strip()  and cst.strip() else ''
#			    cf = ncm.zfill(8)+'.0000.0000.0000'
			    #print('------Valor: ', venda,ef,str(preco2),str(preco3),str(preco4),str(preco5),str(preco6)) #, ncm
			    #if not ef:	ef='0.0000'
			    nome,codigo,unidade,compra,venda,venda2,mestoque, estoque
			    gravar = "INSERT INTO produtos (pd_codi, pd_barr,pd_nome, pd_unid, pd_mdun, pd_tpr1, pd_tpr2, pd_pcom, pd_pcus, pd_estm) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
			    sql[2].execute( gravar, ( str(codigos).zfill(14),codigo,nome,unidade[:2],'1',str(venda),str(venda2),compra,compra,mestoque) )
			    #39269090.5405.0500.0000
			 #   gravar = "INSERT INTO produtos (pd_codi, pd_barr, pd_nome, pd_unid, pd_mdun, pd_pcus,pd_tpr1, pd_cfis) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
			  #  sql[2].execute( gravar, ( str(codigos).zfill(14),barra,nome,un[:2],'1',custo,str(vendas),cfis) )
			  #	  pc = '1'
			    #if un=='ML':	pc = '2'
			    #if un=='M2':	pc = '3'
			    #if un=='M3':	pc = '4'
#			    #gravar = "INSERT INTO produtos (pd_codi, pd_nome, pd_unid, pd_cfis,pd_mdun) VALUES(%s, %s, %s, %s,%s)"
#			    nome=nome.replace('ﾁ','A')
#			    try:
#				sql[2].execute( gravar, ( str(codigos).zfill(14),nome,un[:2],cf,pc) )
#			    except:
#				print(nome)
#				sql[2].execute( gravar, ( str(codigos).zfill(14),nome[:-2],un[:2],cf,pc) )
#			    codigos+=1
				#codigo,nome,un,barra,margem,icm,custo,venda,controle,cest,cst,preco2,preco3,preco4,preco5,preco6,ncm,cfop
			#if sql[2].execute("SELECT pd_nome FROM produtos WHERE pd_codi='"+codigo+"'"):
				#print(sql[2].fetchall())
			#	sql[2].execute("UPDATE produtos SET pd_barr='"+barra+"' WHERE pd_codi='"+codigo+"'")

#%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s

				#if un == "M2":	controle_un = "3"
				#if un == "M3":	controle_un = "4"
				#codigo_fiscal = ''
				#if ncm: # and cst=='41':
					
				#	codigo_fiscal = ncm+'.'
				#	if cst == '0':	cst = '101'
				#	if cst == '101':	cfop = '5102'
				#	if cst == '60':	cfop = '5405'
				#	if cst == '20':	cfop = '5102'
				#	codigo_fiscal = ncm+'.'+cfop+'.'+cst.zfill(4)+'.0000'
				
			#aa +=1
				#print( codigo,codigo_fiscal,aa)

			    """
			    if len(i.split('|'))==26:
				_id, nome_produto, cod_barra, unidade, inf_adicional, pontos, id_moeda, modo_estoque, grade, kit, id_tipo, vr_compra, vr_venda, vr_venda_2, min_estoque, estoque, inativo, aliq_ipi, inside_icms_ipi, id_class_fiscal, aliq_id_base_icms, origem_produto, fracionado,vazio,vv,vv1 = i.split('|')
			    elif len(i.split('|'))==25:
				_id, nome_produto, cod_barra, unidade, inf_adicional, pontos, id_moeda, modo_estoque, grade, kit, id_tipo, vr_compra, vr_venda, vr_venda_2, min_estoque, estoque, inativo, aliq_ipi, inside_icms_ipi, id_class_fiscal, aliq_id_base_icms, origem_produto, fracionado,vazio,vv = i.split('|')
			    else:
				_id, nome_produto, cod_barra, unidade, inf_adicional, pontos, id_moeda, modo_estoque, grade, kit, id_tipo, vr_compra, vr_venda, vr_venda_2, min_estoque, estoque, inativo, aliq_ipi, inside_icms_ipi, id_class_fiscal, aliq_id_base_icms, origem_produto, fracionado,vazio = i.split('|')

			    print 'Produto: ',nome_produto
			    print 'Barras.: ',cod_barra
			    print 'Compra.: ',vr_compra
			    print 'Venda..: ',vr_venda
			    print 'Venda1.: ',vr_venda_2
			    print 'Minimo.: ',min_estoque
			    print 'IPI....: ',aliq_ipi
			    print 'IN-IPI.: ',inside_icms_ipi
			    print 'CLFisca: ',id_class_fiscal
			    print 'ICMS...: ',aliq_id_base_icms
			    print 'Origem.: ',origem_produto
			    print 'Fracao.: ',fracionado
			    print('-'*129)
			    #codigo

			    np=nome_produto.strip()
			    vc=vr_compra.strip()
			    vd=vr_venda.strip()
			    v1=vr_venda_2.strip()
			    un=unidade.strip()
			    cd=str(codigos).zfill(14)
			    """

			    #sql[2].execute("INSERT INTO produtos ( pd_codi, pd_nome, pd_unid, pd_pcom, pd_pcus, pd_mdun, pd_tpr1,pd_tpr2, pd_prod )\
			    #VALUES( '"+cd+"','"+np+"','UN','"+vc+"','"+vc+"','1','"+vd+"','"+v1+"','T')")
			    
				#grava = "INSERT INTO produtos ( pd_codi, pd_nome, pd_refe, pd_unid, pd_nmgr, pd_fabr, pd_pcom, pd_pcus, pd_mdun, pd_tpr1, pd_cfis, pd_prod )\
				#VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"
				#sql[2].execute( grava, ( codigo, nomepd, refe, un, grupo, fab, custos, custos, controle_un, venda1, codigo_fiscal, 'T' ))
				#rpl +=1
				#if len( campos ) >=4 and not campos[2].isdigit():
				
				#codigo = str( campos[1] ).zfill(14)
				#descricao = campos[2].upper().decode("windows-1252",errors='ignore')
				#codigo_barras = campos[3] if int( campos[3] ) else ''
				#print( codigo, descricao,codigo_barras )
				#gravar = "INSERT INTO produtos (pd_codi,pd_nome,pd_unid,pd_mdun,pd_barr) VALUES( %s,%s,%s,%s,%s)"
				#sql[2].execute( gravar, ( codigo,descricao,'UN',"1",codigo_barras) )
			
			codigos+=1

			"""
			cd = campos[0] #.decode("windows-1252",errors='ignore').strip().zfill(14) #--: Codigo do Produto
			nm = campos[1] #.decode("windows-1252",errors='ignore').strip() #--: caracteristica
			un = "UN" #campos[7][:2] #.decode("windows-1252",errors='ignore').strip()[:2] #--: Unidade
			pv = campos[3].replace(",","") #.decode("windows-1252",errors='ignore').strip() #--: Preco de Venda 
			uc = "1" #campos[10].decode("windows-1252",errors='ignore').strip() #-: Controle de Baixa 1-Unidde 2-ML 3-M2 4-M3
			#p6 = campos[4] #.decode("windows-1252",errors='ignore').strip() #-: Preco 6  
			#mg = campos[8] #.decode("windows-1252",errors='ignore').strip() #-: Margem de Lucro
			cu = campos[4].replace(",","") #.decode("windows-1252",errors='ignore').strip() #-: Preco de Custo 
			cm = campos[4].replace(",","") #.decode("windows-1252",errors='ignore').strip() #-: Preco de Custo 
			#pc = campos[2] #.decode("windows-1252",errors='ignore').strip() #-: Preco de Compra
			ef = campos[2].replace(',','') #.decode("windows-1252",errors='ignore').strip() #-: Preco de Compra
			#em = campos[6].replace(',','.') #.decode("windows-1252",errors='ignore').strip() #-: Preco de Compra
			ncm = campos[5]
			cfo = campos[6]
			cst = campos[8].zfill(4)
			ces = campos[9].replace('.','')
			
			cdf = ncm+'.'+cfo+'.'+cst+'.'+'0000'
			#print cd,nm,un,pv,uc,p6,mg,cu,cm,pc,em
			#83013000.5403.0500.0000
			#print("Saida: ",cu)
			#if not pc:	pc = "0.00"
			if not cu:	cu = "0.00"
			#voltar = "INSERT INTO tributos (cd_cdpd,cd_codi,cd_cdt1,cd_cdt2,cd_cdt3) VALUES(%s,%s,%s,%s,%s)"
			#gravar = "INSERT INTO produtos (pd_codi,pd_nome,pd_unid,pd_pcom,pd_pcus,pd_marg,pd_cupf,pd_tpr1,pd_tpr6,pd_mdun)\
			print cd,nm,un,cu,cu,'F',pv,uc,cdf,ef,ces
			gravar = "INSERT INTO produtos (pd_codi,pd_nome,pd_unid,pd_pcom,pd_pcus,pd_cupf,pd_tpr1,pd_mdun,pd_cfis,pd_estf,pd_cest)\
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
			sql[2].execute(gravar,(cd,nm,un,cu,cu,'F',pv,uc,cdf,ef,ces))
			"""
			#arquivo.close()
    
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
		clientes = open("clientes.csv").readlines()
		rcl = 1
		aa=1
		clcd = 1

		for i in clientes: #mc.split('\n'):
		    if i:
			codigos=str(clcd).zfill(8)+'-QUIFE'
			clcd +=1
			#print len(i.split('#')),i.split('#')
			nome,cep,endereco,bairro,cidade,uf,email,tel1,tel2,doc,ie,complemento=i.split('#')
			#print nome,cep,endereco,bairro,cidade,email,tel1,tel2,doc,ie,complemento
			#print len(i.split('|')),i
			#_fantas=''
			#_cdibge=''
			#_compl1=''
			#_compl2=''
			#_telef3=''
			#_nomecl, _fantas, _docume, _iestad, _imunic, _endere, _bairro, _cidade, _cdibge, _cepcli,_compl1, _compl2, _estado, _emailc, _telef1, _telef2, _telef3, _valorm = i.split('|')

			#if len(i.split('|'))==27:
			#    x_id,xcb,_nomecl,_cepcli,_endere,_bairro,_cidade,_estado,_emailc,_telef1,_telef2,_docume,_iestad,xinfad,xfs,xvc,xdes,xsc,xpot,xenv,xina,_nascd,_nascm,_nasca,xcad,xula,vazio=i.split('|')
			#elif len(i.split('|'))==28:
			#    x_id,xcb,_nomecl,_cepcli,_endere,_bairro,_cidade,_estado,_emailc,_telef1,_telef2,_docume,_iestad,xinfad,xfs,xvc,xdes,xsc,xpot,xenv,xina,_nascd,_nascm,_nasca,xcad,xula,vazio,vv=i.split('|')
			#    
			    
			    
			#_nomecl=_nomecl.strip()
			#_fantas=_fantas.strip() 
			#_docume=_docume.strip() 
			#_iestad=_iestad.strip() 
			#_endere=_endere.strip()[:45]
			#_bairro=_bairro.strip()[:20] 
			#_cidade=_cidade.strip()[:20]
			#_cdibge=_cdibge.strip() 
			#_cepcli=_cepcli.strip()[:9]
			#_compl1=_compl1.strip() 
			#_compl2=_compl2.strip() 
			#_estado=_estado.strip()[:2]
			#_telef1=_telef1.strip().split(' ')[0]
			#_telef2=_telef2.strip().split(' ')[0]
			#_telef3=_telef3.strip()
			#if not _iestad.isdigit():	_iestad=''
			#if not _telef1.isdigit():	_telef1=''
			#if not _telef2.isdigit():	_telef2=''
			#print '------------------: ',_telef1
			#print type(_nomecl),_nomecl, _fantas, _docume, _iestad, _endere, _bairro, _cidade, _cdibge, _cepcli,_compl1, _compl2, _estado, _telef1, _telef2, _telef3
			#nome,cep,endereco,bairro,cidade,email,tel1,tel2,doc,ie,complemento
			if endereco.strip()=='0':	endereco=''
			if len(tel1)>13:
			    tel2+=' '+tel1
			    tel1=''
			    
			print len(endereco),endereco,tel1,bairro,codigos
			_grva ="INSERT INTO clientes (cl_nomecl, cl_docume, cl_iestad, cl_endere, cl_bairro, cl_cidade, cl_cepcli, cl_refere, cl_estado, cl_telef1, cl_redeso, cl_indefi,cl_codigo)\
			VALUES('"+nome+"', '"+doc.strip()+"', '"+ie.strip()+"', '"+endereco[:45]+"', '"+bairro[:20]+"', '"+cidade+"', '"+cep+"','"+complemento+"', '"+uf+"', '"+tel1+"', '"+tel2+"', 'QUIFE','"+codigos+"')"
#			sql[2].execute( _grva, (nome,  doc.strip(), ie.strip(), endereco[:45], bairro[:20], cidade, cep,complemento, uf, tel1, tel2, 'QUIFE',codigos))
			#_grva ="INSERT INTO clientes (cl_nomecl, cl_fantas, cl_docume, cl_iestad, cl_endere, cl_bairro, cl_cidade, cl_cdibge, cl_cepcli,cl_compl1, cl_compl2, cl_estado, cl_telef1, cl_telef2, cl_telef3, cl_indefi,cl_codigo)\
			#VALUES('"+_nomecl+"','"+_fantas+"','"+_docume+"','"+_iestad+"','"+_endere+"','"+_bairro+"','"+_cidade+"','"+_cdibge+"','"+_cepcli+"','"+_compl1+"','"+_compl2+"','"+_estado+"','"+_telef1+"','"+_telef2+"','"+_telef3+"','CFORT','"+codigos+"')"
			sql[2].execute( _grva)

#			_grva ="INSERT INTO clientes (cl_nomecl) VALUES(%s)"
#			sql[2].execute("INSERT INTO clientes (cl_nomecl) VALUES('"+_nomecl+"')")







			#codigos+=1
#id, 
#cod_barra,
#nome_cliente,
#cep, 
#endereco, 
#bairro, 
#cidade, 
#uf, 
#email, 
#telefone, 
#celular, 
#cpf_cnpj, 
#rg_ie, 
#inf_adicional, faixa_salarial, vr_maximo_compra, desconto_autom, saldo_compras, pontos, enviar_email, inativo, nascimento_dia, nascimento_mes, nascimento_ano, data_cadastro, data_ultima_alteracao



			"""
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
			"""
			
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
#		clientes = open("fornecedor.csv")
		clientes = open("fornecedor.csv")
		rcl = 1

		for i in clientes.readlines():
		    if i:
			#print i.replace('\n','').split("|")
			#nome,cnpj,ie,cep,ende,num,comp,cida,bair,contato=i.replace('\n','').split("|")
			
			#print nome,cnpj,ie,cep,ende,num,comp,cida,bair,contato
			#print len(cep),cep
#			cnpj,ie,nome,fanta,ende,bair,cida,uf,cep,tl1=i.split('|')
			nome,cep,end,bai,cid,uf,email,tel,doc,ie=i.replace('\n','').split('#')
			#print cp,len(cp)
			#cep=cep.replace('.','').replace('-','').replace(',','')
			#cnpj=cnpj.strip()
			
			#if len(cnpj)>14 or len(cnpj)<14:	cnpj=''
			#print len(ie),ie
			#codigo = campo[0]
			#nome=nome.decode("windows-1252",errors='ignore').strip()
			#ende=ende.decode("windows-1252",errors='ignore').strip()
			#bair=bair.decode("windows-1252",errors='ignore').strip()
			#cida=cida.decode("windows-1252",errors='ignore').strip()
			#tl1=tl1.replace(')',' ').replace('(','') if ( len(tl1) + 1 ) <=13 else ''
			#ie     = campo[5].replace('.','').replace(',','').strip()
			#telefo = campo[6].strip()+' \n'+contat
			#endere = campo[8].decode("windows-1252",errors='ignore').strip()
			#numero = campo[9].decode("windows-1252",errors='ignore').strip()
			#comple = campo[10].decode("windows-1252",errors='ignore').strip()
			#bairro = campo[11].decode("windows-1252",errors='ignore').strip()
			#ibge   = campo[12].decode("windows-1252",errors='ignore').strip()
			#cidade = campo[13].decode("windows-1252",errors='ignore').strip()
			#estado = campo[14].decode("windows-1252",errors='ignore').strip()
			#cep    = campo[15].decode("windows-1252",errors='ignore').strip()
			#email  = campo[16].decode("windows-1252",errors='ignore').strip()
			#print( len(ie), ie )

#			nome,end,bai,cid,uf,email,tel,doc,ie=i.split('#')
			#print cnpj,ie,nome,ende,num,bair,cida,uf,cep,tl1,ema
			#gravar = "INSERT INTO fornecedor(fr_docume,fr_insces,fr_nomefo,fr_endere,fr_numero,fr_bairro,fr_cidade,fr_cepfor,fr_estado,fr_idfila,fr_telef1,fr_contas)\
			#VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
			#sql[2].execute( gravar, ( cnpj, ie.strip().replace(',','').replace('-',''), nome, ende[:60], '', bair, cida, cep[:8], uf.strip(),'POSSE','',tl1 ) )
			#cd,nm,fa,dc,ie,en,ba,cd,ib,cp,cl1,cl2,uf,tl1,tl2
			print nome,cep,end,bai,cid,uf,email,tel,doc,ie
			cep=cep.replace('-','')
			gravar = "INSERT INTO fornecedor (fr_docume,fr_insces,fr_nomefo,fr_endere,fr_bairro,fr_cidade,fr_cepfor,fr_estado,fr_telef1,fr_idfila,fr_tipofi)\
			VALUES('"+doc+"','"+ie+"','"+nome+"','"+end+"','"+bai+"','"+cid+"','"+cep+"','"+uf+"','"+tel+"','QUIFE','1')"

			sql[2].execute(gravar) #,(dc,ie,nm,fa,en,cl1,cl2,ba,cd,cp.replace('-',''),uf,ib,tl1,tl2,'SERVE','1'))
			
			"""
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
			"""
	sql[1].commit()
    

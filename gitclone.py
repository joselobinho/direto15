#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  nfceleo40.py
#  Inicio: 01-10-2018 09:43 Jose de almeida lobinho

import os,sys
import glob
import commands

pasta = str( sys.argv[1] )

""" Copia do git Tabelas do IBPT """
if sys.argv[2] == 'ibpt':

    pasta_ibpt = pasta+'/ibpt'
    pasta_srv  = pasta+'/srv'

    """  Ver se a pasta existe, se nao cria"""
    if os.path.exists(pasta_ibpt):	commands.getstatusoutput("rm -r "+pasta_ibpt)
    if not os.path.exists(pasta_ibpt):	os.makedirs(pasta_ibpt)

    if os.path.exists(pasta_ibpt): #--// Pasta existindo
	
	#--// Faz o git na pasta
	ibpt = commands.getstatusoutput('git clone https://github.com/joselobinho/ibpt '+pasta_ibpt)
	#--// Se o git tiver sucesso retorno [0]
	if not ibpt[0]:
	    
	    #--// Relaciona os arquivos
	    arquivos_ibpt = glob.glob(pasta_ibpt+"/*.csv" )
	    if arquivos_ibpt:

		for i in arquivos_ibpt:
		    #--// Copia e troca o dono do arquivo
		    copiar = commands.getstatusoutput('rsync '+i+' '+pasta_srv)
		    dono = commands.getstatusoutput('chown lykos.users '+pasta_srv+'/'+i.split('/')[-1])

elif sys.argv[2] == 'direto':

    pasta_clone = pasta+'/update'
    pasta_direto  = pasta

    if os.path.exists(pasta_clone):	commands.getstatusoutput("rm -r "+pasta_clone)
    if not os.path.exists(pasta_clone):	os.makedirs(pasta_clone)

    if os.path.exists(pasta_clone): #--// Pasta existindo

	#--// Faz o git na pasta
	direto = commands.getstatusoutput('git clone https://joselobinho:151407jml@github.com/joselobinho/direto '+ pasta_clone)

	lista_pasta = ['/eletronicos','/icons','/imagens','/importar','/subsistema']
	origem = pasta_clone
	destino = pasta
	erros = erro1 = erro2 = erro3 = erro4 = erro5=""
	for i in lista_pasta:

	    simm, erros = commands.getstatusoutput('rsync -v -u '+origem+i+'/* '+destino+i)
	    erro1 += erros

	"""  Copiar para a pasta direto  """
	simm, erro2 = commands.getstatusoutput('rsync -v -u '+origem+'/*.py '+destino)
	simm, erro3 = commands.getstatusoutput('rsync -v -u '+origem+'/*.pyw '+destino)
	simm, erro4 = commands.getstatusoutput('rsync -v -u '+origem+'/eletronicos/xsd/* '+destino+'/eletronicos/xsd')
	
	"""  Copiar SRV """
	lista_srv = ['aliquotas.csv','atualizar.csv','cfop.csv','cst.csv','ncm.csv','municipios.csv','cest.csv','piscofins.csv','modulos.csv','ibpt.csv','perfil.csv','relacao.csv','webs.cmd']
	for l in lista_srv:
	    
	    simm, erro5 = commands.getstatusoutput('rsync -v -u '+origem+'/srv/'+l+' '+destino+'/srv')

	result = "{ Retorno da atualizacao }\n\n"+str( erro1 ) + str( erro2 ) + str( erro3 ) + str( erro4 )
	__arquivo = open(pasta_direto+"/retorno_atualizacao.cmd","w")
	__arquivo.write(result)
	__arquivo.close()

	""" Trocando a pasta de dono [ root para lykos ]"""
	dono = commands.getstatusoutput('chown -Rv lykos.users '+pasta)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  backuponline.py

# Jose de aLemdaida lobinho: 27-2-2017  

import os, sys
import dropbox
import time
import datetime
import commands

if os.path.exists("/mnt/lykos/direto/srv/automatico.cmd"):
			
	conteudo = open( "/mnt/lykos/direto/srv/automatico.cmd" ).read()
	if len( conteudo ) and len( conteudo.split("|") ) == 4 and conteudo.split("|")[1] == "T":

		hoje = datetime.datetime.now().strftime("%d%m%Y")
		arer = "onlineerro.txt"

		token, automatico, filial, servico = conteudo.split("|")

		"""  Backup para dropbox  """
		if servico == "dropbox":

			try:
				
				u = dropbox.client.DropboxClient( str( token ) )
				c = dropbox.Dropbox( str( token ) )
				u.account_info()

				folder = "/filiais/"+str( filial.lower() )
				
				pasT = "/home/lykos"
				arqu = "banco_3"+str( filial.lower() )+".sql"
				fullname = pasT+"/bksystem/online/"+arqu
				abrir = commands.getstatusoutput("mysqldump sei -u root -p151407jml > '"+pasT+"/bksystem/online/"+arqu+"'")

				if abrir[0] == 0:

					overwrite=True
					mode = (dropbox.files.WriteMode.overwrite if overwrite else dropbox.files.WriteMode.add)
					mtime = os.path.getmtime(fullname)

					inicial = datetime.datetime.now().strftime("%d/%m/%Y %T")
					data = open(fullname, 'rb').read()
					if len( data ):	res = c.files_upload( data , folder+"/"+arqu, mode, client_modified = datetime.datetime(*time.gmtime(mtime)[:6]), mute = True )
					final = datetime.datetime.now().strftime("%d/%m/%Y %T")

					__arquivo = open(pasT+"/bksystem/online/"+arer,"w")
					__arquivo.write( "sucesso|"+str( inicial )+"|"+str( final )+"|uplodad sucess" )
					__arquivo.close()
				else:
					
					inicial = datetime.datetime.now().strftime("%d/%m/%Y %T")
					__arquivo = open(pasT+"/bksystem/online/"+arer,"w")
					__arquivo.write( "erro|"+str( inicial )+"||"+str( abrir[1] ) )
					__arquivo.close()

			except Exception as erro:

				inicial = datetime.datetime.now().strftime("%d/%m/%Y %T")
				__arquivo = open(pasT+"/bksystem/online/"+arer,"w")
				__arquivo.write( "erro|"+str( inicial )+"||"+str( erro ) )
				__arquivo.close()
				
	else:

		__arquivo = open(pasT+"/bksystem/online/"+arer,"w")
		__arquivo.write( "erro|||Servidor nao configurado para backup automatico")
		__arquivo.close()

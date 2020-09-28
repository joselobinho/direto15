#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  backupdrop.py
#  
#  Copyright 2017 lykos users <lykos@linux-4368>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

# 23-09-2017 Jose Lobinho Backup separado por tabelas para enviar ao dropbox
import os
import datetime
import commands
from dropconn import *

conn = sqldb()
sql  = conn.dbc("Produtos, Alterar Estoque Fisico",1)

erros = ""

if sql[0]:

	if sql[2].execute("SELECT ep_inde FROM cia"):

		filial = sql[2].fetchone()[0]
		if filial:

			pasta_dropbx = "/root/Dropbox"
			pasta_backup = "/root/Dropbox/filiais"
			pasta_tabela = "/mnt/lykos/direto/importar/tabelas.py"
			pasta_retorn = "/home/lykos/direto/configura"

			if os.path.exists( pasta_dropbx ):
				
				if not os.path.exists( pasta_backup ):	os.makedirs( pasta_backup )
			
				if os.path.exists( pasta_backup ) and os.path.exists( pasta_tabela ):
				
					if not os.path.exists( pasta_backup+"/"+filial ):	os.makedirs( pasta_backup+"/"+filial )

					""" Aproveita a tabelas.py onde conta os nomes de tabelas para utilizar no inicio do arquivo  """
					__arquivo  = open(pasta_tabela,"r").readlines()
					for i in __arquivo:
						
						"""  Filtra apenas o nome das tabelas  """
						if 'IF NOT EXISTS' in i:
							
							tabelas = i.split("IF NOT EXISTS")[1].split('(')[0].strip()
							if not tabelas.isdigit():
								
								back = "mysqldump sei "+ tabelas +" -u root -p151407jml > "+pasta_backup+"/"+filial+"/"+filial+"_"+tabelas+".sql"
								abri = commands.getstatusoutput( back )
								if abri[0]:	erros +="Tabela "+str( tabelas )+', Retorno: '+abri[1]+"\n"
								
			else:	erros = "A pasta do Dropbox nao foi localizada"
	conn.cls( sql[1] )

else:	erros = "Nao conseguiu abrir a tabela de empresas"

if erros:
	
	__data = datetime.datetime.now().strftime("%d-%m-%Y %T")
	__arquivo = open(pasta_retorn+"/errosbackup.txt","w")
	__arquivo.write(__data+'\n'+erros )
	__arquivo.close()


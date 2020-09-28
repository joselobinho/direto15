#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  backup.py
#  
#  Copyright 2015 vendas users <vendas@joselobinho.site>
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
import os
import datetime
import commands

pasT = "/home/lykos"
if os.path.exists(pasT+"/bksystem") == False:	os.makedirs(pasT+"/bksystem")
if os.path.exists(pasT+"/bksystem/bkmont") == False:	os.makedirs(pasT+"/bksystem/bkmont")
if os.path.exists(pasT+"/bksystem/bkerro") == False:	os.makedirs(pasT+"/bksystem/bkerro")

regi = datetime.datetime.now().strftime("%d/%m/%Y %T")
hoje = datetime.datetime.now().strftime("%d%m%Y")
arqu = "banco"+str( hoje )+".sql"
arer = "retornoerror.txt"

# Comando para deixar o cron parmanente { insserv cron }
#------------{ Despositivo de Bloco Comando lsblk }
disP = ""
banc = "sei"
#------------{ Fim Despositivo de Bloco }

"""  Faz a verificacao p/ver se dispositivo de bloco estar ligado"""
li = commands.getstatusoutput("lsblk > "+str(pasT)+"/bksystem/bkerro/driversblocl2.txt")
try:
	
	if os.path.exists(str(pasT)+"/bksystem/bkerro/driversblocl2.txt"):

		__arquivo = open(str(pasT)+"/bksystem/bkerro/driversblocl2.txt","r")
		li = __arquivo
		for i in __arquivo:

			if "SDA1" in i.upper() and 'SWAP' not in i.upper() and 'BOOT' not in i.upper() and 'USR' not in i.upper() and 'PART' in i.upper():	disP = "sda1"
			if "SDB1" in i.upper() and 'SWAP' not in i.upper() and 'BOOT' not in i.upper() and 'USR' not in i.upper() and 'PART' in i.upper():	disP = "sdb1"
			if "SDC" in i.upper():	disP = "sdc1"
			if "SDD" in i.upper():	disP = "sdd1"
			if "SDE" in i.upper():	disP = "sde1"	
			print('-----------------------------: ',disP,i)	
		print('Final-----------------------------: ',disP)	

	if disP:

		uMo1 = commands.getstatusoutput("umount "+pasT+"/bksystem/bkmont")
		Moun = commands.getstatusoutput("mount /dev/"+disP+" "+pasT+"/bksystem/bkmont")
		abri = commands.getstatusoutput("mysqldump "+banc+" -u root -p151407jml > '"+pasT+"/bksystem/bkmont/"+arqu+"'")

		disk_space = commands.getstatusoutput("df -h /dev/"+disP+" | awk '{print $5}'")
		uMo2 = commands.getstatusoutput("umount "+pasT+"/bksystem/bkmont")

		sem_espaco = ''
		if disk_space[0] == 0:

			hd_usado = disk_space[1].split('\n')[1].replace('%','')
			if hd_usado and hd_usado.isdigit() and int( hd_usado ) > 90:	sem_espaco = 'Espaco critico no HD de backup local { em uso '+str( hd_usado )+'% }\nEntre em contato urgente com o suporte do DIRETO'

		if abri[0] !=0 or uMo2[0] !=0 or Moun[0] !=0 or sem_espaco:
			
			__arquivo = open(pasT+"/bksystem/bkerro/"+arer,"w")
			__arquivo.write( "Erro|"+str( regi )+"|"+str( abri[1] )+"\nMotagem Inicial: "+str( Moun[1] )+"\nCopia: "+str( abri[1] )+"\nDesmontagem Final:"+str( uMo2[1] )+"\n\nDispositivo: "+str( disP )+'\n\n'+sem_espaco )
			__arquivo.close()

		else:
			
			__arquivo = open(pasT+"/bksystem/bkerro/"+arer,"w")
			__arquivo.write( "Sucesso|"+str( regi )+"|"+str( abri[1] )+"\nMotagem Inicial: "+str( Moun[1] )+"\nCopia: "+str( abri[1] )+"\nDesmontagem Final:"+str( uMo2[1] ) )
			__arquivo.close()

	else:	

		__arquivo = open(pasT+"/bksystem/bkerro/"+arer,"w")
		__arquivo.write( "Erro|"+str( regi )+"|Nao foi localizado nenhum dispositivo de bloco para backup")
		__arquivo.close()

except Exception as error:

	__arquivo = open(pasT+"/bksystem/bkerro/"+arer,"w")
	__arquivo.write( "Erro|"+str( regi )+"|erro de excecao\n"+str( error ) )
	__arquivo.close()
	
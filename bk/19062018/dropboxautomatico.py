#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dropboxautomatico.py
#  
#  Copyright 2017 lykos users <lykos@linux.suse>
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
#  27-junho-2017 Jose Loibnho
#  Utilizado no cron para backup automatico
#  PS 1 - baixa o dropbox como root { zypper in dropbox }
#     2 - instale dropbox start -i como root
#     3 - na pasta etc/init.d crie um arquivo rc.local { linha 1 #! /bin/sh, linha 2 /usr/bin/dropbox start }  salve e torne executavel para todos os usuarios
#     4 - execute dentro da pasta etc/init.d o insserv rc.local 
#     5 - Reinicie o servidor e teste o dropbox

import os
import datetime
import commands

if os.path.exists("/root/Dropbox"):
		
	arquivo_logs = "/root/logs_dropbox.txt"
	de = datetime.datetime.now().strftime("%Y-%m-%d %T")
	open(arquivo_logs,"a").write(de+" Iniciando backup\n")

	geral = "/root/Dropbox/banco_completo.sql"
	produ = "/root/Dropbox/tabela_produtos.sql"
	clien = "/root/Dropbox/tabela_clientes.sql"
	estoq = "/root/Dropbox/tabela_estoque.sql"
	empre = "/root/Dropbox/tabela_empresa.sql"
	param = "/root/Dropbox/tabela_parametros.sql"
	usuar = "/root/Dropbox/tabela_usuario.sql"
		
	abrir1 = commands.getstatusoutput("mysqldump sei -u root -p151407jml > "+ geral )
	abrir2 = commands.getstatusoutput("mysqldump -u root -p151407jml sei produtos > "+ produ )
	abrir3 = commands.getstatusoutput("mysqldump -u root -p151407jml sei clientes > "+ clien )
	abrir4 = commands.getstatusoutput("mysqldump -u root -p151407jml sei estoque > "+ estoq )
	abrir5 = commands.getstatusoutput("mysqldump -u root -p151407jml sei cia > "+ empre )
	abrir6 = commands.getstatusoutput("mysqldump -u root -p151407jml sei parametr > "+ param )
	abrir7 = commands.getstatusoutput("mysqldump -u root -p151407jml sei usuario > "+ usuar )

	de = datetime.datetime.now().strftime("%Y-%m-%d %T")
	open(arquivo_logs,"a").write(de+" Finalizando backup "+str( abrir1 )+' '+str( abrir2 )+' '+str( abrir3 )+' '+str( abrir4 )+'\n')

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  boletosonline.py
#  
#  Copyright 2017 lykos users <lykos@linux-714r.site>
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
#  Lobinho: 04-03-2017

import datetime
import pycurl
import urllib
import json
import os
from conectar import dialogos,menssagem,gerenciador,login,diretorios
from StringIO import StringIO
#from gerencianet import Gerencianet

alertas = dialogos()
mens    = menssagem()

class BoletosOnlineBoletoCloud:

	modulosolicitante = ""
	def pegarBoletoGerado(self, parent, numero_lancamento, id_boleto, localizacao_local, **kwargs ):

		mensagem_apagada = False
		bl = gravarRetornosBoletos()
		bl.modulo = self.modulosolicitante
		er = ""
		rt = False, ""

		response_buffer = StringIO()
		response_bfbody = StringIO()
		try:

			c = pycurl.Curl()
			c.setopt( pycurl.URL, str( kwargs['url'].strip() + "/"+ id_boleto.strip() ) )

			#---:Setup the base HTTP Authentication.
			c.setopt( pycurl.USERPWD, '%s:%s' % ( kwargs['token'],'token') )
			c.setopt( pycurl.WRITEFUNCTION, response_buffer.write )
			c.setopt( pycurl.HEADERFUNCTION, response_bfbody.write ) #--:Retorno do body, cabecalho

			_mensagem = mens.showmsg("Enviando solicitação de 2a Via do boleto!!\nfazendo o download do pdf para envio por email ou impressão\n\nAguarde...")
			c.perform()
			del _mensagem
			
		except Exception as erros:
			er = erros
			rt = False,	"{ erros externos e/ou de comunicação }\n\n"+str( erros )

			c.close()

		if not er:

			codigo_retorno = c.getinfo(pycurl.RESPONSE_CODE)
			response_value = response_buffer.getvalue()
			response_body  = response_bfbody.getvalue()
			c.close()

			if codigo_retorno == 200:
			
				path_pdf = bl.gravarPdf( response_value, numero_lancamento )
				rt = True, path_pdf

			else:
			
				erro = False,""

			if "ERRO" in response_value.upper() and not "<!DOCTYPE" in response_value.upper():

				r = json.loads(response_value)
				status   = r["erro"]["status"]
				tipo     = r["erro"]["tipo"]
				codigo   = r["erro"]["causas"][0]["codigo"]
				mensagem = r["erro"]["causas"][0]["mensagem"]
				suporte  = r["erro"]["causas"][0]["suporte"]

				erro = True,"Status: "+str( status )+\
							"\nTipo: "+ tipo +\
							"\nCodigo: "+ codigo +\
							"\n\n[ Mensagem ]\n"+ mensagem +\
							"\n\nSuporte: "+ suporte 

				rt = False, u"{ Erro no envio da solicitação }\n\n"+erro[1]
				
			if "</HTML>" in response_value.upper() and "<!DOCTYPE" in response_value.upper():	rt = False, "{ Erro, retorno em html [ URL não localizada ] }\n\nUrl "+str( kwargs['url'].strip() + "/"+ id_boleto.strip() )

		return rt
		
	def boletoConfeccionar(self, parent, email, params, **kwargs ):

		nd = params[16][1]
		bl = gravarRetornosBoletos()
		rt = False,"","","",False

		menssagem = params[21][1] if type( params[21][1] ) == unicode else params[21][1].decode("UTF-8")
		_mensagem = mens.showmsg(u"{ Enviando solicitação para confecção do boleto }\n\nEnviando dados e fazendo download do pdf para envio por email ou impressão\n\nCliente: "+ menssagem +"\n\nAguarde...")

		c = pycurl.Curl()
		try:
			
			erros = ""
			response_buffer = StringIO()
			response_bfbody = StringIO()

			#print "========================================: ",params

			data = urllib.urlencode( params ) #-:codificacao dos dados para url
			c.setopt( pycurl.URL, kwargs['url'] ) #------------------------------------:Url
			c.setopt( pycurl.USERPWD, '%s:%s' % ( kwargs['token'], 'token') ) #--------:Setup the base HTTP Authentication.
			c.setopt( pycurl.HTTPHEADER, ['X-Postmark-Server-Token: API_TOKEN_HERE','Accept: application/json','Content-Type: application/x-www-form-urlencoded; charset=utf-8'] )
			c.setopt( pycurl.POST, True )
			c.setopt( pycurl.TIMEOUT , 150 )
			c.setopt( pycurl.POSTFIELDS, data )

			c.setopt( pycurl.WRITEFUNCTION,  response_buffer.write ) #-:Gravar retorno em arquivo
			c.setopt( pycurl.HEADERFUNCTION, response_bfbody.write) #--:Retorno do body, cabecalho
				
			c.perform()
		
		except Exception as error:
			
			erros = error
			rt = False,"","",error,False
			
		del _mensagem
		
		if not erros:
			
			retorno = c.getinfo(pycurl.RESPONSE_CODE)
			
			c.close()
			response_value = response_buffer.getvalue()
			response_body  = response_bfbody.getvalue()
			
			if retorno == 201:

				localizacao_boleto = self.retornaLocalizacao( response_body )

				_mensagem = mens.showmsg("{ Enviando solicitação para confecção do boleto }!!\n\nGravando arquivo pdf na pasta local\n\nAguarde...")

				path_pdf = bl.gravarPdf( response_value, nd )
				rt = True, localizacao_boleto, path_pdf, "",False

				del _mensagem
				
			elif "</HTML>" in response_value.upper() and "<!DOCTYPE" in response_value.upper():

				rt = False, "", "", u"{ Erro, retorno em html [ URL não localizada ] }\nUrl "+ kwargs['url'], False

			elif "ERRO" in response_value.upper():

				r = json.loads( response_value )
				status   = r["erro"]["status"]
				tipo     = r["erro"]["tipo"]
				codigo   = r["erro"]["causas"][0]["codigo"]
				mensagem = r["erro"]["causas"][0]["mensagem"]
				suporte  = r["erro"]["causas"][0]["suporte"]

				status_erro ="Status: "+ str( status ) +\
							"\nTipo: "+ tipo +\
							"\nCodigo: "+ codigo+\
							"\n\n[ Mensagem ]\n"+ mensagem +\
							"\n\nSuporte: "+ suporte 

				localizacao_boleto = localizacao_boleto = self.retornaLocalizacao( response_body )

				rt = False, localizacao_boleto, "", status_erro, True if tipo.upper() == "CONFLITO" else False
		
		c.close()

		return rt

	def retornaLocalizacao(self, __body ):

		localizacao_boleto = ""
		for i in __body.split('\n'):

			if "LOCATION:" in i.upper() and len( i.split(':') ) >= 2: localizacao_boleto = i.split(':')[1].strip()

		return localizacao_boleto

	def incluirDadosBoleto( self, de ):

		#// OBS: Voce deve codificar todos os dados com decode("UTF-8") antes de enviar para p metodo incluirDadosBoleto
		#// Para no metodo incluirDadosBoleto, encodificar encode("UTF-8") para usar urllib.urlencode( params )
		#// Se nao dar erro ascii codec { 10-01-2018 }
		
		ced_doc = de["cedente"][0]
		ced_des = de["cedente"][1]
		ced_end = de["cedente"][2]
		ced_num = de["cedente"][3]
		ced_cmp = de["cedente"][4]
		ced_bai = de["cedente"][5]
		ced_cid = de["cedente"][6]
		ced_est = de["cedente"][7]
		ced_cep = de["cedente"][8]
		
		"""  Numero, complento separar por pipe  """
		if len( ced_num.split(" ") ) >= 2:	ced_num, cad_cmp = ced_num.split(" ")

		data_hoje = str( datetime.datetime.now().date() ).decode("UTF-8")

		""" Dados do banco """
		ban_num = de["banco"][0]
		ban_age = de["banco"][1]
		ban_coc = de["banco"][2]
		ban_car = de["banco"][3]
		ban_esp = de["banco"][4]
		ban_obs = de["banco"][5]
		ban_emp = de["banco"][6]
		ban_cnv = de["banco"][7] #-:Convenio-numero do benficiario

		"""  Se os dados do cente no cadastro de bancos estiver preenchido o sistema usa ele se nao usa o do cadastro de cedente  """
		if ban_emp:	ced_des, ced_doc, ced_end = ban_emp

		"""  dados do cliente sacado  """
		cl_idcl = de["cliente"][0]
		cl_nome = de["cliente"][1]
		cl_fant = de["cliente"][2]
		cl_docu = de["cliente"][3]
		cl_ende = de["cliente"][4]
		cl_bair = de["cliente"][5]
		cl_cida = de["cliente"][6]
		cl_ibge = de["cliente"][7]
		cl_ceps = de["cliente"][8]
		cl_cmp1 = de["cliente"][9]
		cl_cmp2 = de["cliente"][10]
		cl_esta = de["cliente"][11]
		cl_emai = de["cliente"][12]
                      
		cl_serv = de["cliente"][13]
		#print "------------------1: ",type( cl_serv ), cl_serv
		#print "------------------2: ",type( ced_cid ), ced_cid

		lancamento_nosso_numero = de["valores"][0]
		valor_documento = de["valores"][1]

		vencimento = de["valores"][2]
		data_docum = de["valores"][3]
		juro  = de["valores"][4]
		multa = de["valores"][5]

		l1 = de["instrucao"][0]
		l2 = de["instrucao"][1]
		l3 = de["instrucao"][2]
		l4 = de["instrucao"][3]
		l5 = de["instrucao"][4]
		l6 = de["instrucao"][5]
		#print "LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL: ",type( cl_serv ),cl_serv
		dados_boleto = [("boleto.conta.banco",ban_num if not type( ban_num ) == unicode else ban_num.encode("UTF-8") ),
		("boleto.conta.agencia",ban_age if not type( ban_age ) == unicode else ban_age.encode("UTF-8") ),
		("boleto.conta.numero",ban_coc if not type( ban_coc ) == unicode else ban_coc.encode("UTF-8") ),
		("boleto.conta.carteira",ban_car if not type( ban_car ) == unicode else ban_car.encode("UTF-8") ),
		("boleto.beneficiario.nome",ced_des if not type( ced_des ) == unicode else ced_des.encode("UTF-8") ),
		("boleto.beneficiario.cprf",ced_doc if not type( ced_doc ) == unicode else ced_doc.encode("UTF-8") ),
		("boleto.beneficiario.endereco.cep",ced_cep if not type( ced_cep ) == unicode else ced_cep.encode("UTF-8") ),
		("boleto.beneficiario.endereco.uf",ced_est if not type( ced_est ) == unicode else ced_est.encode("UTF-8") ),
		("boleto.beneficiario.endereco.localidade", ced_cid if not type( ced_cid ) == unicode else ced_cid.encode("UTF-8") ),
		("boleto.beneficiario.endereco.bairro",ced_bai if not type( ced_bai ) == unicode else ced_bai.encode("UTF-8") ),
		("boleto.beneficiario.endereco.logradouro",ced_end if not type( ced_end ) == unicode else ced_end.encode("UTF-8") ),
		("boleto.beneficiario.endereco.numero",ced_num if not type( ced_num ) == unicode else ced_num.encode("UTF-8") ),
		("boleto.beneficiario.endereco.complemento",ced_cmp if not type( ced_cmp ) == unicode else ced_cmp.encode("UTF-8") ),
		("boleto.emissao",data_hoje if not type( data_hoje ) == unicode else data_hoje.encode("UTF-8") ),
		("boleto.vencimento",vencimento if not type( vencimento ) == unicode else vencimento.encode("UTF-8") ),
		("boleto.documento",cl_idcl if not type( cl_idcl ) == unicode else cl_idcl.encode("UTF-8") ),
		("boleto.sequencial",lancamento_nosso_numero if not type( lancamento_nosso_numero ) == unicode else lancamento_nosso_numero.encode("UTF-8") ),
		("boleto.titulo",ban_esp if not type( ban_esp ) == unicode else ban_esp.encode("UTF-8") ),
		("boleto.valor",valor_documento if not type( valor_documento ) == unicode else valor_documento.encode("UTF-8") ),
		("boleto.juros",juro if not type( juro ) == unicode else juro.encode("UTF-8") ),
		("boleto.multa",multa if not type( multa ) == unicode else multa.encode("UTF-8") ),
		("boleto.pagador.nome",cl_nome if not type( cl_nome ) == unicode else cl_nome.encode("UTF-8") ),
		("boleto.pagador.cprf",cl_docu if not type( cl_docu ) == unicode else cl_docu.encode("UTF-8") ),
		("boleto.pagador.endereco.cep",cl_ceps if not type( cl_ceps ) == unicode else cl_ceps.encode("UTF-8") ),
		("boleto.pagador.endereco.uf",cl_esta if not type( cl_esta ) == unicode else cl_esta.encode("UTF-8") ),
		("boleto.pagador.endereco.localidade",cl_cida if not type( cl_cida ) == unicode else cl_cida.encode("UTF-8") ),
		("boleto.pagador.endereco.bairro",cl_bair if not type( cl_bair ) == unicode else cl_bair.encode("UTF-8") ),
		("boleto.pagador.endereco.logradouro",cl_ende if not type( cl_ende ) == unicode else cl_ende.encode("UTF-8") ),
		("boleto.pagador.endereco.numero",cl_cmp1 if not type( cl_cmp1 ) == unicode else cl_cmp1.encode("UTF-8") ),
		("boleto.pagador.endereco.complemento",cl_cmp2 if not type( cl_cmp2 ) == unicode else cl_cmp2.encode("UTF-8") ),
		("boleto.instrucao",l1 if not type( l1 ) == unicode else l1.encode("UTF-8") ),
		("boleto.instrucao",l2 if not type( l2 ) == unicode else l2.encode("UTF-8") ),
		("boleto.instrucao",l3 if not type( l3 ) == unicode else l3.encode("UTF-8") ),
		("boleto.instrucao",l4 if not type( l4 ) == unicode else l4.encode("UTF-8") ),
		("boleto.instrucao",l5 if not type( l5 ) == unicode else l5.encode("UTF-8") ),
		("boleto.instrucao",l6 if not type( l6 ) == unicode else l6.encode("UTF-8") ),
		("boleto.instrucao",cl_serv if not type( cl_serv ) == unicode else cl_serv.encode("UTF-8") )]

		return dados_boleto
		
class gravarRetornosBoletos:
	
	modulo = ""
	def gravarPdf( self, arquivo, numero_nosso_numero ):
		
		_p= "boletos" if self.modulo == "RECEBER" else "nosso_sistema"
		if os.path.exists( diretorios.usPasta + _p ) == False:	os.makedirs( diretorios.usPasta + _p )

		__arquivo = open( diretorios.usPasta + _p + "/"+str( numero_nosso_numero ).zfill(10)+".pdf", "w" )
		__arquivo.write( arquivo )
		__arquivo.close()

		gerenciador.Anexar = diretorios.usPasta + _p + "/"+str( numero_nosso_numero ).zfill(10)+".pdf"
		return diretorios.usPasta + _p+ "/"+str( numero_nosso_numero ).zfill(10)+".pdf"

	def mostrarHtml(self, parent, arquivo ):

		_p= "boletos" if self.modulo == "RECEBER" else "nosso_sistema"

		if os.path.exists( diretorios.usPasta + _p ) == False:	os.makedirs( diretorios.usPasta + _p )

		__arquivo = open(diretorios.usPasta + _p + "/meu_boleto.html","w")
		__arquivo.write( arquivo )
		__arquivo.close()

		__html = diretorios.usPasta + _p + "/meu_boleto.html"

		parent.leituraHtml( __html )

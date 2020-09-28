#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  openbankboleto.py
#  
#  Copyright 2018 lykos users <lykos@linux-01pp>
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

#  Jose de almeida lobinho 24-10-2018 14:33
#  Comunicacao com a biblioteca de webservice de openbank
import json
import requests
import datetime

class PagHiper:
    
    headers_paghiper={'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
    def pagHiperBoleto(self,parent,d):

	try:

	    retorno=True
	    erro,codigo,gravar='','',''
	    
	    dias_vencimento=( (datetime.datetime.strptime(d['vencimento'],'%Y-%m-%d') - datetime.datetime.now() ).days +1 )
	    url='https://api.paghiper.com/transaction/create/'
	    
	    params=json.dumps({
		  'apiKey':d['apiKey'],
		  'token':d['token'],
		  'order_id':d['idlancamento'], #// código interno do lojista para identificar a transacao.
		  'payer_email':d['email'],
		  'payer_name':d['nome'], #// nome completo ou razao social
		  'payer_cpf_cnpj':d['documento'], #// cpf ou cnpj
		  'payer_phone':d['ddd']+d['telefone'], #// fixou ou móvel
		  'payer_street':d['endereco'],
		  'payer_number':d['numero'],
		  'payer_complement':d['complemento'],
		  'payer_district':d['bairro'],
		  'payer_city':d['cidade'],
		  'payer_state':d['estado'], #// apenas sigla do estado
		  'payer_zip_code':d['cep'],
		  'fixed_description':True,
		  'type_bank_slip':'boletoA4', #// formato do boleto
		  'days_due_date':str(dias_vencimento), #// dias para vencimento do boleto
		  'late_payment_fine':'2', #// Percentual de multa após vencimento.
		  'per_day_interest':True, #// Juros após vencimento.
		  'items':[{
		      'description':d['servico'],
		      'quantity':'1',
		      'item_id':'1',
		      'price_cents':d['valor'].replace('.','')}], #// em centavos
		  })

	    r=requests.post(url,headers=self.headers_paghiper,data=params)
	    t = json.loads(r.content)
	    if r.status_code == 201:
		
		codigo=str(r.status_code)
		codigo_barras=t['create_request']['bank_slip']['digitable_line']
		url_boleto=t['create_request']['bank_slip']['url_slip']
		url_pdf_boleto=t['create_request']['bank_slip']['url_slip_pdf']
		order_id=t['create_request']['order_id']
		data_hora_boleto=t['create_request']['created_date']
		id_boleto=t['create_request']['transaction_id']
		menssagem=t['create_request']['response_message']
		gravar=order_id+'|'+id_boleto+'|'+codigo_barras+'|'+url_boleto+'|'+url_pdf_boleto+'|'+menssagem

	    else:
		codigo=str( t['create_request']['http_code'] )
		erro=t['create_request']['response_message']
		retorno=False
		
	except Exception as erros:
	    
	    retorno=False
	    erro=erros if type(erros)==unicode else str(erros)
	    codigo='Excessao'
	
	return retorno, codigo,erro, gravar

    def pagHiperCancelar(self,parent,d):

	url='https://api.paghiper.com/transaction/cancel/'
	params=json.dumps({
	  'apiKey':d['apiKey'],
	  'token':d['token'],
	  'status':'canceled',
	  'transaction_id':d['id']
	})

	r=requests.post(url,headers=self.headers_paghiper,data=params)
	t=json.loads(r.content)
	
	retorno=False
	if r.status_code == 201:
	    menssagem=t['cancellation_request']['response_message']
	    retorno=True
	else:	menssagem=t['cancellation_request']['response_message']
	
	return retorno, menssagem

    def pagHiperLista(self,parent,d):

	url='https://api.paghiper.com/transaction/list/'
	transacoes={}
	params=json.dumps({ 
	'apiKey':d['apiKey'],
	'token':d['token'],
	'initial_date':d['d_inicial'],
	'final_date':d['d_final'],
	'filter_date':d['filtro']
	})

	r=requests.post(url,headers=self.headers_paghiper,data=params)
	t=json.loads(r.content)
	#print t
	if r.status_code == 201:
	    
	    for i in t['transaction_list_request']['transaction_list']:

		id_transacao=i['transaction_id']
		id_cliente=i['order_id'] #--// Codigo enviado { Normalmente o DAV }
		status=i['status'] #--------// [ pending->aguardando, canceled->cancelado, paid->aprovado e completo, processing->analise, refunded->estornado ]
		vencimento=i['due_date']
		tarifa_boleto=i['value_fee_cents']
		cnpj=i['payer_cpf_cnpj']
		nome=i['payer_name']
		data_transacao=i['create_date']
		codigo_barras=i['bank_slip']['digitable_line']
		valor_final_transacao=i['value_cents']
		link_boleto=i['bank_slip']['url_slip']
		link_pdf=i['bank_slip']['url_slip_pdf']
		email=i['payer_email']

		transacoes[id_transacao]=id_cliente,status,vencimento,tarifa_boleto,cnpj,nome,data_transacao,codigo_barras,valor_final_transacao,link_boleto,link_pdf,email
	    if transacoes:	return True, transacoes
	    else:	return False, u'Lista de transações estar vazio para o perido informado ['+d['d_inicial']+' A '+d['d_final']+']'
	
    	else:
	    menssagem=t['transaction_list_request']['response_message']
	    return False, menssagem

		
class Pagarme:
    
    headers_pagarme={'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
    def pagarmeBoleto(self, parent, d):

	url='https://api.pagar.me/1/transactions/?'
	
	type_document='corporation' if len(d['documento'])==14 else 'individual'
	type_document_name='cnpj' if len(d['documento'])==14 else 'cpf'
	params = {
	  'api_key':d['apiKey'],
	  'amount': d['valor'].replace('.',''), 
	  'payment_method': 'boleto',
	  'boleto_expiration_date': d['vencimento'],
	  'customer': {
	    'external_id': d['idlancamento'],
	    'name': d['nome'],
	    'email': d['email'],
	    'country': 'br',
	    'type': type_document,
	    'documents': [{
		'type':type_document_name,
		'number':d['documento']
	    }]
	    }
	}

	r=requests.post(url,headers=self.headers_pagarme,json=params)
	t=json.loads(r.content)
	
	erro=''
	codigo=''
	gravar=''

	if r.status_code==200 and t:
	    
	    codigo='201'
	    codigo_barras=t['boleto_barcode']
	    url_boleto=t['boleto_url']
	    url_pdf_boleto=''
	    order_id=t['customer']['external_id']
	    data_hora_boleto=t['date_created']
	    id_boleto=t['tid']
		
	    gravar=str(order_id)+'|'+str(id_boleto)+'|'+str(codigo_barras)+'|'+url_boleto+'|'+url_pdf_boleto+'|Transacao criada'
	    return True, codigo,erro, gravar

	elif r.status_code==200 and not t:	return False, erro,'Retorno de emissao vazio...', gravar
	else:
	    
	    parametro=', parameter_name: '+t['errors'][0]['parameter_name'] if t['errors'][0]['parameter_name'] else ''
	    erro=t['errors'][0]['message'] +', type: '+ t['errors'][0]['type'] +parametro
	    return False, codigo, erro, gravar

    def pagarmeLista(self,parent,d):

	url='https://api.pagar.me/1/transactions?'
	transacoes={}
	params={ 
	'api_key':d['apiKey'],
	'date_created':'>='+d['d_inicial'],
	}
	
	r=requests.get(url,headers=self.headers_pagarme,json=params)
	t=json.loads(r.content)
	
	if r.status_code == 200 and t:

	    transacoes={}
	    for i in t:

		id_transacao=i['id']
		id_cliente=i['customer']['external_id'] #--// Codigo enviado { Normalmente o DAV }
		status=i['status'] #--------// [ pending->aguardando, canceled->cancelado, paid->aprovado e completo, processing->analise, refunded->estornado ]
		vencimento=i['boleto_expiration_date']
		tarifa_boleto=''
		cnpj=i['customer']['documents'][0]['number']
		nome=i['customer']['name']
		data_transacao=i['date_created']
		codigo_barras=i['boleto_barcode']
		valor_final_transacao=i['authorized_amount']
		transacoes[id_transacao]=id_cliente,status,vencimento,tarifa_boleto,cnpj,nome,data_transacao,codigo_barras,valor_final_transacao
	    
	    return True, transacoes
	elif r.status_code == 200 and not t:	return False,u'Lista de transações estar vazio para a data inicial informada ['+d['d_inicial']+']'
	else:
	    return False, t['errors'][0]['message'] +', type: '+ t['errors'][0]['type'] +', parameter_name: '+ t['errors'][0]['parameter_name']
	    
    def pagarmeCacelar(self,parent,d):

	"""" Nao tem cancelamento apenas estorno """
	url='https://api.pagar.me/1/transactions/'+d['id']+'/refund?'
	transacoes={}
	params={ 
	'api_key':d['apiKey'],
	}
	r=requests.post(url,headers=self.headers_pagarme,json=params)
	t=json.loads(r.content)

	retorno=False
	if r.status_code==200:
	    menssagem='Nao tem cancelamento apenas estorno' #t['cancellation_request']['response_message']
	    retorno=True
	else:	menssagem=t['errors'][0]['message']
	
	return retorno, menssagem
	    

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  sem título.py
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
#

import requests
import json
from requests.auth import HTTPBasicAuth

__token = "api-key_kh0La_9ex4zHNNPU5pusNYVBuRmlYNzbYWBTx6cwvVs="
__bol   = "pMLMOFhsurM2bCa4Ta3wGCgvZfce7LAheXJqxh268W4=" 
__url   = 'https://sandbox.boletocloud.com/api/v1/boletos/'


file = requests.get(self.get_url( token_ticket), auth=self.authenticate)



import requests
import json
from requests.auth import HTTPBasicAuth
#from .exception import ConnectionError, AuthenticationError


class Ticket(object):

    def __init__(self, token):
        self.__token = token
        self.__url = 'https://sandbox.boletocloud.com/api/v1/boletos/'

    @property
    def token(self):
        '''Returns the token for access API.'''
        return self.__token

    def get_url(self, resource=''):
        '''Returns the url.'''
        return '{0}{1}'.format(self.__url, resource)

    @property
    def authenticate(self):
        '''Authenticate all requests.'''
        return HTTPBasicAuth(self.token, 'token') 

    def create(self, bank, agency, number, wallet, recipient_name, recipient_cprf, recipient_address_zip, recipient_address_uf, recipient_address_locale, recipient_address_neighborhood, recipient_address_street, recipient_address_number, recipient_address_complement, emission, pay, document, ticket_number, title, value, payer_name, payer_cprf, payer_address_zip, payer_address_uf, payer_address_locale, payer_address_neighborhood, payer_address_street, payer_address_number, payer_address_complement, instruction):
        '''Creates a ticket with b ase in the parameters of this method.'''
        payload = {
            'boleto.conta.banco': bank,
            'boleto.conta.agencia': agency, 
            'boleto.conta.numero': number, 
            'boleto.conta.carteira': wallet, 
            'boleto.beneficiario.nome': recipient_name, 
            'boleto.beneficiario.cprf': recipient_cprf, 
            'boleto.beneficiario.endereco.cep': recipient_address_zip, 
            'boleto.beneficiario.endereco.uf': recipient_address_uf,
            'boleto.beneficiario.endereco.localidade': recipient_address_locale, 
            'boleto.beneficiario.endereco.bairro': recipient_address_neighborhood, 
            'boleto.beneficiario.endereco.logradouro': recipient_address_street, 
            'boleto.beneficiario.endereco.numero': recipient_address_number,
            'boleto.beneficiario.endereco.complemento': recipient_address_complement, 
            'boleto.emissao': emission,
            'boleto.vencimento': pay, 
            'boleto.documento': document, 
            'boleto.numero': ticket_number, 
            'boleto.titulo': title,
            'boleto.valor': value, 
            'boleto.pagador.nome': payer_name, 
            'boleto.pagador.cprf': payer_cprf,
            'boleto.pagador.endereco.cep': payer_address_zip, 
            'boleto.pagador.endereco.uf': payer_address_uf,
            'boleto.pagador.endereco.localidade': payer_address_locale, 
            'boleto.pagador.endereco.bairro': payer_address_neighborhood,
            'boleto.pagador.endereco.logradouro': payer_address_street, 
            'boleto.pagador.endereco.numero': payer_address_number,
            'boleto.pagador.endereco.complemento': payer_address_complement, 
            'boleto.instrucao': instruction,
        }


        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'Accept': 'application/pdf, application/json'
        }

        with open('ticket.pdf', 'wb') as ticket:
            file = requests.post(self.get_url(), data=json.dumps(payload), headers=headers, auth=self.authenticate)
            ticket.write(file.content)

    def search(self, token_ticket):
        '''Returns the boleto especify in token_ticket.'''
        with open('ticket.pdf', 'wb') as ticket:
            file = requests.get(self.get_url(token_ticket), auth=self.authenticate)
            ticket.write(file.content)













#import pycurl, json

#github_url = 'https://sandbox.boletocloud.com/api/v1/boletos/1'

#data = json.dumps({"From": "user@example.com", "To": "receiver@example.com", "Subject": "Pycurl", "TextBody": "Some text"})

#c = pycurl.Curl()
#c.setopt(pycurl.URL, github_url)
#c.setopt(pycurl.HTTPHEADER, ['X-Postmark-Server-Token: api-key_kh0La_9ex4zHNNPU5pusNYVBuRmlYNzbYWBTx6cwvVs=','Accept: application/json'])
#c.setopt(pycurl.POST, 1)
#c.setopt(pycurl.POSTFIELDS, data)
#saida = c.perform()
#print ("-"*200)+"\n"+str( saida )

#9
#para baixo votação
#favorito
#2
#Alguém poderia converter o seguinte exemplo Curl PostMark para pycurl?
#
#curl -X POST "http://api.postmarkapp.com/email" \
#
#-H "Accept: application/json" \
#
#-H "Content-Type: application/json" \
#
#-H "X-Postmark-Server-Token: ed742D75-5a45-49b6-a0a1-5b9ec3dc9e5d" \
#
#-v \
#
#-d "{From: 'sender@example.com', To: 'receiver@example.com', Subject: 'Postmark test', HtmlBody: '<html><body><strong>Hello</strong> dear Postmark user.</body></html>'}"

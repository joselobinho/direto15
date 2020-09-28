#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  boletocloud.py
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

from boletocloud import Ticket
ticket = Ticket('api-key_eNw4KWIJHz-z31RKq837waQj6ph7I8uLkGdRUhxCrWM=')

params = {
    'boleto.conta.banco': 237,
    'boleto.conta.agencia': '1234-5', 
    'boleto.conta.numero': '123456-0', 
    'boleto.conta.carteira': 12, 
    'boleto.beneficiario.nome': 'DevAware Solutions', 
    'boleto.beneficiario.cprf': '15.719.277/0001-46', 
    'boleto.beneficiario.endereco.cep': '59020-000', 
    'boleto.beneficiario.endereco.uf': 'RN',
    'boleto.beneficiario.endereco.localidade': 'Natal', 
    'boleto.beneficiario.endereco.bairro': 'Petrópolis', 
    'boleto.beneficiario.endereco.logradouro': 'Avenida Hermes da Fonseca', 
    'boleto.beneficiario.endereco.numero': 384,
    'boleto.beneficiario.endereco.complemento': 'Sala 2A, segundo andar', 
    'boleto.emissao': '2014-07-11',
    'boleto.vencimento': '2020-05-30', 
    'boleto.documento': 'EX1', 
    'boleto.numero': '12345678901-P', 
    'boleto.titulo': 'DM',
    'boleto.valor': '1250.43', 
    'boleto.pagador.nome': 'Alberto Santos Dumont', 
    'boleto.pagador.cprf': '111.111.111-11',
    'boleto.pagador.endereco.cep': '36240-000', 
    'boleto.pagador.endereco.uf': 'MG',
    'boleto.pagador.endereco.localidade': 'Santos Dumont', 
    'boleto.pagador.endereco.bairro': 'Casa Natal',
    'boleto.pagador.endereco.logradouro': 'BR-499', 
    'boleto.pagador.endereco.numero': 's/n',
    'boleto.pagador.endereco.complemento': 'Sítio - Subindo a serra da Mantiqueira', 
    'boleto.instrucao': 'Atenção! NÃO RECEBER ESTE BOLETO.',   
}

ticket.create(**params)

# -*- coding: utf-8 -*-
# Jose Lobinho
# 04-03-2017
# Adequacao do gerenciador de boletos para utilizar o servico { boleto cloud }
# pycurl python 2.7
# Teste de comunicacao p/download do pdf
# Teste rapido de compatibilidade
# Original: curl "https://sandbox.boletocloud.com/api/v1/boletos/pMLMOFhsurM2bCa4Ta3wGCgvZfce7LAheXJqxh268W4=" -u "api-key_kh0La_9ex4zHNNPU5pusNYVBuRmlYNzbYWBTx6cwvVs=:token" -o teste.pdf

import urllib
import pycurl
import commands
import json
from StringIO import StringIO

""" Metodo GET

response_buffer = StringIO()
curl = pycurl.Curl()

#-: emitir um boleto antes para pegar o id do boleto url /id_boleto
curl.setopt(curl.URL, "https://sandbox.boletocloud.com/api/v1/boletos/pMLMOFhsurM2bCa4Ta3wGCgvZfce7LAheXJqxh268W4=")

# cadastrar no sandbox antes para pegar o token Setup the base HTTP Authentication. { Numero do token }
curl.setopt(curl.USERPWD, '%s:%s' % ('api-key_kh0La_9ex4zHNNPU5pusNYVBuRmlYNzbYWBTx6cwvVs=','token'))

curl.setopt(curl.WRITEFUNCTION, response_buffer.write)


try:
	curl.perform()
	curl.close()
except Exception as error:
	print "______________________________ ",error

response_value = response_buffer.getvalue()

if "ERRO" in response_value.upper():

	# response_value retorna em str , transformando para dic
	r = json.loads(response_value)
	print r["erro"]["status"]
	print r["erro"]["tipo"]
	print r["erro"]["causas"][0]["codigo"]
	print r["erro"]["causas"][0]["mensagem"]
	print r["erro"]["causas"][0]["suporte"]

#-: se houver erro na url o retorno vem em html [ opcoes de viualizacao do html wx.html, browse, mupdf,evince
if "</HTML>" in response_value.upper() and "<!DOCTYPE" in response_value.upper():

	__arquivo = open("/mnt/lykos/direto/meu_boelto.html","w")
	__arquivo.write(response_value)
	__arquivo.close()

	__html = "/mnt/lykos/direto/meu_boelto.html"

	abrir = commands.getstatusoutput("firefox '"+__html+"'")

else:
	
	__arquivo = open("/mnt/lykos/direto/meu_boelto.pdf","w")
	__arquivo.write(response_value)
	__arquivo.close()

	abrir = commands.getstatusoutput("firefox /mnt/lykos/direto/meu_boelto.pdf")
"""




param = [("boleto.conta.banco","237"),
("boleto.conta.agencia","6467-0"),
("boleto.conta.numero","0000410-3"),
("boleto.conta.carteira","19"),
("boleto.beneficiario.nome","José de Almeida Lobinho"),
("boleto.beneficiario.cprf","475.791.535-72"),
("boleto.beneficiario.endereco.cep","22723-007"),
("boleto.beneficiario.endereco.uf","RJ"),
("boleto.beneficiario.endereco.localidade","rio de janeiro"),
("boleto.beneficiario.endereco.bairro","rio de janeiro"),
("boleto.beneficiario.endereco.logradouro","Rua Vale da Pedra Branca (Rio Grande)"),
("boleto.beneficiario.endereco.numero","340"),
("boleto.beneficiario.endereco.complemento","lote 6"),
("boleto.emissao","2014-07-11"),
("boleto.vencimento","2020-05-30"),
("boleto.documento","4"),
("boleto.sequencial","29"),
("boleto.titulo","DM"),
("boleto.valor","1250.43"),
("boleto.pagador.nome","Alberto Santos Dumont"),
("boleto.pagador.cprf","111.111.111-11"),
("boleto.pagador.endereco.cep","36240-000"),
("boleto.pagador.endereco.uf","MG"),
("boleto.pagador.endereco.localidade","Santos Dumont"),
("boleto.pagador.endereco.bairro","Casa Natal"),
("boleto.pagador.endereco.logradouro","BR-499"),
("boleto.pagador.endereco.numero","s/n"),
("boleto.pagador.endereco.complemento","Sitio - Subindo a serra da Mantiqueira"),
("boleto.instrucao","Atencao NAO RECEBER ESTE BOLETO."),
("boleto.instrucao","Este e apenas um teste utilizando a API Boleto Cloud"),
("boleto.instrucao","Mais info em http://www.boletocloud.com/app/dev/api")]


#data = params #json.dumps( params )
#print data
#print "__________________: ",type(data)




#values = [
#              ("key", your_api_key),
#              ("image", (c.FORM_FILE, image))]
    # OR:     ("image", "http://example.com/example.jpg")]
    # OR:     ("image", "YOUR_BASE64_ENCODED_IMAGE_DATA")]








#.setopt(pycurl.URL, github_url)
#c.setopt(pycurl.HTTPHEADER, ['X-Postmark-Server-Token: API_TOKEN_HERE','Accept: application/json'])
#c.setopt(pycurl.POST, 1)
#c.setopt(pycurl.POSTFIELDS, data)
#c.perform()

# nozzle_url = FIREHOSE_URL % api_fun

#    conn = pycurl.Curl()
#    conn.setopt(pycurl.USERPWD, "%s:%s" % (username, password))
#    conn.setopt(pycurl.URL, nozzle_url)
#    conn.setopt(pycurl.WRITEFUNCTION, callback)

#    data = urllib.urlencode(args)
#    conn.setopt(pycurl.POSTFIELDS, data)







data = urllib.urlencode(param)
response_buffer = StringIO()
body = StringIO()
c = pycurl.Curl()

c.setopt(pycurl.URL, "https://sandbox.boletocloud.com/api/v1/boletos")

c.setopt(pycurl.USERPWD, '%s:%s' % ('api-key_kh0La_9ex4zHNNPU5pusNYVBuRmlYNzbYWBTx6cwvVs=','token'))

#curl.setopt(curl.HTTPHEADER, ["Content-Type: application/x-www-form-urlencoded; charset=utf-8"])
#curl.setopt(pycurl.HTTPHEADER, ["Content-Type: application/x-www-form-urlencoded; charset=utf-8; Authorization: Bearer YOUR API TOKEN; Content-Type: application/json"])

#c.setopt(pycurl.HTTPHEADER, ['Accept: application/json','X-Requested-By:MyClient','Content-Type: application/x-www-form-urlencoded; charset=utf-8'])
c.setopt(pycurl.HTTPHEADER, ['X-Postmark-Server-Token: API_TOKEN_HERE','Accept: application/json','Content-Type: application/x-www-form-urlencoded; charset=utf-8'])



#c.setopt(pycurl.POST, 1)
#c.setopt(pycurl.CUSTOMREQUEST, "POST")
c.setopt(pycurl.POST, True)
c.setopt(pycurl.TIMEOUT , 300)
#curl.setopt(curl.HTTPPOST, json.dumps( params ))

#params  = "boleto.conta.banco=237"
#params += "boleto.conta.agencia=6467-0"
a = 'boleto.conta.banco=237'
#a +='\nboleto.conta.agencia=6467-0'
#c.setopt(c.HTTPPOST, a)
c.setopt(pycurl.POSTFIELDS, data )
#curl.setopt(pycurl.POSTFIELDS, "boleto.conta.agencia=6467-0")

c.setopt(pycurl.WRITEFUNCTION, response_buffer.write)
c.setopt(pycurl.HEADERFUNCTION, body.write)


c.perform()
print c.getinfo(pycurl.RESPONSE_CODE)
c.close()

response_value = response_buffer.getvalue()
print response_value
print("-"*200)
#print json.loads( body.getvalue() )
ssb1 = body.getvalue()
print ssb1.split('\n')
#ssb2 = json.loads( json.dumps( body.getvalue() ) )
#print type( ssb1 ),type( ssb2 )
for i in ssb1.split('\n'):
	if "LOCATION:" in i.upper() and len( i.split(':') ) >=2:
		print i.split(':')[1]
		
#print response_value
__arquivo = open("/mnt/lykos/direto/meu_boelto.pdf","w")
__arquivo.write(response_value)
__arquivo.close()

#abrir = commands.getstatusoutput("firefox /mnt/lykos/direto/meu_boelto.pdf")


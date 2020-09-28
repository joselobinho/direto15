use frnecdor
l = "fornecedor.txt"
set printer to (l)
set device to print
a := 0

do while !eof()


	? fc_codigo+'|'+fc_nome+'|'+fc_fantas+'|'+fc_cnpj  +'|'+fc_cpf+'|'+fc_docume+'|'+fc_iestad+'|'+fc_tipo  +'|'+fc_endere+'|'+fc_bairro+'|'+fc_cidade+'|'+fc_cdibge+'|'+fc_cep+'|'+fc_compl1+'|'+fc_compl2+'|'+fc_estado+'|'+fc_email +'|'+fc_telef1+'|'+fc_telef2+'|'+fc_telef3+'|'+fc_conta1+'|'+fc_email1+'|'+fc_telco1+'|'+fc_conta2+'|'+fc_email2+'|'+fc_telco2+'|'+fc_telco3+'|'+fc_telco4

   a = a + 1
   skip
   
enddo

set printer to
set device to screen

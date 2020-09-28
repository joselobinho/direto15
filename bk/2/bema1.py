#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Buffer =  '#27 + #97 + #1 + #29 + #107 + #81 +  #2 + #12 + #8 + #1 + #19 + #0 + #119 + #119 + #119 + #46 + #98 + #101 + #109 + #97 + #116 + #101 + #99 + #104 + #46 + #99 + #111 + #109 + #46 + #98 + #114;'
Buffer = chr(29)+'(k'+chr(4)+chr(0)+'1A2'+chr(0)+\
                     chr(29)+'(k'+chr(3)+chr(0)+'1C'+chr(4)+\
                     chr(29)+'(k'+chr(3)+chr(0)+'1E0'+\
                     chr(29)+'(k'+Int2TB(length(qrcode)+3)+'1P0'+qrcode+\
                     chr(29)+'(k'+chr(3)+chr(0)+'1Q0'








__arquivo = open("/mnt/lykos/bema.txt","w")
__arquivo.write( Buffer )
__arquivo.close()

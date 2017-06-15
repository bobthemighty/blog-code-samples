version=2

rule=http:%remote_addr:word% %ident:word% %auth:word% [%timestamp:char-to:]%] "%method:word% %request:word% HTTP/%httpversion:float%" %status:number% %bytes_sent:number% "%referrer:char-to:"%" "%agent:char-to:"%"%blob:rest%
rule=http:%remote_addr:word% %ident:word% %auth:word% [%timestamp:char-to:]%] "%method:word% %request:word% HTTP/%httpversion:float%" %status:number% %bytes_sent:number% "%referrer:char-to:"%" "%agent:char-to:"%"
rule=http: %remote_addr:word% %ident:word% %auth:word% [%timestamp:char-to:]%] "%method:word% %request:word% HTTP/%httpversion:float%" %status:number% %bytes_sent:number% "%referrer:char-to:"%" "%agent:char-to:"%"%blob:rest%
rule=http: %remote_addr:word% %ident:word% %auth:word% [%timestamp:char-to:]%] "%method:word% %request:word% HTTP/%httpversion:float%" %status:number% %bytes_sent:number% "%referrer:char-to:"%" "%agent:char-to:"%"


rule=json:%body:json%
rule=json: %body:json%

rule=log4j: [%levelname:char-to:]%] %message:rest%
rule=log4j:[%levelname:char-to:]%] %message:rest%

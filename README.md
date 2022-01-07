## Struktura packetu
---
1024B - Délka max

  -Struktura-     
Velikost packetu= *512B*     
1. Pořadové číslo: číslování (*1byte=1pořadí*)    
           číslovat od 00 do *99*, u příchozí strany řadit od 00 do *99* a opakovat (*99 asi? určit podle odezvy*)     
           
2. Typ dat: označení (*1byte=1typ*)   
           00 - data osobní     
           01 - řídící informace     
           02 - handshake/responde      
           03 - keep alive     
           04 - acknowledgement
           
3. Data: (*510byte=1data)    
           samotné data pro přenos mezi klienty     


---
   
## Struktura komunikačního packetu mezi klientem a serverem
---

Registrace (c -> s) - 1B 392B 32B
1. Typ packetu (hex 11)
2. Veřejný klíč (ascii)
3. Hostname (ascii)

Acknowledged, Not acknowledged (% -> %) - 1B
1. Typ packetu (hex 00 - ack, hex 01 - nack)

Připojit se (c -> s) - 1B 392B
1. Typ packetu (hex 12)
2. Veřejný klíč vzdálené strany (ascii)

Sestava připojení (s -> c) - 1B 4B 2B 2B
1. Typ packetu (hex 13)
2. Vzdálená IP adresa (ve formátu 1B.1B.1B.1B)
3. Vzdálený port (16Bit číslo)
4. Lokalní port (16Bit číslo)

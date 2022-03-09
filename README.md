# μPeer

## Struktura packetu

---
1500B - Délka max
 
Velikost packetu= *1024B*  


1. pořadové číslo *(2Byte)*      
    od 0000 do FFFF
           
2. Typ dat: označení *(1Byte)*   
           00 - data osobní     
           01 - řídící informace     
           02 - handshake/response      
           03 - keep alive     
           04 - acknowledgement
           
3. Data: *(1024byte)*    
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

Připojit se (c -> s) - 1B 392B 392B

1. Typ packetu (hex 12)
2. Veřejný klíč klienta
3. Veřejný klíč vzdálené strany (ascii)

Žádost o připojení (s -> c) - 1B 392B

1. Typ packetu (hex 13)
2. Veřejný klíč strany, která se chce připojit (ascii)

Sestava připojení (s -> c) - 1B 4B 2B 2B

1. Typ packetu (hex 14)
2. Vzdálená IP adresa (ve formátu 1B.1B.1B.1B)
3. Vzdálený port (16Bit číslo)
4. Lokalní port (16Bit číslo)

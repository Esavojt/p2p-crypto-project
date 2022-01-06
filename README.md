## Struktura packetu
---
1024B - Délka max
518B - Aktuální předpoklad

Struktura - pořadové číslo (2 byte max), typ dat (*4* byte), packet (512 byte max) 
1. Pořadové číslo: číslovat od 1 do *64*, u příchozí strany řadit od 1 do *64* a opakovat (*64 asi? určit podle odezvy*)
2. Typ dat: označení (*pro 3 písmena rezervovat 4B*) ODT- data osobní, CDT- řídící info, RDT- handshake/responde
3. Packet: samotné data pro přenos mezi klienty


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

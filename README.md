## Struktura packetu
---
1024B - Délka max

Struktura - 1B 1B xB
1. Pořad. číslo
2. Typ packetu (control, data)
3. Data


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
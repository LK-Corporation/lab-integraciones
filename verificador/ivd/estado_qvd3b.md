# Estado: Q-VD-3 otra vez, con un hecho que faltaba (5-nov-2026)

Redactado el 5-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

En `estado_qvd.md` se preguntó si la pasada de repeticiones entra en el veredicto de la etapa 32 (las muestras públicas validadas
con el esquema de IRIS de la versión que declaran). Salió «dentro» con 0,75 frente a 0,25 y una confianza de 0,5. Al estado le
faltaba lo que dice el texto del estándar sobre los campos de más.

## Hechos

1. **Lo que da IRIS en esa pasada:** «el segmento tiene más campos de los que permite la estructura». Se para en el primero: el
   conductor no sabe enmudecerlo. Contra v2.5, lo dieron 194 muestras; en todas el segmento tenía, de verdad, más campos que la
   tabla de atributos de v2.5, y en 176 alguno de esos campos de más llevaba valor.
2. **El texto de v2.5, «Rules for the recipient»** (CH02.txt:932-935): el receptor ignora los segmentos, campos, componentes,
   subcomponentes y repeticiones de más que no esperaba. **«Adding messages or message constituents»** (CH02.txt:1143-1147): el
   receptor, sea de la versión que sea, tiene que ignorar lo que no espera sin fallar.
3. **La etapa 31 se apoyó en ese mismo pasaje** (Q-MV-4) para quitar, y poner aparte, los segmentos que v2.5 no define. No los
   contó como error.
4. **En su propia versión,** un campo de más es uno que ni su versión define. Contra v2.5 la mayoría eran MSH con los campos que
   añadieron versiones posteriores; en su versión, esos ya no sobran.
5. **Si entra,** la regla para la 2.5.1 sería mirar la tabla de atributos del texto de v2.5.1; para las versiones sin texto, lo que
   diga IRIS. **Si se mide aparte,** se cuenta cuántas muestras lo dan en su versión, como en la 31.

## La pregunta

- **Q-VD-3b.** ¿Un segmento con más campos de los que permite la estructura de su versión hace inválida la muestra?
  - (a) No: se mide aparte, como en la 31, por las reglas del receptor del texto.
  - (b) Sí: entra en el veredicto como error de estructura.

# Estado: Q-IV-D-11 otra vez, con los hechos que faltaban (4-nov-2026, noche)

Redactado el 4-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 30 pasa los 723 mensajes sintéticos publicados por el validador de IRIS y cuenta solo lo que el texto de HL7 v2.5
sostiene. Q-IV-D-11 decidió cómo contar UCUM y SCT, que la tabla 0396 impresa no trae. Se decidió «cuenta», con 0,42 frente a 0,30
y 0,28 y confianza 0,13. El estado de entonces (`estado_qiv11.md`) decía solo que la 29 lo dejó como duda sistémica. Una revisión
a ciegas independiente encontró en el texto hechos que aquel estado no traía, y que afectan a todo valor fuera de una tabla de
HL7, no solo a la 0396. Se vuelve a preguntar, más amplio.

## Hechos

1. **El texto general de v2.5 sobre las tablas de HL7** (CH02.txt:562-565): sus valores no se pueden redefinir localmente, pero
   «the table itself may be extended to accommodate locally defined values».
2. **Para las unidades** (CH07.txt:2931-2933), el texto anima a usar ISO+, pero permite otros sistemas de códigos y los códigos
   locales. Para las unidades del tipo RPT (CH02A.txt:4678 y 4730), manda usar UCUM.
3. **La 0396** remite también al servidor de listas de HL7 (CH07.txt:2674).
4. **La 29:** el auditor de VXU leyó UCUM como admisible, con estas citas; el de ORU lo dejó en duda porque la lista impresa
   podría no ser cerrada.
5. **El método ya deja sin decidir** OBX-2 = `CWE`, que es la misma contradicción entre la tabla impresa y el texto.
6. **Los valores fuera de una tabla de HL7 que hay en los datos:**
   - UCUM en RXA-7 (96) y OBX-6 (80), y SCT en SPM-4 y RXR-2 (1 cada uno), todos en la 0396;
   - MSH-12 = `2.5.1` (8) y `2.6` (1) en la 0104;
   - OBX-11 = `f` en minúscula en la 0085 (1);
   - PID-30 = `NO` en la 0136 (1), en el caso de un par mínimo;
   - un `D` en la 0465 (1).
7. **Lo que da cada opción en los 723:**
   - si cuentan: 246 inválidos y 200 sin decidir;
   - si quedan todos sin decidir: 94 inválidos y 352 sin decidir;
   - si solo la 0396 queda sin decidir: 104 inválidos y 342 sin decidir.

   Los 277 válidos no cambian. En las 27 nuevas, las 12 que se apoyan solo en mensajes inválidos lo son solo por UCUM.

## La pregunta

Q-IV-D-11, un valor que no está en la lista impresa de una tabla de HL7 de v2.5:
- (a) cuenta como inválido: manda la lista impresa;
- (b) queda sin decidir siempre: el texto permite extender las tablas de HL7 con valores locales;
- (c) queda sin decidir en la 0396, por el texto de las unidades y de RPT, y cuenta en las demás tablas.

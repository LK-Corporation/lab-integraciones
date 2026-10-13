# Cambios de las copias publicadas respecto a las selladas

Los documentos de esta carpeta son los del repositorio de trabajo, byte a byte, **salvo los cambios de higiene de abajo**:
- la guarda pública no admite rutas de una máquina concreta;
- el comprobador de enlaces tomaba una expresión regular por un enlace;
- la guarda privada no deja publicar los nombres de operador del catálogo que no son públicos ni los nombres de las máquinas.

Ninguno cambia una cifra, una regla ni una decisión. Por estos cambios, la huella de esas copias ya no es la sellada; las huellas
que citan los sellos son las de los originales.

**Censura de nombres:** en `agente/diseno-agente-fable.md`, tres nombres de operador del catálogo de mutaciones de la fase 12
(los que citaba como receta de construcción de tres casos R) dicen ahora «operador del catálogo (no publicado)». Un nombre de
máquina dice ahora «otra máquina».

| Fichero | Decía | Dice |
|---|---|---|
| `agente/amp/diseno-ampliacion-fable.md` | la carpeta de cajas como ruta del directorio del usuario | «la carpeta de cajas del agente, fuera del repositorio» |
| `agente/amp/diseno-ampliacion-fable.md` | la expresión regular de los puertos, con un grupo `(?!…)` que se leía como enlace | la misma expresión descrita en palabras |
| `agente/diseno-agente-fable.md` | la carpeta de cajas como ruta del directorio del usuario | «una carpeta `ag-caja/<id>/` en el directorio del usuario» |
| `etapa/SELLO-AG1.md` | ídem | «una carpeta `ag-caja/<opaco>/` fuera del repositorio» |
| `etapa/SELLO-AG2-ANTES.md` | ídem | «la carpeta de cajas del agente (fuera del repositorio)» |

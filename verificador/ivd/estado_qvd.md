# Estado: cómo validar las muestras públicas en la versión que declaran (5-nov-2026)

Redactado el 5-nov-2026. **A propósito NO incluye la recomendación de nadie.**

## Contexto

La etapa 32 (elegida por Jev, `decision-jev-ruta16.md`: 0,84) pasa las muestras públicas de los dos conversores por el validador
de IRIS con el esquema de la versión que declaran en MSH-12, no con el de v2.5. La etapa 31 las validó contra v2.5, como las lee el
juez, y dejó dicho que no sabe si son válidas en su propia versión. Esta etapa no cambia el juez.

## Hechos

1. **Las muestras:** 225; 223 declaran otra versión que la 2.5: 108 la 2.6, 64 la 2.8, 44 la 2.5.1 y 7 la 2.3 o la 2.4. El IRIS
   del laboratorio trae los esquemas de 2.1 a 2.8.2. El laboratorio tiene el texto de v2.5 y el de v2.5.1, no el de las demás.
2. **Lo que IRIS acertó frente al texto de v2.5** en las filas de las etapas 30 y 31 (cada error que IRIS dio, leído en el texto):
   - estructura (segmento que falta o sobra): 130 de 130 sostenidos por el texto;
   - obligatorios: 960 de 960;
   - longitudes: 932 de 932;
   - tablas de HL7: en la 30, 874 de 1.098 tenían el valor en la tabla del estándar (el esquema de IRIS la trae incompleta); en la
     31, 389 de 1.548;
   - tablas de usuario: el esquema de IRIS las trae vacías; 13.591 errores que son eso y nada más.
   Esto mide solo lo que IRIS dijo, no lo que no vio. Y es contra el esquema de v2.5: nada dice que los de 2.6 o 2.8 se porten
   igual.
3. **Leer las de la 2.5.1 con su texto,** como la 30 leyó con el de v2.5, pide rehacer desde el texto de v2.5.1 las tablas (el
   guion de la 30 toma la carpeta del texto como argumento) y la tabla de campos de 16 segmentos (longitudes y obligatoriedad),
   que hoy es de v2.5. En la 31, Q-MV-1 decidió validar las de la 2.5.1 contra v2.5, como las lee el juez.
4. **La pasada de repeticiones** (un segmento con más campos de los que permite la estructura): contra v2.5 la dieron 194
   muestras, todas ciertas frente a la tabla de atributos de v2.5. El conductor no reconoce esa forma de error, así que en la 31
   se midió aparte y no entró en el veredicto, como en la 30, donde no dio nada. En su propia versión esos campos pueden existir.
5. **Sin el texto de una versión,** lo que se cuente es «lo que dice IRIS», no lo que dice el estándar. El resultado tendría que
   decirlo así.

## Las preguntas

- **Q-VD-1.** En las versiones sin texto en el laboratorio (2.3, 2.4, 2.6 y 2.8), ¿qué cuenta como error?
  - (a) Estructura, obligatorios y longitudes, como los da IRIS; las tablas de HL7, sin decidir; las de usuario, aviso.
  - (b) Todo lo que da IRIS, salvo las tablas de usuario vacías.
  - (c) Solo la estructura.
- **Q-VD-2.** ¿Cómo se leen las 44 de la 2.5.1?
  - (a) Como las demás, con la regla de Q-VD-1.
  - (b) Con el texto de v2.5.1, como la 30 con el de v2.5.
- **Q-VD-3.** ¿La pasada de repeticiones entra en el veredicto?
  - (a) No: se mide aparte, como en la 31.
  - (b) Sí: es un error de estructura que IRIS da desde el esquema de la versión.

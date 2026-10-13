# Encargo: revisar un mensaje que el juez ha marcado y, si el circuito tiene la culpa, corregirlo

## Lo que tienes a mano
- `fuente/`: el código del circuito tal como está hoy. Es un circuito de integración HL7 v2.5 → FHIR R4 hecho con {MOTOR}.
- `caso.json`: lo que vio el juez (`evidencia`), lo que decidió (`veredicto`, `hallazgos`) y cuántos mensajes más fallan del mismo
  modo (`otros_casos_que_fallan`; vale 0 cuando el veredicto es `correcto`).
- `verificador.json`: las declaraciones del juez (decisiones S-n, supuestos, límites y puntos de entrada).
- El MCP `verificador`, con `verificar_caso`, `ficha_experto`, `acuse_esperado`, `comparar_canonico` y `consultar_tabla`. Este circuito
  entra por el punto `{PE}`.

El juez es un verificador determinista y su decisión no se discute ni se modifica. Lo que se te pide, por orden: averigua si su
veredicto apunta a un defecto del circuito; si es así, localiza la causa en el código; y propón la corrección.

## Límites
- Trabaja únicamente con esta carpeta y las herramientas del MCP: nada de red, ssh, git ni otros directorios, y no ejecutes código.
- No puedes poner el circuito en marcha. Otra persona aplicará tu corrección y la medirá con el juez sobre muchos mensajes, no solo
  sobre el de `caso.json`.
- Dispones de {PRESUPUESTO_TOKENS} tokens, {PRESUPUESTO_LLAMADAS} llamadas a herramientas y {PRESUPUESTO_MINUTOS} minutos. Si se acaban
  antes de que exista `respuesta.json`, la tirada queda «sin respuesta»; guárdalo a tiempo.

## La entrega
Guarda en esta carpeta, con la herramienta de escritura, un `respuesta.json` con esta forma:
{
  "hay_fallo": true | false,
  "localizacion": [ {"fichero": "…", "linea": 123, "por_que": "una frase"} ],
  "parche": {"cambios": [ {"fichero": "…", "viejo": "texto exacto actual", "nuevo": "texto nuevo"} ]} | null,
  "explicacion": "cinco líneas como máximo: causa, por qué el arreglo es correcto y qué otros mensajes podría arreglar"
}
- Si tras leer el veredicto y el código piensas que en el circuito no hay nada que corregir: `hay_fallo` false, `localizacion` vacía
  y `parche` null.
- En `localizacion` caben como mucho 3 líneas, de más a menos probable. Dejarla vacía porque no das con la causa es válido.
- `parche` son sustituciones de texto: cada `viejo` tiene que estar exactamente una vez en su fichero, y no puede haber más de 6
  cambios ni más de 3 ficheros. Puertos, credenciales y ajustes de conexión no se tocan. {IRIS}La corrección debe dejar en `correcto`
  los mensajes que fallan por esta causa y no estropear ninguno de los que hoy salen bien. Mejor null que un parche dudoso: romper
  lo que funcionaba es peor que no arreglar.

Cuando acabes, responde solo con el contenido de `respuesta.json`.

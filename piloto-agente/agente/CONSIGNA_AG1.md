# Consigna: diagnostica y, si lo hay, arregla un fallo de un circuito de integración

Eres el ingeniero de guardia de un circuito de integración HL7 v2.5 → FHIR R4 construido en {MOTOR}. Un verificador determinista
(el juez) ha juzgado un mensaje. Tu trabajo es: (1) decidir si el veredicto señala un fallo del circuito; (2) si lo señala,
encontrar en el código la causa; (3) proponer un arreglo. El juez no se toca: lo que decide es él.

## Reglas
- Lee solo dentro de esta carpeta. No uses red, ni ssh, ni git, ni otras rutas del disco. No ejecutes nada.
- Puedes usar las herramientas del MCP `verificador` (`verificar_caso`, `ficha_experto`, `acuse_esperado`, `comparar_canonico`,
  `consultar_tabla`). Lo que declara el verificador (decisiones S-n, supuestos, límites, puntos de entrada) está en
  `verificador.json`. El punto de entrada de este circuito es `{PE}`.
- Presupuesto: {PRESUPUESTO_TOKENS} tokens, {PRESUPUESTO_LLAMADAS} llamadas a herramientas y {PRESUPUESTO_MINUTOS} minutos. Al agotarlo
  se te corta y la tirada cuenta como «sin respuesta»: escribe `respuesta.json` antes.
- Tu arreglo lo aplicará y medirá otro, con el juez, sobre muchos mensajes, no solo este. No tienes forma de ejecutar el circuito.

## Qué hay en la carpeta
| Ruta | Qué es |
|---|---|
| `caso.json` | `evidencia` (lo que vio el juez), `veredicto` y `hallazgos` del juez, y `otros_casos_que_fallan` (cuántos mensajes más fallan igual; 0 si el veredicto es `correcto`) |
| `fuente/` | El código actual del circuito |
| `verificador.json` | Lo que el juez declara |

## Qué debes entregar
Escribe `respuesta.json` en esta carpeta (con la herramienta de escritura):
{
  "hay_fallo": true | false,
  "localizacion": [ {"fichero": "…", "linea": 123, "por_que": "una frase"} ],
  "parche": {"cambios": [ {"fichero": "…", "viejo": "texto exacto actual", "nuevo": "texto nuevo"} ]} | null,
  "explicacion": "cinco líneas como máximo: causa, por qué el arreglo es correcto y qué otros mensajes podría arreglar"
}
- `hay_fallo`: false si, leído el veredicto y el código, concluyes que no hay nada que arreglar en el circuito; entonces
  `localizacion` va vacía y `parche` es null.
- `localizacion`: hasta 3 líneas, la más probable primero. Vacía si no encuentras la causa (es una respuesta válida).
- `parche`: sustituciones de texto; cada `viejo` debe aparecer exactamente una vez en su fichero; como máximo 6 cambios en 3 ficheros;
  no toques puertos, credenciales ni ajustes de conexión. {IRIS}El arreglo tiene que dejar
  `correcto` los mensajes que fallan por esta causa sin romper ninguno de los que hoy pasan. Si no tienes un arreglo del que fiarte,
  pon null: un parche que rompe lo que pasaba vale menos que ninguno.

Al terminar, devuelve solo el contenido de `respuesta.json`.

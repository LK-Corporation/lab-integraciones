# Etapa 18: verifica tu conversor en un comando (24-oct-2026)

**Hecho.** Un tercero pasa su conversor HL7 v2 → FHIR R4 por el verificador con un fichero de adaptador JSON y una orden, sin
escribir código:

```bash
python3 cv/verificar_conversor.py <adaptador.json> <carpeta de salida> --artefactos <carpeta con el conversor>
```

**El control cuadra.** Con los adaptadores de Microsoft y LinuxForHealth, la herramienta da exactamente los mismos veredictos
que el estudio de conversores, caso por caso, con el mismo juez:
- **los 368 casos de cada conversor:** 0 diferencias en estado, categoría, subtipo y hallazgos que cuentan;
- **los pares mínimos:** coinciden los 34.

El detalle está en [`vc/CONTROL-VC.md`](vc/CONTROL-VC.md). La comparación caso por caso se hizo con el detalle del estudio, que
no es público; lo que se puede repetir desde aquí lo dice ese documento.

Dos informes de ejemplo, sobre el corpus que viaja con el repositorio, están en [`vc/ejemplos/`](vc/ejemplos/). Se hicieron con
el juez del laboratorio, `40bbc3ef…`. Corridos desde esta copia, la cabecera dirá `0dd3ae5c…`: se diferencia en un extracto que
el juez cita, no en su lógica (ver [`../MANIFIESTO.txt`](../MANIFIESTO.txt)). Todo lo demás debe coincidir.

La pregunta y sus condiciones están en [`../ANTES-ETAPA-VERIFICA-CONVERSOR.md`](../ANTES-ETAPA-VERIFICA-CONVERSOR.md).

## Cómo se usa

**Con uno de los dos conversores del estudio:** `--artefactos` apunta a una carpeta con lo que pide su adaptador. Para
Microsoft, `ms/out` (la herramienta compilada) y `ms/src/data/Templates/Hl7v2`; para LinuxForHealth, `lfh/lib`, `lfh/clases` y
`lfh/Arnes.java`. Cómo se construyeron está en [`CV1.md`](CV1.md). La imagen de Docker tiene que estar ya en la máquina.

**Con el tuyo:** copia uno de los cuatro adaptadores de [`adaptadores/`](adaptadores/) y cambia los datos:
- el nombre, la versión y las partes de la huella;
- la imagen y los montajes, siempre de solo lectura y con rutas relativas a `--artefactos`;
- la orden, con sus marcadores (`{entrada_dir}`, `{salida_dir}`, `{entrada_fichero}`, `{salida_fichero}`, `{base}`,
  `{nombre}`, `{plantilla}`);
- y cómo se lee la salida: el Bundle tal cual o envuelto, y el fichero de error si lo hay.

El formato entero está en el §2 del diseño ([`vc/diseno-vc-fable.md`](vc/diseno-vc-fable.md)), con las desviaciones de abajo.
Antes de correr nada, `--solo-orden` valida el adaptador, calcula la huella e imprime la orden de Docker del primer grupo.

**Lo que escribe en la carpeta de salida:**
- `ADAPTADOR.json`, el adaptador normalizado;
- `CORRIDA.json`, con lo variable: fecha, duraciones y rutas;
- `corpus/`, con su manifiesto;
- `cajas/`, el registro de cada contenedor;
- `evidencias/`, una por mensaje;
- `juicio.jsonl`, una fila por caso;
- `INFORME.json`, sin fechas, tiempos ni rutas. La herramienta es determinista: con un conversor que también lo sea, dos
  corridas dan el mismo fichero byte a byte (P-VC-20). Microsoft no lo es del todo: algunos de sus textos de error llevan
  identificadores aleatorios, y el texto de esos rechazos cambia de una corrida a otra, aunque el veredicto no;
- `INFORME.md`.

**Las opciones** (también en `--help`):
- **El corpus:**
  - `--corpus <carpeta>` añade mensajes propios (`*.hl7`, con cualquier salto de línea); se puede repetir;
  - `--muestras <carpeta>` añade las muestras de los proyectos, en subcarpetas `ms/` y `lfh/`, como en el estudio;
  - `--sin-corpus-lab` quita las bases A1/E2 y las ORU del laboratorio;
  - `--sin-minimos` quita los 68 mínimos, que solo entran con los dos conversores del estudio;
  - `--limite-casos N` corre solo los N primeros de cada corpus, como prueba de humo.
- **El juicio:**
  - `--sin-sensibilidad` no calcula las alternativas de Q-CV-D-3, 5 y 9;
  - `--desde-evidencias` vuelve a juzgar las evidencias de una corrida anterior, sin correr el conversor;
  - `--comparar <juicio.jsonl>` compara caso por caso con otra corrida.
- **La salida:**
  - `--solo-orden` no corre nada;
  - `--json-solo` no escribe `INFORME.md`.

**Los códigos de salida:**

| Código | Qué quiere decir |
|---|---|
| 0 | todo juzgado |
| 2 | el adaptador no es válido, o la carpeta de salida no está vacía y no es de una corrida anterior |
| 3 | Docker o la imagen no están |
| 4 | la caja falló en algún grupo; hay informe, con lo no juzgado |
| 5 | `--comparar` encontró diferencias |
| 1 | error interno |

## Qué hace

1. **Lee el adaptador.** Es un JSON declarativo con cinco bloques: el conversor, la caja, la invocación, la salida y, dentro de
   la caja, los límites. No admite ganchos, scripts ni expresiones; lo que no cabe en él es un límite declarado (L-VC-3).
2. **Corre el conversor en la caja de siempre:** Docker sin red, sistema de ficheros de solo lectura, usuario 65534, sin
   capacidades, sin escalada de privilegios y con límite de procesos. Ningún campo del adaptador las quita (S-VC-3).
3. **Escribe una evidencia por mensaje** con la forma que ya lee el juez (S-CV-2) y la juzga con `verificador.verificar`, sin
   tocarlo. La huella del juez no cambia.
4. **Agrega** por las ocho clases que cambian el significado (S-CV-5), aparta los rechazos y evalúa los pares mínimos del
   estudio con la misma regla de `cv3_minimos.py`.
5. **Escribe el informe**, `INFORME.md` y `INFORME.json`. Antes de los resultados va lo que la herramienta no puede saber: si el
   proyecto del conversor ya tenía declarada cada discrepancia. Ese contraste lo hace una persona, como en
   [`RESULTADO-CV3.md`](RESULTADO-CV3.md); hasta entonces, cada mecanismo es «sin_contraste» (L-VC-1).

Los adaptadores de los dos conversores del estudio están en [`adaptadores/`](adaptadores/): reproducen, opción por opción, la
invocación de `correr_conversor.py`. El del conversor de juguete es el de las pruebas. LinuxForHealth tiene además un
adaptador mensaje a mensaje, [`adaptadores/linuxforhealth-mensaje.json`](adaptadores/linuxforhealth-mensaje.json): el mismo
conversor, un proceso por mensaje (etapa 21). Con él, los 436 casos del estudio dan los mismos veredictos que en lote
([`../RESULTADO-ARRASTRE.md`](../RESULTADO-ARRASTRE.md)).

## Cómo se hizo

- **El diseño, a ciegas:** lo escribió otro modelo (Claude Fable 5.1) leyendo solo el repositorio público
  ([`vc/ENCARGO-VC0.md`](vc/ENCARGO-VC0.md), [`vc/diseno-vc-fable.md`](vc/diseno-vc-fable.md)).
- **Nueve preguntas de diseño, decididas por Jev** con un estado neutro, sin la recomendación del diseñador
  ([`vc/estado_qvc.md`](vc/estado_qvc.md), [`vc/decision-jev-qvc.md`](vc/decision-jev-qvc.md)). Cuatro salieron con confianza
  baja (por debajo de 0,3); se aplican igual y se dicen:

| Q | Decisión de Jev | Confianza | Qué cambia |
|---|---|---|---|
| Q-VC-D-1 | las dos huellas: la del estudio en la evidencia y la de nombres en el informe | 0,28 | renombrar un fichero cambia la segunda |
| Q-VC-D-2 | un conversor que sale con 0 sin escribir nada da «vacio» | 0,02 | el juez dice indeterminado, no rechazo |
| Q-VC-D-3 | los 68 mínimos, solo con los dos conversores del estudio | 0,10 | un tercero no los ve en su informe |
| Q-VC-D-4 | la imagen por etiqueta; se registra el digest y se exige si el adaptador lo da | 0,94 | |
| Q-VC-D-5 | el Bundle envuelto se recorta del texto, sin reescribirlo | 0,48 | se conserva `1.20` |
| Q-VC-D-6 | sin límite de memoria por omisión | 0,52 | |
| Q-VC-D-7 | «el mismo veredicto» = estado, categoría, subtipo y los hallazgos que cuentan | 0,30 | el texto de cada hallazgo no cuenta |
| Q-VC-D-8 | lo que el adaptador declara que el proyecto no convierte se separa en el informe; el juez no cambia | 0,95 | |
| Q-VC-D-9 | tras un tiempo vencido, los mensajes sin salida se reintentan uno a uno | 0,26 | un mensaje lento no arrastra a su grupo |

- **Las pruebas, en rojo antes del código:** [`prueba_vc.py`](prueba_vc.py), P-VC-1..26, fallaron las 26 porque el módulo no
  existía. Corren sin Docker, con el conversor de juguete ([`conversor_juguete.py`](conversor_juguete.py)) y con un ejecutor
  espía que registra las órdenes de Docker sin correrlas. Hoy: `PRUEBAS VC: TODO BIEN (152 comprobaciones, 26 pruebas)`.

## El control

Se hizo en la máquina del laboratorio, con el juez del estudio (`40bbc3ef`) y con la herramienta ya cerrada (huella
`1ea91cf2…`). Los pasos van en orden, y cada uno podía parar el control:

0. **La caja no cambia al conversor:** el conversor de juguete da los mismos seis veredictos dentro de Docker que fuera.
1. **Las identidades cuadran antes de correr nada:** las huellas de los dos conversores, la del juez y las 368 líneas del
   manifiesto del corpus son las del estudio.
2. **Las dos corridas, caso por caso:** 0 diferencias en los 368 casos de cada conversor. Microsoft tardó 233 s y
   LinuxForHealth, 17 s, con los 68 mínimos incluidos.
3. **Lo público:**
   - las categorías por corpus son las de `RESULTADO-CV2.json`, salvo en las muestras de Microsoft, donde la diferencia es el
     arreglo del juez de CV4 que ya estaba previsto;
   - los pares mínimos coinciden con la confirmación de CV4 en los 34; con la de CV3, que es pública, en 33. La excepción es
     el par de CX.4, que CV4 arregló.
4. **Los informes sin las muestras,** que son los que puede repetir cualquiera, pasan su propia comprobación.

No hubo ninguna diferencia que adjudicar. Lo que no se puede repetir desde aquí es la comparación caso por caso: el detalle del
estudio no es público (L-VC-8).

## Dos defectos del arnés del estudio, medidos

El diseño señaló dos cosas que `correr_conversor.py` hacía y la herramienta no hace. Se midió si alguna movió un veredicto
publicado:

- **El Bundle de Microsoft se reescribía** con `json.loads` y `json.dumps`, y eso convierte `1.20` en `1.2`. El juez lee los
  números como texto y la precisión cuenta (Q-CV-D-10). En los 368 casos de Microsoft, el único hallazgo sobre un valor numérico
  es `.5` convertido en `5`, que la reescritura no produce. **Ningún veredicto publicado depende de ella.**
- **Un código 0 sin salida se registraba como error.** En el estudio no pasó nunca: los 74 errores de Microsoft salieron con
  código 255 y los 139 de LinuxForHealth son excepciones escritas por su arnés.

## Desviaciones del diseño (DV-VC-n)

| Id | Qué | Por qué |
|---|---|---|
| DV-VC-1 | La publicación sigue la opción B del laboratorio (guarda, higiene, revisión a ciegas y Jev), no el visto bueno previo del autor que pedía el diseño; el tope es el del ANTES, dos sesiones | el diseño no conocía el mandato vigente |
| DV-VC-2 | La directiva del juguete va en MSH-8, no en MSH-3 | `adt_conv` consume MSH-3 |
| DV-VC-3 | El juguete reproduce 13 de los 34 pares mínimos, no 2 | su Bundle genérico omite campos (ubicación, tipo de servicio, sufijo del nombre…), y el caso da el mismo «falta» que busca el par; la prueba fija la lista |
| DV-VC-4 | El adaptador se valida a mano, con un código por regla (`json_invalido`, `mensaje_sin_contenedor`, `imagen_obligatoria`…), no con un esquema genérico | los códigos los pide P-VC-2 y un esquema no los da |
| DV-VC-5 | Sin los marcadores `{msh9_tipo}` y `{msh9_evento}` | ningún adaptador los necesita, y en un contenedor por grupo no se pueden calcular sin leer el mensaje desde el shell |
| DV-VC-6 | Las categorías van por corpus (`adt`, `oru`, `muestras`, `propio`), como `RESULTADO-CV2.json`; los mínimos solo cuentan en su sección | así se comparan con el estudio, y una sonda no es parte del corpus |
| DV-VC-7 | En el proceso local (solo el juguete), `python3` es el intérprete que corre la herramienta, y el contenedor por grupo es un bucle en Python con el mismo registro por mensaje | las pruebas no dependen de `sh` |
| DV-VC-8 | `--solo-orden` no pregunta a Docker | imprime la orden y nada más |
| DV-VC-9 | La herramienta rechaza una carpeta de salida que no esté vacía y no sea de una corrida anterior | no borrar lo que no es suyo |
| DV-VC-10 | `comprobar_informe` avisa y no para | el texto de un hallazgo lleva valores del mensaje, que pueden contener cualquier palabra |
| DV-VC-11 | El contenedor se llama `vc-<id>-<pid>-<n>` | dos corridas a la vez no chocan por el nombre |
| DV-VC-12 | Tras la revisión a ciegas: la imagen se valida con la gramática de Docker (`imagen_formato`) y va tras `--`; cada opción lleva su ayuda; una carpeta de salida ocupada sale con 2 | una «imagen» que empezara por `-` era una bandera de Docker. Hoy no se explotaba, porque `docker image inspect` fallaba antes, pero la garantía no puede depender de eso |

## Lo que no hace

Los límites L-VC-1..15 están en `verificar_conversor.py` y en cada informe. Los que más pesan:
- **No sabe si el proyecto ya tenía declarada una discrepancia** (L-VC-1).
- **Solo programas de línea de órdenes en Docker** que lean y escriban ficheros: ni servicios HTTP, ni bibliotecas, ni
  conversores que necesiten red (L-VC-3).
- **No descarga nada:** la imagen tiene que estar ya en la máquina (L-VC-4).
- **Solo ADT de los ocho eventos y ORU^R01**; lo demás sale como fuera de alcance (L-VC-2).
- **Las muestras de los proyectos no viajan con el repositorio** (L-VC-7).

## En cada cambio, en GitHub Actions

Para correr esta herramienta en cada cambio de un proyecto, con una línea base que separa lo que el proyecto ya conoce de lo
que acaba de aparecer, está el flujo reutilizable de la etapa 23: [`ci/CI.md`](ci/CI.md).

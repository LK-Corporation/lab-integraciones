# Resultado de la etapa 22: las nueve de VXU en las ramas principales

**De las 9 nuevas de VXU, siguen 9 en la rama principal de su conversor (Microsoft 6 de 6, LinuxForHealth 3 de 3); el arrastre de
estado sigue en `master`.**

Ninguna de las nueve estaba reportada en su proyecto al mirarlo el 25-oct; dos tienen un PR fusionado relacionado, que trata el
mismo campo desde otro lado. Los borradores de issues y el comentario al issue abierto del arrastre quedan preparados para que el
autor decida si los abre. No se publican.

La pregunta, fijada antes de medir en [`ANTES-ETAPA-RAMAS-VXU.md`](ANTES-ETAPA-RAMAS-VXU.md):

> ¿Siguen en la rama principal de cada conversor las nueve discrepancias nuevas de VXU y el arrastre de estado de LinuxForHealth?
> Y, para las que sigan, ¿quedan listos los borradores de issues, contrastados con lo que cada proyecto tiene abierto hoy?

## Las ramas

| Conversor | Rama y commit | Avanzó desde el 24-oct | Construcción | Huella |
|---|---|---|---|---|
| Microsoft FHIR-Converter | `main`, `70fd328` (3-jun-2026) | no | la de `cv/RESULTADO-15A.md` | `38c6d32bb662` |
| LinuxForHealth hl7v2-fhir-converter | `master`, `2cb72c2` (11-feb-2026) | no | la de `cv/RESULTADO-15A.md` | `28c1606701d9` |

**Ninguna rama avanzó**, así que no hubo que reconstruir nada: se midió con las construcciones del 24-oct. Las huellas son las de
15A. **Los adaptadores de rama** están en `cv/adaptadores/`: `microsoft-main.json`, `linuxforhealth-main.json` y
`linuxforhealth-main-mensaje.json`.

## Las nueve

| Id | Conversor | Discrepancia | Par | Fuerza | En la rama | En el proyecto |
|---|---|---|---|---|---|---|
| VX-M15 | Microsoft | RE o NA sin RXA-18 salen `completed` | VM15 | fuerte | **sigue** | no reportada |
| VX-M14 | Microsoft | RXA-6 «.5» se escribe 5 | VM14 | fuerte | **sigue** | no reportada |
| VX-M7 | Microsoft | RXA-15 repetido se concatena en un lote que no existe | VM07 | fuerte | **sigue** | no reportada |
| VX-M10 | Microsoft | NK1-3 GRD sin código | VM10 | fuerte | **sigue** | no reportada |
| VX-M8 | Microsoft | el nombre del fabricante une CE.2 y CE.5 | VM08 | débil | **sigue** | no reportada |
| VX-M12 | Microsoft | de dos RXA-19 llega una | VM12 | débil | **sigue** | no reportada |
| VX-L6 | LinuxForHealth | RXA-21 D sale `completed` | VL04 | fuerte | **sigue** | relacionada: #343, PR fusionado en 2021 (`Immunization.status` desde ORC-5) |
| VX-L8 | LinuxForHealth | de dos RXA-10 llega el primero | VL06 | débil | **sigue** | no reportada |
| VX-L9 | LinuxForHealth | de dos RXA-19 llega una | VL07 | débil | **sigue** | relacionada: #380, PR fusionado en 2022 (un solo `reasonCode`, en MedicationRequest) |

**VX-L9 es la más débil como «no reportada».** El #380 eligió a propósito un solo `reasonCode` para MedicationRequest, y en
`master` la plantilla de Immunization lee `reasonCode` de RXA-19 de una sola vez, sin `generateList`, que da lo mismo
(`src/main/resources/hl7/resource/Immunization.yml`, entrada `reasonCode`, en el commit `2cb72c2` del proyecto). El proyecto no lo
declara para Immunization, donde la guía pide las repeticiones (`RXA_Immunization.csv:24`, 0..*). Los dos PR relacionados se
fusionaron antes de v1.1.0, así que las dos versiones juzgadas los llevan. Las fechas de fusión (18-nov-2021 y 5-ene-2022) y la de
v1.1.0 (23-oct-2023) se leyeron a mano en GitHub el 25-oct; el aparato no las registra.

**«Sigue»** quiere decir que, en la rama, el juez confirma el par: el caso da el hallazgo, con su hecho, subtipo y texto, y el
control no (`cv/cv3_minimos_vxu.py`).

**En los 26, la rama da exactamente lo mismo que la versión fijada,** con el texto del juez incluido: las nueve, y las otras 17
(16 pares ya declarados o de convención, y la secuencia).
- **Por eso los tres ficheros de juicios son idénticos byte a byte:** `RESULTADO-RV-minimos-fijada-lote.json`, `-fijada-mensaje` y
  `-main`. `cv3_minimos_vxu.juzgar` no escribe nada propio de cada corrida.
- **Que son corridas distintas lo dice `vx/rv/CORRIDAS-RV.json`:** el conversor, la huella, la imagen con su digest, la fecha, los
  mensajes y la duración de cada una.

**LinuxForHealth se decidió mensaje a mensaje,** un proceso Java por mensaje, para que el arrastre no contaminara unos pares con
otros. En la rama no se corrieron los pares en lote (Q-RV-D-5, Jev).

## El control, antes de mirar las ramas

- **Los pares corridos hoy con las versiones fijadas,** Microsoft v7.0 y LinuxForHealth v1.1.0, dan exactamente lo de la etapa 20
  (`vx/RESULTADO-VX3-minimos.json`). Son los 26: 25 pares y la secuencia, con 0 diferencias de veredicto y 0 de texto. Solo cambia
  la huella del juez, `11a3754fb8b6` entonces y `bde94016ca58` hoy, y entre las dos solo difieren textos.
- **Con LinuxForHealth v1.1.0, los 50 mensajes de los pares dan los mismos veredictos en lote y mensaje a mensaje.** Los pares de
  la etapa 20, que se corrieron en lote, no estaban contaminados por el arrastre.
- **La secuencia VL11 sale con la versión fijada:** en lote, el segundo mensaje pierde el fabricante y, mensaje a mensaje, no.

## La secuencia del arrastre en `master`

**Sigue, en las dos repeticiones.** Convertidos en el mismo proceso, tras un VXU con RXA-17 de solo texto el siguiente sale sin
`manufacturer` y sin la Organization. Mensaje a mensaje sale con ella. Lo ve también el nivel del Bundle, que solo se usa para
comprobar el positivo. El issue abierto del proyecto, #348, describe grupos ORC/RXA repetidos dentro de un mensaje y un arreglo
provisional que no cubre un RXA-17 de solo texto. El borrador es un comentario a ese issue.

## El contraste con los proyectos

Se leyeron el 25-oct todos los issues y PR de los dos proyectos, abiertos y cerrados, con sus comentarios: 587 de Microsoft y 533
de LinuxForHealth, con 879 comentarios.
- **Candidatos:** se buscó, por cada discrepancia, al menos un término del campo y uno del efecto.
- **La decisión,** a mano: qué cuenta como «ya reportada» (el mismo campo y el mismo efecto) y qué como «relacionada» (el mismo
  campo, otro efecto u otra fuente).
- **Dónde está:** en `vx/rv/CONTRASTE-RV.json`, con el título, el estado y los términos de cada candidato, y la cita y la nota
  de cada decisión.

## La previsión sellada, frente a lo que salió

Se selló antes de cualquier corrida con Docker de la etapa y antes de consultar GitHub (`vx/rv/PREVISION-RV.json`,
`vx/rv/SELLO-RV.txt`). Hay dos previsiones, cada una con su autor:
- la del programador, que escribió el código;
- la de Jev, el modelo de decisión al que el laboratorio pasa las preguntas de diseño con un estado neutro y que contesta con
  probabilidades (`../piloto-agente/README.md`).

**`SELLO-RV.txt` ya no verifica `ramas_vxu.py`,** que cambió después en la redacción de los borradores (DV-RV-2 y DV-RV-8); lo
demás del sello cuadra, incluidos los dos ficheros que producen los juicios. `PREVISION-RV.md` fecha «ayer» el contraste de la
etapa 20, que fue el mismo día (DV-RV-6).

| Qué | Programador | Jev | Salió |
|---|---|---|---|
| Siguen las nueve | 0,73 | 0,41 (siete u ocho, 0,59) | sí |
| El arrastre sigue en `master` | 0,9 | 1,0 | sí |
| Alguna ya reportada | ~0,2 en conjunto | 0,02 | ninguna (dos relacionadas) |
| El control reproduce la etapa 20 | 0,88 | — | sí |
| Lote y mensaje a mensaje iguales con v1.1.0 | 0,93 | — | sí |
| Alguna rama avanzó | 0,05 y 0,02 | — | no |

## Límites

- **«Sigue» vale para el par mínimo.** Una corrección que solo cubra otras entradas, o un fallo que solo salga con otras, no se ve
  (L-RV-1).
- **La rama es la del commit anotado el 25-oct.** Un commit posterior puede cambiarlo (L-RV-2).
- **Los artefactos de las ramas son privados.** Lo público son sus huellas, el commit y la receta de `cv/RESULTADO-15A.md`
  (L-RV-3).
- **El contraste depende de unos términos y de una lectura humana.** Un issue escrito con otras palabras puede escaparse (L-RV-4).
- **VL11 prueba un solo disparador del arrastre** y un solo síntoma (L-RV-5).
- **El juez de hoy no es byte a byte el de la etapa 20** (`bde94016` frente a `11a3754f`). La igualdad de veredictos se apoya en
  el control de los 26 y en que entre los dos solo difieren textos, no en una comparación del código (L-RV-6).
- **La huella de una rama identifica la construcción, no el commit.** Dos construcciones del mismo commit pueden dar huellas
  distintas (L-RV-7). Las identidades anotan las huellas de las ramas, que aquí son las de 15A; el código no lo exige.
- **La imagen de Microsoft va por etiqueta** (`runtime:8.0`). Su digest se registra en `RAMAS-RV.json` y en `CORRIDAS-RV.json`,
  pero no se exige (L-RV-9).
- **El camino «corregida» no se ejercitó con conversiones reales** en este aparato, solo con juicios fabricados en sus pruebas:
  aquí no salió ninguna.
- **El contraste lee los issues, los PR y sus comentarios,** no los comentarios de revisión de los PR ni los mensajes de commit.
- **Las otras 17 solo se anotan:** ni se contrastan ni llevan borrador (L-RV-12).

## Cómo repetir

Desde `verificador/`, con los artefactos del estudio (`ms/`, `lfh/`, `ms-main/`, `lfh-main/`; ver `cv/CV1.md` y
`cv/RESULTADO-15A.md`):

1. **Las pruebas,** sin Docker: `python3 vx/rv/prueba_rv.py`.
2. **Una previsión propia,** sellada en otra carpeta con `vx/rv/sellar_prevision_rv.py <cuerpo> <carpeta>`, y su commit. El
   sello publicado ya no verifica `ramas_vxu.py`.
3. **Las identidades y el control** (pasos 3 y 5), **las ramas al día** (con red) y **las corridas de las ramas y el estado**
   (pasos 7 y 8):

```bash
python3 vx/rv/ramas_vxu.py correr <artefactos> <salida> --desde 3 --hasta 5 --sello <carpeta>
gh api "repos/microsoft/FHIR-Converter/compare/70fd328...main" > compare-ms.json
gh api "repos/LinuxForHealth/hl7v2-fhir-converter/compare/2cb72c2...master" > compare-lfh.json
python3 vx/rv/ramas_vxu.py ramas compare-ms.json compare-lfh.json <salida>/RAMAS-RV.json
python3 vx/rv/ramas_vxu.py correr <artefactos> <salida> --desde 7 --hasta 8 --sello <carpeta>
python3 vx/rv/completar_ramas.py compare-ms.json compare-lfh.json <salida>/RAMAS-RV.json <artefactos> <salida>
```

4. **El contraste,** con los issues y comentarios de cada proyecto descargados con `gh api` (§6 del diseño):
   `ramas_vxu.py contraste <proyectos> <salida>/ESTADO-RV.json <salida>/CONTRASTE-RV.json`. Después vienen las decisiones a mano
   (aquí, `vx/rv/decidir_contraste.py`) y `contraste … --comprobar`.
5. **Los borradores y el resultado:** `ramas_vxu.py borradores <salida> <fichero>` y `ramas_vxu.py resultado <salida> <fichero>`.
   Este documento amplía el que escribe el segundo (DV-RV-5).

**El aparato:** el diseño a ciegas de Fable está en `vx/rv/diseno-rv-fable.md` y su encargo en `vx/rv/ENCARGO-RV0.md`. Las
decisiones de Jev y las desviaciones del programador están en `vx/rv/decisiones-qrv.md`.

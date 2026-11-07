# RESULTADO de la etapa 35: cerrar el círculo del ensayo (7-nov-2026)

> **Después del push, la comprobación dice si el árbol publicado es el ensayado: cae cuando no lo es y pasa cuando lo es.**
>
> - [`cv/ci/comprobar_publicado.py`](cv/ci/comprobar_publicado.py) lee del remoto el commit publicado, saca su árbol y lo compara
>   con el que dice cada `ENSAYO.json`.
> - En un remoto de prueba, con los tres flujos ensayados una vez:
>   - el push tal cual pasa;
>   - un `git add` de más y un `commit --amend` después del ensayo caen, con la ruta exacta, en los tres flujos.
> - Con un remoto local, cada comprobación tarda unas centésimas de segundo. Contra GitHub, solo leer el remoto (`git ls-remote`)
>   tarda de 0,44 a 0,50 s, en cinco medidas ([`cr/COSTE-CR.txt`](cr/COSTE-CR.txt)).
> - Veintinueve mutantes de la comprobación, cada uno con una cosa que tiene que hacer rota a propósito, hacen caer alguna prueba.
>   Entre ellos están los que leen el clon en vez del remoto.

La pregunta, fijada antes de diseñar, está en [`ANTES-ETAPA-CIRCULO.md`](ANTES-ETAPA-CIRCULO.md).

## Cómo se hizo

| | |
|---|---|
| El porqué | En la etapa 34, la demo se ensayó sobre el árbol que se publicó, y el ejemplo y el rojo sobre uno anterior, que difería en textos. Nada lo comprobó antes del push |
| El diseño | Fable, a ciegas de los resultados ([`cr/diseno-cr-fable.md`](cr/diseno-cr-fable.md); encargo en [`cr/encargo-diseno-cr.md`](cr/encargo-diseno-cr.md)) |
| Las decisiones | Jev, siete (`Q-CR-1` a `7`): [`cr/decision-jev-cr.md`](cr/decision-jev-cr.md); `Q-CR-2` y `5` otra vez por su confianza baja ([`cr/decision-jev-cr2.md`](cr/decision-jev-cr2.md)); y `Q-CR-5` una tercera vez, sin la frase que la inclinaba ([`cr/decision-jev-cr3.md`](cr/decision-jev-cr3.md)). Sus estados: [`cr/estado_cr.md`](cr/estado_cr.md) y [`cr/estado_cr3.md`](cr/estado_cr3.md) |
| Las pruebas, en rojo antes | `P-CR-1` a `15`, en [`cv/ci/prueba_ci.py`](cv/ci/prueba_ci.py). Las doce primeras caían antes de escribir la comprobación ([`cr/ROJO-CR.txt`](cr/ROJO-CR.txt)); las de después de la revisión, en [`cr/ROJO-CR-2.txt`](cr/ROJO-CR-2.txt) y [`cr/ROJO-CR-3.txt`](cr/ROJO-CR-3.txt); y todas, frente a veintinueve mutantes, en [`cr/MUTANTES-CR.txt`](cr/MUTANTES-CR.txt) |
| La previsión | Sellada antes de correr los controles: [`cr/PREVISION-CR.json`](cr/PREVISION-CR.json), con las huellas de la comprobación, las pruebas y el guion de los controles. Las versiones selladas que cambiaron después, en [`cr/sellada/`](cr/sellada/) |
| Los controles | [`cr/controles_cr.sh`](cr/controles_cr.sh), sobre un remoto de prueba local, y [`cr/ensamblar_controles_cr.py`](cr/ensamblar_controles_cr.py), que junta lo que dejan: [`cr/CONTROLES-CR.json`](cr/CONTROLES-CR.json) y [`cr/CODIGOS-CR.txt`](cr/CODIGOS-CR.txt); con la versión final, [`cr/CONTROLES-CR-2.json`](cr/CONTROLES-CR-2.json) y [`cr/CODIGOS-CR-2.txt`](cr/CODIGOS-CR-2.txt) |

## Lo que hace la comprobación

```bash
python3 cv/ci/comprobar_publicado.py <clon> <ENSAYO.json de la demo> <del ejemplo> <del rojo> [--rama main] [-o <carpeta>]
```

- **Qué compara:** lee con `git ls-remote` el commit que el remoto tiene en la rama (solo lectura; si falta en el clon, lo trae con
  `fetch`), saca su árbol y lo compara con `clon.arbol` de cada `ENSAYO.json`. Compara árboles, no commits.
- **Cuándo pasa (0):** si los tres flujos (`demo-ci`, `ejemplo-ci` y `rojo-ci`; `Q-CR-2`) tienen un ensayo de sus jobs mínimos
  (`Q-CR-7`) sobre el árbol publicado.
- **Cuándo cae (1):** si falta un ensayo, si no ensayó nada o no dice su árbol, si le falta un job, o si ensayó otro árbol.
  - **Un árbol distinto** cae siempre (`Q-CR-3`), con la orden para re-ensayar.
  - **Las rutas que difieren** se listan si el árbol ensayado sigue en el clon; si no, lo dice.
- **Sale con 2** si no pudo comprobar:
  - el remoto o la rama no se leen;
  - un `ENSAYO.json` no es válido;
  - hay dos ensayos del mismo flujo;
  - no hay flujos que comprobar;
  - los argumentos están mal;
  - o un fichero no se lee o no se escribe.
- **Avisa, sin cambiar el código:**
  - un ensayo en rojo sobre el árbol publicado (`Q-CR-4`);
  - commits intermedios, que GitHub no corre;
  - otra historia sobre el mismo árbol, como un amend que solo cambia el mensaje;
  - con `--base`, un commit de fusión de un PR con otro árbol (lo prevé `git merge-tree`).
- **Dónde corre:** es una orden local, después del push (`Q-CR-1` y `Q-CR-5`). Los flujos de GitHub no cambian. Deja lo
  comparado en `PUBLICADO.json`.
- **La guía,** [`cv/ci/CI.md`](cv/ci/CI.md), lleva una sección nueva: «Después del push: la comprobación».

Jev decidió como recomendaba el diseño salvo en dos puntos:
- **Un ensayo en rojo sobre el árbol publicado avisa y no cae** (`Q-CR-4`: peso 0,69, confianza 0,38).
- **No hay modo `--local` antes del push** (`Q-CR-5`), que el diseño proponía como opción de más.
  - Las dos primeras veces (confianza 0,12 y 0,18), el estado decía en la opción (a) «como fija el ANTES». El ANTES pregunta por
    la comprobación de después, pero no dice nada de antes. La revisión a ciegas lo señaló.
  - Se preguntó una tercera vez sin esa frase (`cr/estado_cr3.md`), y Jev decidió lo mismo: 0,95, con confianza 0,90.
  - **Ese estado tampoco era neutral,** como señaló la segunda pasada de la revisión. Le contaba a Jev sus dos respuestas
    anteriores, y sus hechos pesaban del lado de (a): que lo mismo se hace con un remoto de prueba, y el tope de una sesión. No se
    preguntó una cuarta vez.

## Las pruebas

Las quince montan repositorios de git mínimos con un remoto vacío al lado, sin Docker ni red, y corren en el trabajo `pruebas` de
la demo.

| Prueba | Qué monta | Con la comprobación |
|---|---|---|
| P-CR-1 | El ensayo del HEAD, y push | 0: «es el mismo commit» |
| P-CR-2 | El ensayo del índice, commit y push | 0: «el commit es nuevo sobre él» |
| P-CR-3 | Un `git add` de más después del ensayo | 1, con `A OTRO` |
| P-CR-4 | Un `commit --amend` con cambio después del ensayo del HEAD | 1, con `M MARCA` y «el commit ensayado … ya no está en main» |
| P-CR-5 | Un amend que solo cambia el mensaje | 0: el mismo árbol |
| P-CR-6 | Ningún ensayo, una ruta que no existe, un ensayo sin `clon`, uno sin `.git`, uno que no ensayó; un fichero que no es JSON | 1 en los cinco primeros, 2 en el último |
| P-CR-7 | Otra copia: con otro contenido, y con el mismo | 1 («no está en este clon»); 0 |
| P-CR-8 | Dos flujos sobre árboles distintos | 1, solo por el del árbol viejo, con su ruta |
| P-CR-9 | Varios commits: la cabeza es lo ensayado, y no lo es | 0 con aviso de 2 commits; 1 |
| P-CR-10 | Un PR, con `--base main`, antes y después de que `main` avance | 0, la fusión con el mismo árbol; 0 con aviso |
| P-CR-11 | Un remoto que no se lee y una rama que no está | 2 |
| P-CR-12 | Un ensayo en rojo, y un job que falta de la lista mínima | 0 con aviso; 1 |
| P-CR-13 | Sin push: el remoto sigue en el commit de antes | 1, con la ruta, y «el clon está en otro commit» |
| P-CR-14 | El remoto avanzó desde otro clon | 1, con la ruta: trae el commit y lee el remoto, no el clon |
| P-CR-15 | `ENSAYO.json` con tipos raros, argumentos mal puestos, ningún flujo, dos ensayos del mismo flujo, `-o` sobre un fichero, un `ENSAYO.json` que no se lee | 2 |

P-CR-13 a 15 llegaron con la revisión a ciegas, junto con tres comprobaciones más:
- en P-CR-2, que un solo commit no da el aviso de commits intermedios;
- en P-CR-5, el aviso de otra historia;
- en P-CR-10, una fusión con conflictos.

La segunda pasada añadió a P-CR-15 dos casos más: `-o` sobre un fichero y un `ENSAYO.json` que no se lee. Su rojo está en
[`cr/ROJO-CR-3.txt`](cr/ROJO-CR-3.txt).

**Los mutantes** ([`cr/mutantes_cr.py`](cr/mutantes_cr.py), [`cr/MUTANTES-CR.txt`](cr/MUTANTES-CR.txt)) son veintinueve copias
rotas a propósito de la comprobación:
- dieciséis de la etapa;
- doce que probó la segunda pasada de la revisión a ciegas, con el mismo arnés (M17 a M28);
- uno más para los ficheros (M29).

Cada una cambia una cosa:
- compara mal los árboles, no lista las rutas o las lista al revés;
- lee el HEAD del clon, o su rama de seguimiento, en vez del remoto, no hace `fetch` o ignora `--remoto`;
- calla un aviso, o se equivoca con la fusión;
- deja pasar un flujo sin ensayo, sin jobs, raro, repetido o vacío, o con otro árbol;
- sale con 0 teniendo el círculo abierto, o no captura los errores.

Con cada una cae alguna P-CR, y con la comprobación sin tocar, ninguna. Los que leen el clon los cazan P-CR-13 y 14: antes de la
revisión no había prueba que los distinguiera.

En el repositorio publicado (`cd verificador && python3 cv/ci/prueba_ci.py`):
- **Antes de la comprobación:** las doce primeras caían con una excepción, porque el guion no existía. Las 41 de antes, en verde,
  con 198 comprobaciones.
- **Con la primera versión:** TODO BIEN, 234 comprobaciones en 53 pruebas.
- **Las de la revisión, con la comprobación de antes del arreglo:** P-CR-15 caía con una traza. Las otras miraban lo que ya hacía
  bien, y su rojo está en los mutantes.
- **Con la versión final:** TODO BIEN, 251 comprobaciones en 56 pruebas. En el laboratorio son 244, por lo mismo que en la etapa
  34: P-CI-26 y 27 comprueban más cuando están los flujos de `.github/`.

## Los controles

En un remoto de prueba hecho a partir del clon del público en `464bbb2`, nunca en el público:
- una copia con una línea añadida a `verificador/cv/ci/CI.md`, en el índice;
- los tres flujos ensayados una vez sobre ese índice (árbol `f07968687b3f`);
- tres pushes al remoto de prueba, cada uno comprobado con los mismos tres `ENSAYO.json`.

| Control | Qué se publicó | Código | Lo que dijo, en los tres flujos | Segundos |
|---|---|---|---|---|
| Negativo | El índice ensayado, tal cual | 0 | «el mismo árbol; el commit es nuevo sobre él» | 0,03 |
| Positivo: `git add` de más | Además, `verificador/DE-MAS-35.txt` | 1 | «OTRO ÁRBOL: 1 ruta difiere (A verificador/DE-MAS-35.txt)» | 0,04 |
| Positivo: `commit --amend` | Otra línea en `verificador/cv/ci/CI.md`, con amend | 1 | «OTRO ÁRBOL: 1 ruta difiere (M verificador/cv/ci/CI.md)» | 0,05 |

**La segunda tanda,** con la versión final (DV-CR-3), dio lo mismo: los mismos códigos, las mismas rutas y casi los mismos
segundos (0,04 a 0,05). Desde ella, el guion guarda las huellas de la comprobación y del ensayo que corre, y son las de lo que se
publica.

**El caso real,** el push de esta etapa, se comprueba después de publicarla, con los tres ensayos de ese push. Su registro y su
resultado van en un segundo push, en `cr/PUBLICADO-PUSH.json` (`Q-CR-6`).

**Lo que no cambia** (las condiciones 1 y 5 del ANTES):
- **El juez, la herramienta, las bases y los flujos no cambian.** Fuera de la documentación de la etapa, el push solo añade
  `cv/ci/comprobar_publicado.py` y toca `cv/ci/prueba_ci.py`, `cv/ci/CI.md`, el README, la higiene y el manifiesto.
- **En el ensayo de este push,** la demo, el ejemplo y el rojo dan lo mismo que antes:
  - el negativo pasa sin nuevos;
  - el positivo cae solo por PID-7, en 344 casos;
  - el ejemplo pasa con sus dos bases;
  - el rojo cae solo por su defecto, en 164 casos.

## La previsión

| | Jev | El diseñador | Lo que pasó |
|---|---|---|---|
| Los controles, a la primera | Alta, 0,9 o más (confianza 0,88) | 0,95 | Sí |
| El push de la etapa pasa la comprobación a la primera | Media, de 0,6 a 0,9 (confianza 0,94) | 0,8 | En el segundo push |

## Las desviaciones del diseño (DV-CR-n)

- **DV-CR-1:** el fichero de más del control positivo es `verificador/DE-MAS-35.txt` y no `verificador/cr/DE-MAS.txt`, porque
  `verificador/cr/` no existe aún en el commit de partida.
- **DV-CR-2:** las pruebas del diseño eran trece, y salieron doce.
  - La de `--local` (`P-CR-11` del diseño) no se escribió, porque Jev no quiso ese modo.
  - Las `P-CR-12` y `13` del diseño son aquí la 11 y la 12.
  - La del ensayo en rojo espera un aviso y no una caída, como decidió Jev en `Q-CR-4`.
- **DV-CR-3, tras la revisión a ciegas:**
  - una lista de flujos vacía, un `ENSAYO.json` con tipos raros o unos argumentos mal puestos salen con 2, y no con un verde sin
    comparar nada o con una traza y 1 ([`cr/parche_comprobar_cr.py`](cr/parche_comprobar_cr.py));
  - tras la segunda pasada, también un fichero que no se lee o no se escribe
    ([`cr/parche_comprobar_cr2.py`](cr/parche_comprobar_cr2.py));
  - tres pruebas más y dos casos más en P-CR-15 ([`cr/parche_prueba_cr2.py`](cr/parche_prueba_cr2.py) y
    [`cr/parche_prueba_cr3.py`](cr/parche_prueba_cr3.py));
  - los controles se repitieron con la versión final.
- **DV-CR-7:** el guion de los controles guarda, desde la segunda tanda, las huellas de lo que corre. Su versión sellada está en
  [`cr/sellada/`](cr/sellada/).
- **DV-CR-4:** `CONTROLES-CR.json` no lo escribe el guion de los controles, como decía el diseño, sino
  [`cr/ensamblar_controles_cr.py`](cr/ensamblar_controles_cr.py), a partir de lo que el guion deja. Reproduce el de la primera
  tanda byte a byte.
- **DV-CR-5:** el guion de los controles toma cuatro argumentos (el clon, la comprobación, el ensayo y la carpeta), no dos.
- **DV-CR-6:** `PUBLICADO.json` no es exactamente el del diseño.
  - No lleva `local` ni `verde`, porque no hay modo `--local` y el rojo solo avisa.
  - Lleva `rojo`, `faltan`, `amend` y `avisos`, y `commits_nuevos` va por flujo.
  - Que el clon esté en otro commit que el remoto va en la cabecera, no como aviso.

## Lo que la comprobación no ve

- Si los `ENSAYO.json` que se le dan son los últimos. Compara contenido: un ensayo viejo sobre el mismo árbol es un ensayo válido
  de ese árbol.
- Si un `ENSAYO.json` se editó a mano. Es una guarda contra el descuido, no contra la mala fe.
- El commit de fusión real de un PR. `merge-tree` lo prevé con el `main` del momento.
- Un push posterior a la comprobación. Hay que volver a correrla, porque no vigila.
- Lo que pasa en el runner, y lo que el ensayo mismo no emula.
- Si el `ensayo_flujo.py` que ensayó es el publicado.

## Cómo se repite

Desde `verificador/`:
- `python3 cv/ci/prueba_ci.py` corre las pruebas, también las `P-CR`.
- `bash cr/controles_cr.sh <clon limpio del público> cv/ci/comprobar_publicado.py cv/ci/ensayo_flujo.py <carpeta vacía fuera del
  clon>` corre los controles. Necesita el Docker de la máquina para los ensayos, y escribe `res/` con las salidas, `CODIGOS.txt`
  y los `PUBLICADO.json`.
- `python3 cr/ensamblar_controles_cr.py <esa carpeta> <salida.json> [segunda]` junta lo comparado. Con `segunda`, el texto de la
  segunda tanda.
- `python3 cr/mutantes_cr.py <verificador/ de una exportación>` corre los mutantes.

## Ficheros

- **La comprobación, sus pruebas y la guía:** [`cv/ci/comprobar_publicado.py`](cv/ci/comprobar_publicado.py),
  [`cv/ci/prueba_ci.py`](cv/ci/prueba_ci.py) y [`cv/ci/CI.md`](cv/ci/CI.md).
- **Los parches,** cada uno con su comprobación de texto: [`cr/parche_prueba_cr.py`](cr/parche_prueba_cr.py) y
  [`cr/parche_guia_cr.py`](cr/parche_guia_cr.py); tras la revisión, [`cr/parche_comprobar_cr.py`](cr/parche_comprobar_cr.py),
  [`cr/parche_prueba_cr2.py`](cr/parche_prueba_cr2.py) y [`cr/parche_guia_cr2.py`](cr/parche_guia_cr2.py); y tras su segunda
  pasada, [`cr/parche_comprobar_cr2.py`](cr/parche_comprobar_cr2.py), [`cr/parche_prueba_cr3.py`](cr/parche_prueba_cr3.py) y
  [`cr/parche_guia_cr3.py`](cr/parche_guia_cr3.py). Aplicados en ese orden sobre lo de `464bbb2` y la comprobación sellada, dan
  lo publicado.
- **El diseño, las decisiones, la previsión y los controles,** en [`cr/`](cr/).

# La previsión de la etapa 25, sellada antes del primer push

Se escribió y se selló antes del primer push de la etapa, antes de que GitHub corra las acciones nuevas. Las cifras exactas
están en `PREVISION-MANT.json`; su huella y la del aparato, en `SELLO-MANT.txt`.

| | Programador | Jev |
|---|---|---|
| La demo en verde en el primer push | 0,9 | 0,84 |
| Con los mismos informes | 0,97 | — |
| El ejemplo en verde a la primera tras subir su pin | 0,85 | 0,87 |
| El rojo como se espera a la primera | 0,85 | — |
| Sin el aviso de Node.js 20 donde debe desaparecer | 0,85 | 0,75 |
| Las corridas del PR en verde a la primera | 0,8 | 0,74 |
| Todo en una sesión | 0,7 | — |
| Pushes | de 4 a 6; lo más probable, 4 | cuatro o menos, 0,98 |
| Casos con el hallazgo del rojo | 164 | — |

**Lo más probable que falle,** por orden:
1. una acción nueva que no carga o cambia algo en el runner, porque el ensayo no corre su código;
2. setup-python v6 sin Python 3.12 en Ubuntu 26;
3. download-artifact v7 bajando lo que subió la versión anterior de upload-artifact, en el primer push, cuando el ejemplo aún
   llama al flujo viejo;
4. el patrón del aviso, que deja de casar con el texto de GitHub;
5. el commit del primer push mal copiado en el segundo;
6. la higiene.

Las cifras del programador se fijaron antes de leer la respuesta de Jev (`estado_prevision_mant.md`,
`decision-jev-prevision-mant.md`) y no se cambiaron.

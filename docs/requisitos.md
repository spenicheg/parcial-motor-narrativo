# Requisitos — Motor de ficción interactiva

Vocabulario común (usado igual en requisitos, diagramas y código):
**historia**, **escena**, **opción**, **condición**, **efecto**, **variable**, **sesión/partida**, **final**, **bloqueo**, **problema de contenido**.

## 1. Requisitos funcionales

Cada RF es atómico, observable y tiene criterio de aceptación (CA) verificable. La columna «Prueba» indica dónde se verifica.

| ID | Necesidad | Requisito (comportamiento observable) | Criterio de aceptación | Prueba |
|---|---|---|---|---|
| RF01 | N01 | El sistema carga una historia desde un archivo JSON indicado por ruta, sin cambios en el código. | Dado `el_faro.json` y `la_ultima_transmision.json`, ambos se juegan con el mismo motor. | `test_integracion.py::test_I1_*` |
| RF02 | N01 | La partida comienza en la escena indicada por `inicio` con los valores de `variables`. | Partida nueva de La última transmisión: escena E1, `conoce_origen=false`, `confia_en_la_voz=false`. | `test_motor.py::test_U5_*`, `test_U2_CA01_*` |
| RF03 | N02 | El sistema muestra el texto de la escena actual. | Al iniciar se imprime el texto de E1. | `test_integracion.py::test_I1_interfaz_*` |
| RF04 | N02 | Solo se muestran las opciones cuyas condiciones se cumplen todas (mapa vacío = siempre visible). | En E3 con `conoce_origen=true` se ven exactamente `activar_codigo` y `cortar`; con `false`, `activar_sin_verificar` y `cortar`. | `test_U1_*` (CA01) |
| RF05 | N03 | Al elegir una opción habilitada se aplican sus efectos y la sesión pasa a su destino. | `investigar` en E2 → E3 con `conoce_origen=true`. | `test_U2_*` |
| RF06 | N03 | Una opción inexistente, no habilitada o una entrada inválida se rechaza con mensaje y sin cambiar escena, variables ni recorrido. | Enviar `activar_codigo` en E3 sin conocer el origen → rechazo, sigue en E3. | `test_U3_*`, `test_CA02_*`, RNF03 |
| RF07 | N04 | La sesión conserva las variables y el recorrido de escenas durante toda la partida. | Ruta `revisar→investigar→activar_codigo` deja `recorrido=[E1,E2,E3,E4]` y la decisión de E2 condiciona E3. | `test_U2_*`, `test_RNF01_agregar_*` |
| RF08 | N05 | Al llegar a una escena final se anuncia el desenlace y no se aceptan más elecciones. | En E4/E5/E6 se muestra «FINAL ALCANZADO (id)» y `elegir` devuelve rechazo. | `test_U3_no_se_puede_elegir_en_un_final`, `test_I1_*` |
| RF09 | N05 | El lector puede reiniciar en cualquier momento; la nueva partida no conserva nada de la anterior. | Tras E4 + reiniciar: E1, variables iniciales, recorrido `[E1]`. | `test_U5_*` |
| RF10 | N06 | Antes de jugar, el sistema valida el archivo y lo rechaza si tiene algún problema de contenido de la lista mínima (ver §3). No se abre sesión. | Copia con destino E99 → rechazo, no hay historia ni sesión. | `test_U4_*`, `test_CA03_*` |
| RF11 | N06 | Cada problema se informa con código, ubicación (escena/opción/campo) y causa; se informan todos los problemas en una sola validación. | Ver RNF02. | `test_RNF02_*` |
| RF12 | N06 | El comando `validar` revisa una historia sin jugarla (código de salida 0 válida / 2 inválida). | `python -m motor_narrativo validar …` | `test_I1_comando_validar_*` |
| RF13 | N03/N06 | Si en una escena no final ninguna opción está habilitada, se informa el bloqueo y se permite reiniciar. | Sesión bloqueada → mensaje y `reiniciar()` vuelve a E1. | `test_escena_no_final_sin_opciones_habilitadas_*` |

### Requisitos agregados por la solicitud de cambio (hora 6)

| ID | Necesidad | Requisito | Criterio de aceptación | Prueba |
|---|---|---|---|---|
| RF14 | Cambio / N03, N04 | El lector puede deshacer su última elección válida; se restauran exactamente la escena, todas las variables y el recorrido previos a esa elección. | Desde E2, `investigar` → E3 con `conoce_origen=true`; deshacer → E2 con `conoce_origen=false`. | `tests/test_deshacer.py::test_U6_ejemplo_del_anexo` |
| RF15 | Cambio | El retroceso es de un solo nivel: tras deshacer no se puede volver a deshacer hasta una nueva elección válida. No hay rehacer. | Segundo `deshacer()` → rechazo sin cambios; tras `continuar`, `deshacer()` vuelve a funcionar. | `test_U6_un_solo_nivel`, `test_U6_nueva_eleccion_valida_*` |
| RF16 | Cambio / N05 | Al comenzar no hay retroceso disponible; reiniciar elimina el historial. | Sesión nueva o reiniciada → `puede_deshacer=false`, `deshacer()` rechazado. | `test_U6_al_comenzar_*`, `tests/test_motor.py::test_U5_*` |
| RF17 | Cambio / N03 | Una opción inexistente o no habilitada no modifica la sesión ni reemplaza el historial de la última elección válida. | En E3 enviar `activar_codigo` sin conocer origen y luego deshacer → E2 (previo a `continuar`). | `test_U6_entrada_invalida_*` |
| RF18 | Cambio / N05 | Se puede deshacer desde un final (E4, E5, E6): se regresa a E3 con los valores previos a esa elección. | E6 → deshacer → E3, `confia_en_la_voz` con su valor anterior. | `test_U6_deshacer_desde_un_final_*`, `tests/test_integracion.py::test_I1_cargar_recorrer_y_deshacer_*` |
| RF19 | Cambio | La consola ofrece `[d] Deshacer` solo cuando hay retroceso disponible y confirma o rechaza la acción con un mensaje. | Ruta `1,1,2,d,d` muestra «Se deshizo…» y luego «No hay una decisión para deshacer». | `test_I1_consola_deshacer_desde_un_final` |

## 2. Requisitos no funcionales (medibles)

| ID | Atributo | Requisito y métrica | Procedimiento de verificación | Evidencia |
|---|---|---|---|---|
| RNF01 | Modificabilidad del contenido | Agregar una escena, cambiar un destino o cargar otra historia requiere **0 líneas modificadas** en `motor_narrativo/`. El código del motor contiene **0** identificadores de escenas, opciones o variables de historias. | (a) Búsqueda automática de literales de historias en `motor_narrativo/*.py`. (b) Se agrega E2b solo por datos y se recorre. (c) Se juega `el_faro.json`. | `tests/test_rnf.py::test_RNF01_*`, `test_I1_segunda_historia_*` |
| RNF02 | Claridad de errores | **100 %** de los 10 tipos de error obligatorios se reportan **en una sola carga**, cada uno con formato `[CÓDIGO] ubicación: causa`, ubicación no vacía y causa ≥ 15 caracteres. | Se inyecta un error de cada tipo en el mismo archivo y se cuentan los códigos detectados. | `test_RNF02_*` |
| RNF03 | Confiabilidad | **0** excepciones no controladas y **0** cambios de estado tras entradas rechazadas, con 2 000 entradas aleatorias del lector (semilla 2026) y 500 archivos corruptos aleatorios; el ≥ 80 % de las corrupciones se rechaza con `ErrorContenido`. | Pruebas de entrada aleatoria con semilla fija sobre `Sesion`, la consola y el cargador. | `test_RNF03_*`, `resultados/ultima_ejecucion.txt` |

## 3. Errores de contenido obligatorios (RF10)

`ARCHIVO_ILEGIBLE`, `ESTRUCTURA_INVALIDA`, `CAMPO_AUSENTE`, `TIPO_INVALIDO`, `INICIO_INEXISTENTE`, `ESCENA_DUPLICADA`, `OPCION_DUPLICADA` (dentro de su escena), `DESTINO_INEXISTENTE`, `VARIABLE_NO_DECLARADA`, `VALOR_NO_BOOLEANO`, `FINAL_CON_OPCIONES`, `ESCENA_SIN_OPCIONES`. El bloqueo en partida (RF13) no es error de carga: se detecta al jugar.

## 4. Conflicto: retroceso vs. decisiones irreversibles

> **Actualización (hora 6, `v2-con-cambio`):** el cliente resolvió el conflicto: retroceso de **un solo nivel** que revierte todas las consecuencias de la última decisión (RF14–RF19). El texto siguiente se conserva como registro de la v1.

- **Escritora:** quiere poder retroceder siempre. **Diseñador:** quiere decisiones irreversibles.
- **Acuerdo provisional (v1):** no se implementa retroceso; las decisiones son irreversibles dentro de la partida y solo se puede **reiniciar** (RF09).
- **Pregunta de aclaración al cliente:** «¿El retroceso es una ayuda de lectura (deshacer la última elección, con sus efectos) que el autor puede habilitar o bloquear por escena, o debe existir siempre en todas las escenas?»
- **Preparación sin presuponer la respuesta:** la sesión ya guarda `recorrido`; no se guarda historial de variables ni se expone comando de retroceso.

## 5. Preguntas, respuestas y supuestos

| # | Pregunta | Respuesta / supuesto |
|---|---|---|
| P1 | ¿Las condiciones/efectos son obligatorios en cada opción aunque estén vacíos? | **Supuesto:** sí, como en el contrato de referencia (`{}`), para que el archivo sea explícito. |
| P2 | ¿El lector elige por número o por id? | **Supuesto:** la consola muestra números; el motor recibe ids. Así la interfaz no afecta las reglas. |
| P3 | ¿Se valida que todos los finales sean alcanzables? | No: la guía no lo exige. Se detecta el bloqueo durante la partida (RF13). |
| P4 | Retroceso | **Respondida en la solicitud de cambio:** deshacer un nivel, sin rehacer (RF14–RF19). |
| P5 | ¿Se puede deshacer en una escena bloqueada? | **Supuesto:** sí; el anexo no lo prohíbe y es la forma natural de salir del bloqueo sin perder toda la partida. |

## 6. Revisión entre integrantes — defecto encontrado

- **Defecto (ambigüedad):** la primera versión de RF06 decía «las entradas erróneas se ignoran». No era verificable: ¿se informa al lector? ¿qué parte del estado se conserva?
- **Corrección:** RF06 ahora exige mensaje de rechazo **y** que escena, variables y recorrido no cambien, con CA concreto (CA02) y prueba `test_U3_*`.

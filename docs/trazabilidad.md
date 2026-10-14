# Matriz de trazabilidad (v2 — con la solicitud de cambio)

Rutas relativas a la raíz del proyecto. Modelos en `docs/arquitectura.md` (§ = sección).

| Req. | Necesidad | Modelos | Componente / archivo | Evidencia de verificación |
|---|---|---|---|---|
| RF01 | N01 | Contexto §1, CU1, Componentes §6 | `motor_narrativo/cargador.py::cargar_historia` | `tests/test_integracion.py::test_I1_archivo_real_hasta_cada_final`, `::test_I1_segunda_historia_con_el_mismo_motor` |
| RF02 | N01 | Clases §3 (Historia), Estados §5 | `motor_narrativo/sesion.py::Sesion.reiniciar` | `tests/test_motor.py::test_U5_reiniciar_restaura_escena_y_variables_iniciales` |
| RF03 | N02 | CU2, Secuencia §4 | `motor_narrativo/cli.py::jugar` | `tests/test_integracion.py::test_I1_interfaz_consola_recorre_un_final_y_reinicia` |
| RF04 | N02 | Clases §3 (Opcion.habilitada) | `motor_narrativo/modelo.py::Opcion.habilitada`, `sesion.py::opciones_disponibles` | `tests/test_motor.py::test_U1_*` (CA01) |
| RF05 | N03 | Secuencia §4 | `sesion.py::Sesion.elegir` | `tests/test_motor.py::test_U2_*` |
| RF06 | N03 | Secuencia §4 (alt), Estados §5 | `sesion.py::Sesion.elegir`, `cli.py::jugar` | `tests/test_motor.py::test_U3_*`, `::test_CA02_*`, `tests/test_rnf.py::test_RNF03_*` |
| RF07 | N04 | Clases §3 (Sesion) | `sesion.py` (`_variables`, `_recorrido`) | `tests/test_motor.py::test_U2_*`, `tests/test_rnf.py::test_RNF01_agregar_escena_*` |
| RF08 | N05 | Estados §5 (Final), CU6 | `sesion.py::estado`, `cli.py::jugar` | `tests/test_motor.py::test_U3_no_se_puede_elegir_en_un_final`, `test_integracion.py::test_I1_*` |
| RF09 | N05 | CU4, Estados §5 | `sesion.py::reiniciar` | `tests/test_motor.py::test_U5_*` |
| RF10 | N06 | CU5, ADR-01 | `cargador.py::validar`, `construir_historia` | `tests/test_validacion.py::test_U4_*`, `::test_CA03_*` |
| RF11 | N06 | Clases §3 (Problema) | `errores.py`, `cargador.py` | `tests/test_rnf.py::test_RNF02_*` |
| RF12 | N06 | CU5 | `cli.py::main` (`validar`) | `tests/test_integracion.py::test_I1_comando_validar_desde_terminal` |
| RF13 | N03/N06 | Estados §5 (Bloqueada) | `sesion.py::estado`, `cli.py` | `tests/test_motor.py::test_escena_no_final_sin_opciones_habilitadas_queda_bloqueada` |
| RF14 | Cambio | CU7, Clases §3 (Instantanea), Secuencia §4.1, Estados §5, ADR-03 | `sesion.py::Sesion.deshacer`, `_instantanea`, `_restaurar` | `tests/test_deshacer.py::test_U6_ejemplo_del_anexo` |
| RF15 | Cambio | Estados §5 (nota), ADR-03 | `sesion.py::deshacer` (`_anterior = None`) | `tests/test_deshacer.py::test_U6_un_solo_nivel`, `::test_U6_nueva_eleccion_valida_vuelve_a_habilitar_el_retroceso` |
| RF16 | Cambio | Estados §5 | `sesion.py::reiniciar` | `tests/test_deshacer.py::test_U6_al_comenzar_no_hay_retroceso`, `tests/test_motor.py::test_U5_*` |
| RF17 | Cambio | Secuencia §4, Diseño detallado §8 | `sesion.py::elegir` (instantánea solo en rama válida) | `tests/test_deshacer.py::test_U6_entrada_invalida_*`, `tests/test_rnf.py::test_RNF03_entradas_aleatorias_*` |
| RF18 | Cambio | Estados §5 (Final → EnCurso) | `sesion.py::deshacer` | `tests/test_deshacer.py::test_U6_deshacer_desde_un_final_vuelve_a_E3`, `tests/test_integracion.py::test_I1_cargar_recorrer_y_deshacer_desde_un_final` |
| RF19 | Cambio | Secuencia §4.1 | `cli.py::jugar`, `cli.py::_menu` | `tests/test_integracion.py::test_I1_consola_deshacer_desde_un_final` |
| RNF01 | — | Componentes §6, ADR-02 | todo `motor_narrativo/` (sin ids de historias) | `tests/test_rnf.py::test_RNF01_*` + `historias/el_faro.json` |
| RNF02 | — | ADR-01 | `errores.py`, `cargador.py` | `tests/test_rnf.py::test_RNF02_*` |
| RNF03 | — | Diseño detallado §8 | `sesion.py::elegir`, `cli.py`, `cargador.py` | `tests/test_rnf.py::test_RNF03_*` |

Registro de la última ejecución: `resultados/ultima_ejecucion.txt` y `resultados/junit.xml`.

## Cambio de la hora 6 — análisis de impacto

Solicitud: «el lector debe poder deshacer su última decisión, revirtiendo todas sus consecuencias». Reemplaza el acuerdo provisional de no implementar retroceso.

| Elemento | Antes (`v1-antes-cambio`) | Después (`v2-con-cambio`) | Evidencia |
|---|---|---|---|
| Requisitos | RF01–RF13; §4 acuerdo «sin retroceso» | + RF14–RF19; §4 marcado como resuelto; P4 respondida, P5 supuesto | `docs/requisitos.md` |
| Modelos | CU1–CU6; Sesion sin historial | + CU7; clase `Instantanea`; secuencia §4.1; transiciones `deshacer()` en estados; ADR-03 | `docs/arquitectura.md` |
| Componentes | — | `motor_narrativo/sesion.py` (modificado), `motor_narrativo/cli.py` (comando `d`). **Sin cambios:** `modelo.py`, `cargador.py`, `errores.py`, `historias/*.json` | `git diff v1-antes-cambio v2-con-cambio --stat` |
| Pruebas nuevas | U1–U5, I1 | **U6** en `tests/test_deshacer.py` (ejemplo del anexo, inicio, entrada inválida ×5 variantes, nueva elección rehabilita, un nivel, desde cada final ×3) | `resultados/ultima_ejecucion.txt` |
| Pruebas extendidas | — | U5: reiniciar elimina historial. I1: cargar archivo, recorrer y deshacer desde cada final + consola con `d`. RNF03: deshacer incluido en las 2 000 entradas aleatorias | `tests/test_motor.py`, `tests/test_integracion.py`, `tests/test_rnf.py` |
| Backlog | B09 «Solicitud de cambio» sin definir | B09a–B09d (ver `docs/plan_y_proceso.md`) | tablero |
| Resultado | 62 pruebas en verde | 81 pruebas en verde | `resultados/junit.xml` |

**Por qué el impacto fue bajo:** la separación contenido / reglas / interfaz (ADR-02) concentró el estado de partida en `Sesion`; el retroceso es estado de partida, así que no tocó el contenido ni el validador.

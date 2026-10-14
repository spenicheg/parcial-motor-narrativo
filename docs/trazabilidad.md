# Matriz de trazabilidad (v1 — antes del cambio)

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
| RNF01 | — | Componentes §6, ADR-02 | todo `motor_narrativo/` (sin ids de historias) | `tests/test_rnf.py::test_RNF01_*` + `historias/el_faro.json` |
| RNF02 | — | ADR-01 | `errores.py`, `cargador.py` | `tests/test_rnf.py::test_RNF02_*` |
| RNF03 | — | Diseño detallado §8 | `sesion.py::elegir`, `cli.py`, `cargador.py` | `tests/test_rnf.py::test_RNF03_*` |

Registro de la última ejecución: `resultados/ultima_ejecucion.txt` y `resultados/junit.xml`.

## Cambio de la hora 6 (completar)

| Elemento | Antes (`v1-antes-cambio`) | Después (`v2-con-cambio`) | Evidencia |
|---|---|---|---|
| RF nuevos / modificados | | | |
| Modelos afectados | | | |
| Componentes afectados | | | |
| Pruebas nuevas (U6) / extendidas | | | |

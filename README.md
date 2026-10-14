# Motor de ficción interactiva — «La última transmisión»

Parcial de Ingeniería de Software (UTB).

**Integrantes:** Sebastián _(apellidos completos)_ · _(nombre completo del integrante 2)_

## Requisitos de software

| Herramienta | Versión probada | Uso |
|---|---|---|
| Python | 3.10 o superior (probado en 3.13) | ejecución |
| pytest | 8.x / 9.x (probado en 9.1.1) | solo pruebas |
| Git | 2.x | versionado |

El motor solo usa la biblioteca estándar de Python (`json`, `dataclasses`, `argparse`, `enum`, `pathlib`).

## Instalación

```bash
git clone <repo>   # o descomprimir el ZIP
cd parcial
python -m venv .venv
# Windows: .venv\Scripts\activate     Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Ejecución

```bash
python -m motor_narrativo jugar historias/la_ultima_transmision.json
python -m motor_narrativo jugar historias/el_faro.json               # segunda historia, mismo motor
python -m motor_narrativo validar historias/la_ultima_transmision.json
python -m motor_narrativo validar historias/ejemplos_con_error/destino_inexistente.json   # muestra el error (código de salida 2)
```

En el juego: escriba el **número** de la opción, `d` para deshacer la última decisión (un nivel), `r` para reiniciar, `s` para salir.

### Rutas para demostrar cada final

| Final | Teclas | Opciones |
|---|---|---|
| E4 Rescate | `1`, `1`, `1` | Revisar señal → Investigar archivo → Activar con código |
| E5 El eco | `1`, `2`, `1` | Revisar señal → Continuar sin investigar → Activar sin verificar |
| E6 Silencio | `1`, `1`, `2` (o `1`, `2`, `2`) | … → Cortar comunicación |

**Deshacer (cambio de la hora 6):** desde cualquier final pulse `d` para volver a E3 con las variables anteriores; un segundo `d` no hace nada hasta que elija de nuevo. Ejemplo de demo: `1`, `1`, `2` (E6) → `d` (E3) → `1` (E4).

Cómo una condición cambia las opciones: en E3, tras *Investigar* aparece «Activar con código»; tras *Continuar* aparece «Activar sin verificar».

## Pruebas

```bash
python -m pytest                                   # todas
python -m pytest -v tests/test_rnf.py              # requisitos no funcionales
python -m pytest -v --junitxml=resultados/junit.xml | tee resultados/ultima_ejecucion.txt
```

| Escenario | Archivo |
|---|---|
| U1 condiciones habilitan opciones | `tests/test_motor.py::test_U1_*` |
| U2 efectos y destino | `tests/test_motor.py::test_U2_*` |
| U3 opción inexistente/no habilitada no altera estado | `tests/test_motor.py::test_U3_*` |
| U4 errores de contenido (parametrizada) | `tests/test_validacion.py::test_U4_*` |
| U5 reinicio (+ elimina historial de retroceso) | `tests/test_motor.py::test_U5_*` |
| U6 deshacer (cambio hora 6) | `tests/test_deshacer.py::test_U6_*` |
| I1 archivo real + motor hasta un final (+ deshacer desde un final) | `tests/test_integracion.py::test_I1_*` |
| CA01 / CA02 / CA03 | `test_U2_CA01_*`, `test_CA02_*`, `test_CA03_*` |
| Bloqueo en partida | `test_escena_no_final_sin_opciones_habilitadas_queda_bloqueada` |
| RNF01–RNF03 | `tests/test_rnf.py` |

## Formato de contenido (para escritores)

Un archivo `.json` en UTF‑8 por historia. Se usa el contrato de referencia de la guía **sin cambios**.

```json
{
  "titulo": "Nombre visible",
  "inicio": "ID de la escena inicial",
  "variables": { "nombre_variable": false },
  "escenas": [
    {
      "id": "E1",
      "texto": "Lo que lee el lector.",
      "final": false,
      "opciones": [
        { "id": "abrir", "texto": "Abrir la puerta", "destino": "E2",
          "condiciones": { "tiene_llave": true },
          "efectos": { "puerta_abierta": true } }
      ]
    }
  ]
}
```

Reglas:
- Todos los campos son obligatorios. `condiciones` y `efectos` pueden ser `{}`.
- `condiciones`: la opción aparece solo si **todas** las variables tienen esos valores. `{}` = siempre aparece.
- `efectos`: al elegir, se asignan esos valores. `{}` = no cambia nada.
- Solo `true` / `false` (sin comillas). Toda variable usada debe estar declarada en `variables`.
- Escenas finales: `"final": true` y `"opciones": []`. Las demás: al menos una opción.
- IDs de escena únicos en todo el archivo; IDs de opción únicos dentro de su escena.

### Errores de contenido

Antes de jugar se valida todo el archivo y se listan **todos** los problemas con el formato `[CÓDIGO] ubicación: causa`. Ejemplo:

```
La historia tiene 1 problema(s) y no se puede jugar:
  1. [DESTINO_INEXISTENTE] escena 'E3' › opción 'activar_codigo' › destino: la escena destino 'E99' no existe
```

Códigos: `ARCHIVO_ILEGIBLE`, `ESTRUCTURA_INVALIDA`, `CAMPO_AUSENTE`, `TIPO_INVALIDO`, `INICIO_INEXISTENTE`, `ESCENA_DUPLICADA`, `OPCION_DUPLICADA`, `DESTINO_INEXISTENTE`, `VARIABLE_NO_DECLARADA`, `VALOR_NO_BOOLEANO`, `FINAL_CON_OPCIONES`, `ESCENA_SIN_OPCIONES`.

## Estructura

```
motor_narrativo/   modelo.py (dominio) · sesion.py (reglas) · cargador.py + errores.py (contenido) · cli.py (interfaz)
historias/         la_ultima_transmision.json · el_faro.json · ejemplos_con_error/
tests/             test_motor.py · test_validacion.py · test_integracion.py · test_rnf.py
docs/              requisitos.md · arquitectura.md · trazabilidad.md · plan_y_proceso.md
resultados/        ultima_ejecucion.txt · junit.xml
```

## Limitaciones conocidas

- El retroceso es de un solo nivel y no existe «rehacer» (según la solicitud de cambio).
- Solo variables booleanas y condiciones de igualdad.
- No se analiza si todos los finales son alcanzables; un bloqueo se detecta durante la partida.
- Interfaz solo de consola; no guarda partidas entre ejecuciones.

## Bibliotecas, licencias y herramientas de apoyo

| Recurso | Licencia | Para qué | Verificación |
|---|---|---|---|
| Python estándar | PSF | todo el motor | — |
| pytest | MIT | pruebas automatizadas | — |
| Claude (Anthropic), asistente de IA | — | borrador inicial de código, pruebas y documentación | _(completar: cómo revisaron y probaron cada parte, qué modificaron)_ |
| Mermaid | MIT | diagramas | renderizados en mermaid.live |

## Versiones

- `v1-antes-cambio`: versión inicial antes de la solicitud de cambio.
- `v2-con-cambio`: incorpora deshacer (RF14–RF19). Impacto: `docs/trazabilidad.md` y `git diff v1-antes-cambio v2-con-cambio --stat`.
- Historial: `git log --pretty=format:"%h | %an | %ad | %s" --date=iso > resultados/git_log.txt`

## Video de demostración

_(enlace o `demo.mp4`)_

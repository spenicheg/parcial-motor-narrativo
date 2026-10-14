# Fundamentos, proceso, agilidad y plan de 12 horas

> Completar con los nombres reales de la pareja: **Integrante A** = Sebastián (…), **Integrante B** = (…).

## Unidad 1 — Fundamentos

- **Problema:** el colectivo necesita publicar relatos interactivos editables por no programadores, con decisiones condicionadas y detección temprana de errores.
- **Actores:** Escritora (crea y edita archivos), Diseñador de la experiencia (define condiciones y consecuencias), Lector (juega), Coordinadora del festival (opera y verifica).
- **Alcance v1:** consola, archivos JSON locales, variables booleanas, validación, reinicio. **Fuera:** cuentas, BD, guardado, red, editor visual, multimedia, expresiones, retroceso.
- **Riesgos:** (R1) la solicitud de cambio de la hora 6 obliga a rehacer el núcleo → mitigación: reglas aisladas en `sesion.py` y validador en `cargador.py`, cada cambio toca un módulo. (R2) la escritora edita JSON a mano y comete errores de sintaxis → mitigación: mensajes con línea/columna y ubicación (RNF02).
- **Atributos priorizados:** 1) Modificabilidad del contenido, 2) Claridad de errores, 3) Confiabilidad, 4) Facilidad de uso. Rendimiento no es prioritario (historias pequeñas).
- **Responsabilidad profesional:** el texto de las historias es autoría del colectivo; el programa no modifica ni publica los archivos, solo los lee. Se usa una sola dependencia de desarrollo (pytest, licencia MIT) y ninguna en ejecución, para reducir riesgos de licencias y de cadena de suministro. Se declara el uso de herramientas de IA en el README.

## Unidad 2 — Proceso

- **Elegido:** incremental con iteraciones cortas tipo Scrum adaptado a 12 h (3 incrementos de ~3 h + 1 de cierre).
- **Alternativa comparada:** cascada. Se descarta porque el cambio llega a la hora 6: con cascada aún estaríamos en diseño/implementación sin pruebas, y el costo de reabrir requisitos sería mayor.
- **Actividades en esta entrega:**
  - *Especificación:* RF/RNF en `docs/requisitos.md`, revisados por ambos.
  - *Desarrollo:* TDD ligero — primero pruebas U1–U5 desde los CA, luego código.
  - *Validación:* `pytest` en cada commit; recorrido manual de los 3 finales; RNF automatizados.
  - *Evolución:* análisis de impacto de la solicitud de cambio con la matriz de trazabilidad; etiquetas Git `v1-antes-cambio` y `v2-con-cambio`.

## Unidad 3 — Agilidad

**Backlog (prioridad descendente)**

| ID | Historia de usuario | RF | Resp. | Est. |
|---|---|---|---|---|
| B01 | Como escritora quiero cargar una historia desde un archivo | RF01, RF02 | A | 1 h |
| B02 | Como escritora quiero saber todos los errores de mi archivo | RF10–RF12 | B | 2 h |
| B03 | Como lector quiero ver solo opciones coherentes con lo que sé | RF03, RF04 | A | 1 h |
| B04 | Como lector quiero que mis elecciones tengan consecuencias | RF05–RF07 | A | 1 h |
| B05 | Como lector quiero ver el final y volver a empezar | RF08, RF09, RF13 | B | 1 h |
| B06 | Como coordinadora quiero pruebas automáticas de RNF | RNF01–03 | B | 1 h |
| B07 | Segunda historia + README | RF01 | A | 0,5 h |
| B08 | Diagramas, ADR, informe | — | A+B | 2 h |
| B09 | Solicitud de cambio (hora 6) | por definir | A+B | 2–3 h |

**Tablero:** columnas *Por hacer / En curso / En revisión / Hecho* (GitHub Projects, Trello o una tabla). Capturas: inicial (hora 0–1) y final (hora 11–12).

**Prácticas ágiles usadas:**
1. *Programación en pareja con rol rotativo* (piloto/copiloto cada hora): ambos conocen todo el código → la nota es compartida y no hay sustentación.
2. *Integración continua local*: `pytest` antes de cada commit; ningún commit rompe pruebas.
- **Descartada:** *Planning poker* — con dos personas y 12 h el costo de la ceremonia supera el beneficio; se estima directamente en horas.

**Definición de terminado:** código en `main`, pruebas en verde, RF trazado en `docs/trazabilidad.md`, README actualizado si cambia el uso.

**Aprendizaje y mejora (completar al cierre):** p. ej. «Al principio redactamos RF06 de forma no verificable → acción: escribir el CA antes del enunciado del RF».

## Plan de 12 horas

| Hora | Integrante A | Integrante B | Hito / commit |
|---|---|---|---|
| 0–0:30 | Leer guía, crear repo, tablero (captura inicial) | Leer guía, borrador RF | — |
| 0:30–1:30 | Revisar RF/RNF juntos, preguntas y conflicto | ídem | `docs: requisitos v1` |
| 1:30–3:30 | `modelo.py`, `sesion.py` + U1, U2, U3, U5 | `cargador.py` + U4, CA03 | `feat: motor`, `feat: validador` |
| 3:30–4:30 | `cli.py`, I1, segunda historia | RNF01–03 | `test: integración y RNF` |
| 4:30–5:45 | Diagramas (Mermaid → PNG) | README, ADR | **Tag `v1-antes-cambio`** |
| **6:00** | **Descargar Solicitud de cambio** — ambos | | |
| 6:00–6:30 | Análisis de impacto en la matriz, ajustar backlog | ídem | `docs: impacto del cambio` |
| 6:30–9:00 | Implementar cambio + prueba U6 | Extender U4/I1 y diagramas afectados | **Tag `v2-con-cambio`** |
| 9:00–10:30 | Grabar video (≤ 6 min) | Informe PDF (≤ 8 págs) + anexo | — |
| 10:30–11:30 | Revisión cruzada, `git log` exportado, captura final | Ejecutar pruebas → `resultados/` | `chore: entrega` |
| 11:30–12:00 | Armar ZIP y verificar que se instala desde cero en otra carpeta | | **Entrega** |

**Preparación para el cambio:** puntos de extensión probables y dónde tocarían:
- Variables no booleanas u operadores → `cargador.validar` (tipos) + `Opcion.habilitada`.
- Retroceso → `Sesion` (pila de estados) + comando en `cli.py`.
- Nuevo tipo de error → `errores.py` + `cargador.py` + caso en `CASOS` de U4.
- Opciones de un solo uso / contador de visitas → `Sesion.recorrido` ya existe.

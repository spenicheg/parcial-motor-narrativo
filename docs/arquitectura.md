# Modelos y arquitectura

Diagramas en Mermaid (se renderizan en GitHub, VS Code o https://mermaid.live → exportar PNG/SVG para el anexo PDF). El mapa narrativo de la historia está al final y **no** sustituye a los modelos del software.

## 1. Contexto

```mermaid
flowchart LR
  Escritora([Escritora]) -- "edita archivo .json" --> Archivo[(Historia .json)]
  Escritora -- "validar" --> Sistema
  Lector([Lector]) -- "elige / reinicia" --> Sistema[[Motor de ficción interactiva]]
  Sistema -- "escena, opciones, final" --> Lector
  Archivo -- "lectura" --> Sistema
  Sistema -- "lista de problemas" --> Escritora
  Coordinadora([Coordinadora del festival]) -. "ejecuta pruebas / demo" .-> Sistema
```

## 2. Casos de uso

```mermaid
flowchart LR
  L([Lector]) --- CU1((CU1 Iniciar partida))
  L --- CU2((CU2 Ver escena y opciones))
  L --- CU3((CU3 Elegir opción))
  L --- CU4((CU4 Reiniciar partida))
  L --- CU7((CU7 Deshacer última decisión))
  E([Escritora]) --- CU5((CU5 Validar historia))
  CU1 -. include .-> CU5
  CU3 -. extend: final o bloqueo .-> CU6((CU6 Ver desenlace / bloqueo))
```

| CU | RF |
|---|---|
| CU1 | RF01, RF02, RF10 |
| CU2 | RF03, RF04 |
| CU3 | RF05, RF06, RF07 |
| CU4 | RF09 |
| CU5 | RF10, RF11, RF12 |
| CU6 | RF08, RF13 |
| CU7 (cambio) | RF14–RF19 |

## 3. Clases del dominio

```mermaid
classDiagram
  class Historia {
    titulo: str
    inicio: str
    variables_iniciales: Map~str,bool~
    escena(id) Escena
    finales() List~Escena~
  }
  class Escena {
    id: str
    texto: str
    final: bool
    opcion(id) Opcion
  }
  class Opcion {
    id: str
    texto: str
    destino: str
    condiciones: Map~str,bool~
    efectos: Map~str,bool~
    habilitada(variables) bool
  }
  class Sesion {
    -escena_id: str
    -variables: Map~str,bool~
    -recorrido: List~str~
    -anterior: Instantanea
    puede_deshacer() bool
    opciones_disponibles() List~Opcion~
    estado() EstadoSesion
    elegir(opcion_id) ResultadoEleccion
    deshacer() ResultadoEleccion
    reiniciar()
  }
  class Instantanea {
    escena_id: str
    variables: Map~str,bool~
    recorrido: List~str~
  }
  class EstadoSesion {
    <<enumeration>>
    EN_CURSO
    FINAL
    BLOQUEADA
  }
  class Cargador {
    <<módulo>>
    cargar_historia(ruta) Historia
    validar(datos) List~Problema~
  }
  class Problema {
    codigo: str
    ubicacion: str
    mensaje: str
  }
  class ErrorContenido {
    problemas: List~Problema~
  }
  Historia "1" *-- "1..*" Escena
  Escena "1" *-- "0..*" Opcion
  Opcion --> Escena : destino
  Sesion --> Historia
  Sesion "1" o-- "0..1" Instantanea : anterior
  Sesion ..> EstadoSesion
  Cargador ..> Historia : construye
  Cargador ..> ErrorContenido : lanza
  ErrorContenido *-- Problema
```

## 4. Secuencia: elegir una opción

```mermaid
sequenceDiagram
  actor Lector
  participant CLI as cli.jugar
  participant S as Sesion
  participant O as Opcion
  Lector->>CLI: "1"
  CLI->>CLI: número → opcion_id (de opciones visibles)
  CLI->>S: elegir(opcion_id)
  S->>S: estado == EN_CURSO?
  S->>O: habilitada(variables) [por cada opción]
  alt opción habilitada encontrada
    S->>S: anterior ← instantánea(escena, variables, recorrido)
    S->>S: variables ← variables + efectos
    S->>S: escena ← destino; recorrido += destino
    S-->>CLI: ResultadoEleccion(aceptada=true)
  else inexistente / no habilitada
    S-->>CLI: ResultadoEleccion(aceptada=false, mensaje)
  end
  CLI->>S: escena, estado, opciones_disponibles()
  CLI-->>Lector: texto de escena y opciones / FINAL / bloqueo
```

### 4.1 Secuencia: deshacer (cambio hora 6)

```mermaid
sequenceDiagram
  actor Lector
  participant CLI as cli.jugar
  participant S as Sesion
  Lector->>CLI: "d"
  CLI->>S: deshacer()
  alt anterior ≠ nulo
    S->>S: escena, variables, recorrido ← anterior
    S->>S: anterior ← nulo
    S-->>CLI: ResultadoEleccion(true, "Se deshizo…")
  else sin historial
    S-->>CLI: ResultadoEleccion(false, "No hay una decisión para deshacer.")
  end
  CLI-->>Lector: escena restaurada / mensaje
```

## 5. Estados de una sesión

```mermaid
stateDiagram-v2
  [*] --> EnCurso: Sesion(historia válida)
  EnCurso --> EnCurso: elegir(opción válida) → escena no final con opciones
  EnCurso --> EnCurso: elegir(inválida) / sin cambios
  EnCurso --> Final: elegir → escena final
  EnCurso --> Bloqueada: elegir → escena no final sin opciones habilitadas
  Final --> EnCurso: reiniciar()
  Bloqueada --> EnCurso: reiniciar()
  EnCurso --> EnCurso: reiniciar()
  EnCurso --> EnCurso: deshacer() [hay anterior]
  Final --> EnCurso: deshacer() [hay anterior]
  Bloqueada --> EnCurso: deshacer() [hay anterior]
  note right of EnCurso
    Variable de historial: anterior ∈ {nulo, instantánea}
    elegir válida → anterior = estado previo
    deshacer / reiniciar / inicio → anterior = nulo
  end note
  Final --> [*]: salir
  Bloqueada --> [*]: salir
```

## 6. Componentes / capas

```mermaid
flowchart TB
  subgraph Interfaz
    CLI["cli.py<br/>lee teclado, imprime, mapea número→id"]
  end
  subgraph Reglas
    SES["sesion.py<br/>estado de partida, condiciones, efectos, reinicio"]
  end
  subgraph Dominio
    MOD["modelo.py<br/>Historia, Escena, Opcion (inmutables)"]
  end
  subgraph Contenido
    CAR["cargador.py<br/>lee JSON, valida, construye Historia"]
    ERR["errores.py<br/>Problema, ErrorContenido, códigos"]
    JSON[("historias/*.json")]
  end
  CLI --> SES
  CLI --> CAR
  SES --> MOD
  CAR --> MOD
  CAR --> ERR
  CAR --> JSON
```

Regla de dependencias: las flechas solo van hacia abajo. `sesion.py` no sabe que existe JSON ni consola; `cargador.py` no sabe de reglas de juego; `modelo.py` no depende de nada.

**Separación contenido / reglas / interfaz:** el contenido cambia con frecuencia y lo editan no programadores; las reglas cambian rara vez; la interfaz podría pasar a web en el festival. Separarlos permite que cada cambio toque un solo módulo (RNF01) y que las reglas se prueben sin archivos ni teclado.

## 7. Decisiones de arquitectura (ADR)

### ADR-01 Validar todo antes de jugar y reportar todos los problemas
- **Contexto:** N06 y la coordinadora piden saber qué corregir sin que el programa se cierre.
- **Alternativas:** (a) validar de forma perezosa al entrar a cada escena; (b) detenerse en el primer error; (c) validar todo el archivo al cargar y acumular problemas.
- **Elección:** (c). `construir_historia` solo crea objetos si `validar` devuelve lista vacía.
- **Consecuencias:** + la escritora corrige todo en una pasada (RNF02); + `Sesion` puede asumir datos válidos y queda simple. − No detecta finales inalcanzables (fuera de alcance); el bloqueo se maneja en partida (RF13).

### ADR-02 Motor de reglas guiado por datos con estado inmutable de historia
- **Contexto:** RNF01 exige cambiar el relato sin tocar código; la guía prohíbe lógica específica por id.
- **Alternativas:** (a) clases/`if` por escena; (b) lenguaje de expresiones (eval); (c) mapas de igualdad booleanos evaluados genéricamente.
- **Elección:** (c). `Opcion.habilitada` = todas las igualdades se cumplen; efectos = actualización del mapa.
- **Consecuencias:** + 0 líneas de motor por historia; + sin `eval` (seguro). − Solo booleanos; ampliar a números u operadores requiere cambiar validador y `Opcion.habilitada` (cambio localizado en dos funciones).

### ADR-03 Deshacer mediante instantánea del estado anterior (cambio hora 6)
- **Contexto:** el cliente pide deshacer la última decisión revirtiendo todas sus consecuencias, un solo nivel, también desde un final.
- **Alternativas:** (a) calcular efectos inversos de la opción (requiere guardar valores previos de cada variable tocada; frágil si cambian los efectos); (b) patrón Command con pila de comandos (pensado para múltiples niveles y rehacer, que no se piden); (c) guardar una **instantánea inmutable** (escena, variables, recorrido) antes de cada elección válida.
- **Elección:** (c), con un único campo `anterior`.
- **Consecuencias:** + restauración exacta por construcción (RF14); + cambio confinado a `sesion.py` y a un comando en `cli.py`: **0 cambios** en `modelo.py`, `cargador.py`, `errores.py` ni en los JSON; + si se piden más niveles, `anterior` pasa a ser una pila. − Memoria de una copia de variables por partida (despreciable).

## 8. Decisión de diseño detallado (unidad 7)

`Sesion.elegir` recibe un **id**, no un número de menú, y siempre devuelve un `ResultadoEleccion` en vez de lanzar excepciones. Así (1) la consola es la única que conoce la numeración, y una futura interfaz web no cambia las reglas (bajo acoplamiento); (2) el estado se calcula en una copia y solo se asigna al final, de modo que una entrada inválida no puede dejarlo a medias (RF06, RNF03). Las vistas `variables` y `recorrido` devuelven copias para que nadie modifique el estado desde fuera. Con el cambio, la instantánea se toma **solo** en la rama de elección válida, de modo que una entrada inválida no puede reemplazar el historial (RF17).

## 9. Mapa narrativo (contenido, no modelo de software)

```mermaid
flowchart LR
  E1 -->|revisar| E2
  E2 -->|"investigar / conoce_origen=true"| E3
  E2 -->|continuar| E3
  E3 -->|"activar_codigo [conoce_origen=true]"| E4((E4 Rescate))
  E3 -->|"activar_sin_verificar [conoce_origen=false]"| E5((E5 Eco))
  E3 -->|cortar| E6((E6 Silencio))
```

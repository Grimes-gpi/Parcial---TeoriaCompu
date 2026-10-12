# Especificación técnica

## Simulador gráfico de autómatas finitos

**Integrantes:** Integrante 1 e Integrante 2 (reemplazar por los nombres completos)  
**Asignatura:** Teoría de la Computación  
**Fase:** 0. Especificación  
**Fecha:** 12 de octubre de 2026

## 1. Propósito y alcance

Este documento define los requisitos para una aplicación de escritorio que permita editar autómatas finitos, convertir un AFND en un AFD mediante el método de subconjuntos, obtener una expresión regular equivalente mediante sistemas de ecuaciones y comprobar experimentalmente la equivalencia de los tres modelos. El diseño responde a la guía del parcial, que solicita una aplicación local con dos módulos conectados, explicación de los pasos y verificación hasta una longitud configurable (*Teoría de la computación: Parcial del segundo corte*, s. f.).

La aplicación se implementará en **Python 3 con Tkinter**, usando la biblioteca estándar. Será una única aplicación local: no tendrá servidor, acceso a internet, llamadas a API, CDN, ni dependencias que deban descargarse para ejecutarla. La interfaz y los mensajes estarán en español. El proyecto se desarrollará en pareja; ambos integrantes deben poder explicar el modelo, los algoritmos y las decisiones de implementación.

El alcance obligatorio comprende edición/validación del autómata, conversión AFND→AFD, obtención AF→ER, visualización de grafos y pasos, e inspección exhaustiva de cadenas hasta una longitud n. El soporte de transiciones ε se implementa como bonus y debe poder activarse sin cambiar el significado de las entradas ordinarias.

## 2. Términos y convenciones

- **AF:** autómata finito, posiblemente no determinista.
- **AFND:** autómata finito no determinista. Para un estado y símbolo puede haber cero, una o varias transiciones.
- **AFD:** autómata finito determinista. Para cada estado y símbolo hay exactamente un destino.
- **Σ:** alfabeto finito de símbolos de entrada. ε no pertenece a Σ.
- **ε (o λ en la expresión mostrada):** cadena vacía; consume cero símbolos.
- **∅:** lenguaje vacío si aparece en una ER; subconjunto vacío/estado pozo si aparece como estado del AFD.
- **Cadena:** secuencia finita de símbolos de Σ. La cadena de longitud cero se denota ε.
- **ER:** expresión regular que denota un lenguaje sobre Σ.

En la interfaz, los símbolos del alfabeto serán caracteres individuales no vacíos, distintos entre sí y diferentes de ε, λ, ∅ y los operadores reservados `+`, `*`, `(`, `)`, `·`. Los nombres de estado son identificadores de texto no vacíos; no se interpretan como símbolos del alfabeto. Los espacios alrededor de entradas se eliminan; los espacios internos no se aceptan en nombres de estado ni en símbolos. El alfabeto puede tener un solo símbolo.

## 3. Usuarios y flujo principal

El usuario es un estudiante que necesita ingresar un autómata, observar y explicar su conversión y revisar la ER resultante. El flujo principal será:

1. Crear un autómata en el editor o importar un archivo JSON.
2. Validar y visualizar el AFND.
3. Ejecutar la conversión por subconjuntos y consultar la tabla, el grafo del AFD y la traza paso a paso.
4. Enviar el AFD resultante al módulo de ecuaciones, consultar las ecuaciones, sustituciones y simplificaciones, y obtener la ER.
5. Elegir n (n ≥ 6) y comparar AFND, AFD y ER para todas las cadenas de Σ de longitud entre 0 y n, inclusive.
6. Consultar o exportar los resultados y los datos del autómata.

## 4. Requisitos funcionales

### 4.1 Editor, modelo y validación

**RF-01. Crear y editar.** La interfaz permitirá definir estados, alfabeto, estado inicial, estados finales y transiciones. El usuario podrá modificar y eliminar elementos; la interfaz indicará cualquier transición que quede inválida por una edición.

**RF-02. Validar antes de calcular.** El sistema comprobará que:

- haya al menos un estado y los nombres sean únicos;
- haya al menos un símbolo en el alfabeto y los símbolos sean únicos;
- el estado inicial pertenezca al conjunto de estados;
- todos los estados finales pertenezcan al conjunto de estados;
- el origen y destino de cada transición pertenezcan al conjunto de estados;
- cada etiqueta de transición pertenezca a Σ, excepto ε cuando esté activado el bonus;
- no haya campos requeridos vacíos ni valores duplicados ambiguos.

Si hay errores, no ejecutará la conversión y mostrará el campo, el valor implicado y una explicación corregible. Un estado puede no tener transiciones, ser inalcanzable o no ser final. El conjunto de estados finales puede estar vacío.

**RF-03. Guardar/intercambiar datos.** Se podrán importar y exportar autómatas como JSON UTF-8 con el esquema de la sección 5. Un archivo inválido no reemplazará el autómata que ya está abierto. El editor gráfico seguirá siendo la forma principal de trabajo.

**RF-04. Símbolo único.** Si |Σ| = 1, todas las operaciones, tablas, grafos y generación de cadenas funcionarán con ese símbolo, sin depender de que haya al menos dos columnas o ramas.

### 4.2 Módulo 1: AFND a AFD

**RF-05. Método de subconjuntos.** El módulo calculará el estado inicial del AFD como el conjunto que contiene el estado inicial del AFND (o su clausura-ε si el bonus está activo). Para cada subconjunto alcanzable S y símbolo a ∈ Σ calculará δD(S,a) = ⋃(q∈S) δN(q,a), aplicando clausura-ε al resultado si corresponde. Procesará los subconjuntos nuevos hasta que no quede ninguno pendiente.

**RF-06. Estados finales.** Un subconjunto del AFD será final si contiene al menos un estado final del AFND, luego de aplicar la convención de clausura-ε.

**RF-07. Estado pozo.** Si el cálculo de una transición produce el subconjunto vacío, se añadirá ∅ como estado del AFD. Sus transiciones para todos los símbolos serán ∅→∅. El estado ∅ se mostrará en la tabla y el grafo cuando sea alcanzable desde el estado inicial. La conversión generará los subconjuntos alcanzables; no añadirá subconjuntos inalcanzables solo por completar la potencia de Q.

**RF-08. Tabla.** La tabla mostrará una fila por subconjunto alcanzable y una columna por símbolo, además de las marcas de estado inicial y final. Los nombres de conjuntos tendrán un orden de presentación estable, por ejemplo `{q0,q1}`; ∅ se mostrará literalmente como `∅`. El orden visual no cambia la identidad matemática del subconjunto.

**RF-09. Traza paso a paso.** El usuario podrá avanzar y retroceder por la traza. Cada registro identificará el subconjunto procesado, el símbolo, las transiciones AFND consultadas, la unión de destinos, el destino calculado y si este es nuevo, final o ∅. Debe ser posible ver la traza completa además del control paso a paso.

**RF-10. Grafos.** Se visualizarán por separado el AFND de entrada y el AFD obtenido. Los estados se dibujarán como óvalos; el inicial tendrá una flecha de entrada sin origen; los finales tendrán doble círculo; las transiciones serán flechas etiquetadas. Las transiciones entre los mismos dos estados podrán agrupar etiquetas. El diseño inicial será legible y el usuario podrá reubicar estados sin cambiar el autómata. El lienzo permitirá desplazamiento si el grafo excede el área visible.

### 4.3 Módulo 2: AF a expresión regular

**RF-11. Entrada conectada.** El módulo recibirá directamente el AFD producido por el Módulo 1. También aceptará un AF válido ingresado/importado, interpretando varias transiciones con el mismo origen y símbolo como alternativas. Si hay ε-transiciones, las eliminará antes de construir el sistema mediante `δ'(q,a) = clausura-ε(⋃(r∈clausura-ε(q)) δ(r,a))` y `F' = {q | clausura-ε(q) ∩ F ≠ ∅}`. La normalización conserva Q, Σ e inicial, y deja un sistema sin arcos ε para aplicar las reglas de ecuaciones.

**RF-12. Sistema de ecuaciones.** Se construirá una variable Xq por estado q. Xq representará el lenguaje de las cadenas que llevan desde q a algún estado final. Se incluirá una ecuación por estado: las transiciones aportarán el símbolo multiplicado por la variable de destino; las alternativas se unirán con `+`; a la ecuación de un estado final se añadirá λ (cadena vacía). Las transiciones paralelas se conservarán como alternativas o se combinarán por unión.

**RF-13. Resolver y explicar.** Se resolverá el sistema con sustituciones y el Lema de Arden. Cuando una ecuación quede en forma X = A·X + B, se explicará la condición clásica ε ∉ L(A) y se transformará en X = A*·B. La aplicación registrará cada operación, la ecuación antes/después y el nombre de la regla aplicada. Si una simplificación requiere eliminar ε-transiciones, se mostrarán también ese paso y su justificación. El resultado pedido será la expresión asociada al estado inicial.

**RF-14. Reglas de simplificación.** La representación interna de la ER conservará operadores diferenciados (vacío, cadena vacía, símbolo, unión, concatenación y estrella). Como mínimo se aplicarán y etiquetarán estas simplificaciones:

- `R + ∅ = R`; `R + R = R`;
- `R·∅ = ∅` y `∅·R = ∅`;
- `R·λ = R` y `λ·R = R`;
- `∅* = λ`; `λ* = λ`; `(R*)* = R*`;
- agrupación de alternativas y eliminación de paréntesis redundantes solo cuando la precedencia lo permita.

La interfaz mostrará unión con `+`, concatenación explícita con `·`, estrella con `*`, lenguaje vacío con `∅` y cadena vacía con `λ`. La ER se imprimirá con paréntesis suficientes para que su precedencia sea inequívoca.

**RF-15. Casos sin aceptación.** Si no hay estados finales alcanzables desde el inicial, la expresión resultante será `∅`. Si el inicial es final, el resultado incluirá λ, además de las rutas adicionales que regresen a aceptación.

### 4.4 Verificador de equivalencia acotada

**RF-16. Longitud configurable.** El usuario elegirá n, con n ≥ 6. El valor n representa la longitud máxima inclusive. Se enumerarán todas las cadenas de Σ de longitud 0, 1, …, n, incluida ε.

**RF-17. Conteo y control de recursos.** Antes de ejecutar, el sistema mostrará el total previsto de cadenas, `Σ(i=0..n) |Σ|^i`. Si la configuración supera el límite de trabajo definido por la implementación, informará el conteo y permitirá reducir n o cancelar; no declarará que una comprobación parcial fue completa. El límite debe estar documentado y no alterará silenciosamente el valor solicitado.

**RF-18. Evaluación equivalente.** Cada cadena se evaluará directamente en el AFND (manteniendo conjuntos de estados y clausuras-ε), en el AFD (seguimiento determinista) y en la ER. La ER se compilará desde su árbol de operadores a un AFND de Thompson y se evaluará mediante simulación de estados; no se analizará el texto de presentación ni se dependerá de `eval` o de interpretar operadores de usuario como código.

**RF-19. Resultado.** La pantalla indicará cuántas cadenas fueron revisadas y si las tres representaciones coincidieron en todas. Si hay diferencias, listará cada cadena distinta y el resultado de aceptación de AFND, AFD y ER; ε se mostrará con notación legible. La comparación será exacta para el conjunto finito comprobado.

**RF-20. Límite de la comprobación.** La enumeración hasta n es una comprobación exhaustiva acotada, no una demostración formal de equivalencia para cadenas de longitud arbitraria. La interfaz y el informe no presentarán el resultado acotado como una prueba matemática del lenguaje infinito.

### 4.5 Bonus: transiciones ε

**RF-21. Clausura-ε.** Cuando se habilite el bonus, el editor aceptará transiciones ε que no pertenezcan al alfabeto. La conversión tomará la clausura-ε del inicial, y en cada transición del método de subconjuntos calculará clausura-ε después de reunir los destinos. La aceptación directa del AFND también considerará la clausura antes, durante y después de consumir símbolos, según corresponda.

**RF-22. Presentación del bonus.** Las ε-transiciones se dibujarán y aparecerán identificadas como ε en la tabla de transiciones de entrada. No se crearán columnas ε en la tabla del AFD resultante, porque ε no es un símbolo de Σ.

## 5. Modelo de datos y formatos

### 5.1 Definición matemática

Un AFND de entrada se representa como M = (Q, Σ, δ, q0, F), donde Q es un conjunto finito y no vacío de estados, Σ es un alfabeto finito y no vacío, δ asigna a cada pareja (q,a) un conjunto de estados destino, q0 ∈ Q y F ⊆ Q. Con el bonus, δ acepta además la etiqueta ε, que no pertenece a Σ. Un AFD cumple que cada pareja estado-símbolo tiene un único destino; el AFD generado por el método de subconjuntos es completo respecto de los subconjuntos alcanzables, creando ∅ cuando alguna transición calculada no tiene destino.

### 5.2 JSON de intercambio

Los nombres de propiedades son fijos y el archivo se codifica en UTF-8. Las transiciones se guardan como una lista de aristas; varias filas con el mismo origen y símbolo expresan no determinismo. La etiqueta `ε` se reserva para las transiciones vacías y se omite de `alfabeto`.

```json
{
  "version": 1,
  "tipo": "AFND",
  "estados": ["q0", "q1", "q2"],
  "alfabeto": ["a", "b"],
  "inicial": "q0",
  "finales": ["q2"],
  "transiciones": [
    {"desde": "q0", "simbolo": "a", "hacia": "q0"},
    {"desde": "q0", "simbolo": "a", "hacia": "q1"},
    {"desde": "q1", "simbolo": "b", "hacia": "q2"}
  ]
}
```

`tipo` será `AFND` o `AFD`. El importador validará la versión y todas las referencias antes de aceptar el archivo. Si `tipo` es `AFD`, rechazará símbolos con más de un destino desde el mismo estado. Al exportar el AFD convertido, sus estados-subconjunto tendrán identificadores estables serializables (por ejemplo `S0`, `S1`) y el archivo incluirá un campo `etiquetas_estados` que asocie cada identificador con el conjunto original. La interfaz seguirá mostrando la notación matemática del conjunto.

### 5.3 Resultados internos

- **AFD:** conjunto de subconjuntos alcanzables, estado inicial, finales y tabla total de transiciones para Σ.
- **Traza de conversión:** secuencia ordenada de eventos por cada par subconjunto-símbolo, con cálculo y destino.
- **ER:** árbol de operadores tipados; el texto mostrado es una serialización de dicho árbol, no su fuente semántica.
- **Traza de ecuaciones:** lista de sistemas antes y después de cada sustitución/simplificación, con regla y explicación.
- **Verificación:** n, cantidad esperada y evaluada, y lista de discrepancias con sus tres valores booleanos.

Los resultados se derivarán del modelo validado. Editar el autómata después de calcular invalidará los resultados anteriores y la interfaz solicitará recalcularlos.

## 6. Casos límite y comportamiento esperado

| Caso | Comportamiento requerido |
|---|---|
| Destino vacío para un símbolo | Crear/usar ∅; mostrar bucle de ∅ para cada símbolo. |
| ∅ no es alcanzable | No añadirlo al AFD alcanzable. |
| Estado del AFND inalcanzable | Conservarlo en la entrada/grafo; excluirlo de los subconjuntos alcanzables desde el inicial. En Módulo 2 puede omitirse tras mostrar la razón. |
| Alfabeto de un símbolo | Crear una columna y enumerar cadenas correctamente, incluidas las de longitud cero. |
| Ningún estado final | Todas las cadenas se rechazan y la ER es ∅. |
| Estado inicial final | ε se acepta; la ER resultante incluye λ. |
| Estado sin transiciones | Aceptarlo como entrada; si no es final, no acepta desde ese estado; sus transiciones de AFD llevan a ∅. |
| Transiciones duplicadas | Normalizarlas como una sola arista sin cambiar el lenguaje. |
| AFND con varios destinos | Conservar el conjunto de destinos y unirlos en la conversión. |
| ε en el alfabeto | Rechazarlo; ε solo puede ser etiqueta de transición cuando el bonus está activo. |
| n menor que 6 | Rechazarlo con mensaje que indique el mínimo requerido. |
| Estado, símbolo o destino desconocido en JSON | Rechazar la importación sin alterar el documento abierto y señalar el dato inválido. |
| Subconjunto AFD final | Marcarlo final si contiene al menos un final del AFND. |
| ER con muchas alternativas | Mantener precedencia y paréntesis para preservar el significado. |

## 7. Requisitos no funcionales y restricciones

**RNF-01. Offline:** toda funcionalidad estará disponible sin conexión. No se utilizarán recursos alojados externamente.

**RNF-02. Plataforma:** Python 3 y Tkinter; no se combinará con HTML/JavaScript ni se iniciará un servidor. Se preferirá la biblioteca estándar.

**RNF-03. Ejecución:** el proyecto debe poder iniciarse localmente con `python app.py`, según la estructura final acordada en Fase 1.

**RNF-04. Claridad:** el usuario podrá distinguir entradas, resultados calculados, estados finales, estado inicial, ∅, λ y ε. Los errores describirán cómo corregir la entrada.

**RNF-05. Trazabilidad:** las conversiones y las sustituciones deberán ser reproducibles con el mismo orden de estados y transiciones. La aplicación expondrá los cálculos relevantes para que cualquiera de los dos integrantes pueda explicarlos.

**RNF-06. Separación lógica/interfaz:** el modelo y los algoritmos deberán poder ejecutarse independientemente de Tkinter; la interfaz los invocará y presentará sus resultados.

**RNF-07. Rendimiento controlado:** el conteo de cadenas se calculará antes de la verificación; la interfaz mantendrá visible el estado de una operación larga y ofrecerá cancelación segura si el diseño de implementación lo permite.

## 8. Criterios de aceptación

La Fase 0 se considera especificada cuando las decisiones anteriores están documentadas. Para las fases posteriores, el producto debe satisfacer, como mínimo:

1. Resolver el caso AFND→AFD del Anexo A de la guía: inicial `{q0}`, destinos `{q0,q1}`, `{q2}` y `∅` donde corresponda, incluyendo los bucles de ∅.
2. Resolver el caso AF→ER del Anexo A y presentar una expresión equivalente a `x(xy*y)*` (o equivalente algebraicamente), con su sistema de ecuaciones y reglas visibles.
3. Permitir inspeccionar el grafo, la tabla de conversión y una traza individual paso a paso.
4. Para n = 6 o superior, comparar las tres representaciones para todas las cadenas de longitud 0..n y reportar cualquier diferencia.
5. Admitir un alfabeto con un único símbolo y manejar correctamente los estados inalcanzables y el estado pozo.
6. Si se entrega el bonus, demostrar clausuras-ε en el inicial y en los conjuntos alcanzados, sin incluir ε como columna del AFD.
7. Abrir y operar sin internet mediante Python y Tkinter.

La comprobación del criterio 4 demuestra coincidencia solo en las cadenas enumeradas. La corrección general de los algoritmos deberá respaldarse además con revisión del procedimiento y pruebas independientes en la fase de lógica pura.

## 9. Supuestos de esta especificación

- La elección de stack es Python con Tkinter.
- Se adopta APA, séptima edición, para citas autor-fecha y referencias del documento; los nombres reales de los dos integrantes se añadirán en la portada/metadata final.
- Se incluye JSON para el intercambio de datos, además del editor gráfico.
- Las transiciones ε se describen como bonus opcional, no como requisito para aprobar los módulos obligatorios.
- El verificador aplica n como máximo inclusive y empieza por la cadena vacía.
- La fase 1 podrá concretar estructura de carpetas, límites de rendimiento y detalles visuales sin contradecir estos requisitos.

## Referencias

*Teoría de la computación: Parcial del segundo corte. Simulador gráfico de autómatas: de AFND a AFD y de AF a expresión regular* [Guía del parcial]. (s. f.). Documento PDF proporcionado para la actividad.

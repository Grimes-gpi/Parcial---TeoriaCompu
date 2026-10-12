# Simulador de autómatas

Aplicación por consola para estudiar la conversión de un AFND a un AFD, obtener una expresión regular a partir de las ecuaciones de estados y comparar las tres representaciones sobre un conjunto finito de cadenas.

# Requisitos

- Python 3.10 o posterior.
- Tkinter 
- No requiere conexión a internet ni librerías externas.

# Ejecución

Abra una terminal en esta carpeta y ejecute:

```text
python app.py
```

# Funciones

1. Autómata: edita/valida la estructura JSON, abra o guarda autómatas y ve el grafo. Los estados pueden reubicarse moviendolos
2. AFND → AFD: aqui construye únicamente los subconjuntos alcanzables, muestra la tabla y el estado pozo cuando aparece, y presenta cada transición paso a paso. Podemos exportar en JSON
3. AF → ER: Esta arma una ecuación por estado, resuelve con sustitución y Lema de Arden, y muestra la expresión final y la hace toda
4. Verificador: Aqui enumera todas las cadenas desde longitud 0 hasta n inclusive (n mínimo 6) y compara AFND, AFD y ER. Informa todas las discrepancias que tenga

ε es soportado en la entrada del AFND. La conversión calcula clausuras-ε; para las ecuaciones, elimina ε-transiciones preservando el lenguaje.

# Formato del autómata

El archivo usa UTF-8 y la forma siguiente. Se permiten varios destinos repitiendo aristas con el mismo origen y símbolo. `ε` se admite como etiqueta de transición y nunca pertenece a `alfabeto`.

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

Los símbolos son caracteres individuales; el alfabeto puede contener uno solo. Los nombres de estado deben ser únicos y no vacíos. La validación de la interfaz indica campos y transiciones inválidos antes de calcular.

# Alcance del verificador

Para alfabeto de tamaño k y longitud máxima n se enumeran `1 + k + k² + … + kⁿ` para las cadenas. El límite de trabajo actual es 200 000 cadenas; si se supera, la aplicación informa el total y pide reducir n. 
# Módulos

- `app.py`: interfaz Tkinter, editor JSON, grafos y resultados.
- `logic.py`: modelo, validaciones, clausura-ε, construcción por subconjuntos, ecuaciones/ER y verificación.
- `ejemplo_afnd.json`: caso de referencia de AFND→AFD.
- `SPEC.md`: especificación técnica de la Fase 0.
- `Bitacora_prompts.pdf`: registro de prompts propios de nosotros y estado de avance.



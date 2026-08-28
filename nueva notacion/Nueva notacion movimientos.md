OJO!! Esta no es la notacion que está implementada, es una nueva muy poarecida a la anterior, que voy a usar en otros proyectos

# Notación de movimientos para cubos NxN

## 1. Caras

Las caras se identifican mediante:

    U D F B L R

manteniendo la nomenclatura estándar de Rubik:

- `U` = **Up**
- `D` = **Down**
- `F` = **Front**
- `B` = **Back**
- `L` = **Left**
- `R` = **Right**

Una cara sin rango significa exclusivamente **su capa exterior**, es decir, la posición `1`.

Por tanto:

    F

es equivalente a seleccionar:

    F[1]

---

## 2. Convención geométrica

Todo movimiento se interpreta **mirando directamente la cara indicada de frente**.

Cada cara se considera una matriz en la que:

- Las filas se numeran de arriba hacia abajo.
- Las columnas se numeran de izquierda a derecha.
- La primera fila/columna es `1`.

La orientación de las caras es fija:

- `F`, `B`, `L`, `R`: `U` queda arriba y `D` queda abajo.
- `U`, `D`: `L` queda a la izquierda y `R` queda a la derecha.

Por lo tanto, las direcciones `u`, `d`, `l`, `r` siempre significan literalmente **up, down, left, right desde el punto de vista de la cara indicada**.

---

## 3. Estructura general

Un movimiento puede escribirse como:

    FACE [RANGE] MOVEMENT [MULTIPLIER]

donde:

- `FACE` identifica la cara desde la que se describe el movimiento.
- `[RANGE]` es opcional y selecciona filas, columnas o capas.
- `MOVEMENT` indica la dirección.
- `MULTIPLIER` permite repetir el movimiento.

Los espacios separan movimientos consecutivos.

Ejemplo:

    R U R' U'

---

## 4. Rangos

Los rangos se escriben obligatoriamente entre corchetes:

    [...]

Esto permite distinguir inequívocamente una coordenada de un movimiento.

Hay cinco formas básicas:

    [n]       una posición
    [n:m]     desde n hasta m
    [:m]      desde 1 hasta m
    [n:]      desde n hasta N
    [:]       desde 1 hasta N

Los extremos son inclusivos.

Ejemplos:

    F[2]

    F[2:5]

    F[:3]

    F[3:]

    F[:]

`[3:]` es una abreviatura de `[3:B]`, mientras que `[:3]` es una abreviatura de `[T:3]`.

No es necesario utilizar las abreviaturas: las formas explícitas también son válidas.

El orden de los extremos de un rango es indistinto:

    F[2:5]
    F[5:2]

son equivalentes.

---

## 5. Coordenadas

Las coordenadas pueden ser números o expresiones numéricas.

### Coordenadas simbólicas

Se utilizan letras que ayudan a recordar qué posición representan:

    T = Top    = 1       primera posición
    t = top    = 2       segunda posición

    B = Bottom = N       última posición
    b = bottom = N-1     penúltima posición

    c = center  inferior
    C = Center  superior

En cubos impares:

    c = C

En cubos pares:

    c = N/2
    C = N/2 + 1

También pueden utilizarse las coordenadas laterales:

    L = Left
    l = left

    R = Right
    r = right

En todos los casos, las letras tienen el significado de coordenada cuando aparecen dentro de `[...]`.

Por ejemplo:

    F[T:b]

    F[t:C]

    F[L:R]

### Expresiones

Las coordenadas pueden formar expresiones:

    T+1
    B-2
    c+1
    C-1

y, cuando el movimiento forma parte de un método parametrizado, pueden utilizarse las variables:

    i
    j
    k

Por ejemplo:

    F[T+i:B-k]

---

## 6. Direcciones

Hay seis direcciones posibles:

    u d l r c a

Las cuatro primeras indican desplazamientos lineales:

    u = up
    d = down
    l = left
    r = right

Las dos últimas indican rotaciones:

    c = clockwise
    a = anticlockwise

La dirección también determina qué tipo de selección representa el rango.

### `u` / `d` → filas

El rango representa filas de la cara indicada.

Ejemplo:

    F[2:3]d

Significa:

> Tomar las filas 2 y 3 de F y moverlas hacia abajo.

### `l` / `r` → columnas

El rango representa columnas de la cara indicada.

Ejemplo:

    F[2:3]r

Significa:

> Tomar las columnas 2 y 3 de F y moverlas hacia la derecha.

### `c` / `a` → capas

El rango representa capas contadas desde la cara indicada.

Ejemplo:

    F[2:3]c

Significa:

> Tomar las capas 2 y 3 desde F y rotarlas en sentido horario.

---

## 7. Compatibilidad con la notación estándar

Los movimientos clásicos de la notación de Rubik siguen siendo válidos como abreviaturas.

Por ejemplo:

    F
    F'
    F2

pueden interpretarse como:

    F[1]c
    F[1]a
    F[1]c2

respectivamente.

Lo mismo aplica a:

    U D F B L R

Por lo tanto, un algoritmo estándar como:

    R U R' U'

puede seguir escribiéndose exactamente así.

---

## 8. Multiplicadores

El multiplicador aparece **después de la dirección**.

Puede ser:

    2
    '

o puede omitirse.

### Sin multiplicador

    F[2:3]d

equivale a ejecutar el movimiento una vez.

### Multiplicador `2`

    F[2:3]d2

ejecuta el movimiento dos veces.

### Apóstrofe `'`

    F[2:3]d'

equivale a ejecutar el movimiento una vez en la dirección contraria.

El apóstrofe se conserva también por compatibilidad con la notación tradicional.

### Dirección en mayúscula

Una dirección escrita en mayúscula es una abreviatura de dos ejecuciones:

    d2 = D
    r2 = R
    c2 = C
    a2 = A
    u2 = U
    l2 = L

cuando aparece en la posición sintáctica de una dirección.

Por ejemplo:

    F[2:3]D

equivale a:

    F[2:3]d2

Las letras mayúsculas pueden tener otros significados cuando aparecen en otros contextos. Por ejemplo:

    F

es una cara, mientras que:

    F[2:3]D

contiene `D` como dirección duplicada. El contexto sintáctico elimina la ambigüedad.

---

## 9. Restricciones geométricas

No toda combinación de cara, rango y dirección es geométricamente válida.

La dirección determina qué representa el rango:

    u / d  → filas
    l / r  → columnas
    c / a  → capas

Por ejemplo:

    F[2:3]d

selecciona filas.

Mientras que:

    F[2:3]r

selecciona columnas.

Y:

    F[2:3]c

selecciona capas.

La sintaxis permite distinguir perfectamente estos tres casos; la validez concreta de una combinación es una cuestión geométrica.

---

## 10. Ausencia de rango

Una cara sin `[...]` representa únicamente su capa exterior:

    F = F[1]
    R = R[1]
    U = U[1]
    ...

En los movimientos de rotación estándar:

    F  = F[1]c
    F' = F[1]a
    F2 = F[1]c2

Los movimientos lineales `u`, `d`, `l`, `r` requieren una selección cuyo tipo permita determinar las filas o columnas involucradas.

---

## 11. Representaciones equivalentes

Un mismo movimiento físico puede tener varias representaciones equivalentes.

Por ejemplo, un movimiento que resulta incómodo de expresar desde `B` puede escribirse desde `F` si ambas expresiones producen exactamente la misma transformación.

No existe obligación de utilizar una representación canónica.

La notación está pensada para favorecer:

1. Facilidad de ejecución.
2. Facilidad de memorización.
3. Claridad del algoritmo.

No necesariamente la representación más corta.

---

## 12. Movimientos estándar adicionales

Se pueden conservar las convenciones conocidas:

    M E S
    x y z

como abreviaturas convenientes.

No forman parte de la sintaxis fundamental: son aliases de movimientos que pueden expresarse mediante la notación general.

Esto permite utilizar algoritmos publicados con notación tradicional sin renunciar a la expresividad de la notación NxN.

---


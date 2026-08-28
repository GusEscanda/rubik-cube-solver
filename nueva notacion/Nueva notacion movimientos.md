OJO!! Esta no es la notacion que está implementada, es una nueva muy poarecida a la anterior, que voy a usar en otros proyectos

# Notación de movimientos para cubos NxN

## 1. Conceptos básicos

La notación está diseñada para describir movimientos de cubos de cualquier tamaño `N×N×N`.

`N` representa el tamaño del cubo.

Por ejemplo:

- En un 3×3: `N = 3`
- En un 5×5: `N = 5`
- En un 13×13: `N = 13`

Las posiciones de filas, columnas y capas se numeran desde `1` hasta `N`.

---

## 2. Caras

Las caras se identifican mediante:

    U D F B L R

siguiendo la nomenclatura estándar de Rubik:

    U = Up
    D = Down
    F = Front
    B = Back
    L = Left
    R = Right

Una cara sin rango representa exclusivamente su capa exterior.

Por ejemplo:

    F

representa la capa exterior de la cara F y es equivalente a seleccionar la posición `1` desde F:

    F[1]

---

## 3. Convención geométrica

Todo movimiento se interpreta **mirando directamente la cara indicada de frente**.

Cada cara se considera una matriz en la que:

- Las filas se numeran de arriba hacia abajo.
- Las columnas se numeran de izquierda a derecha.
- La primera fila y la primera columna son la posición `1`.

### Orientación de las caras

Para `F`, `B`, `L` y `R`:

- `U` queda arriba.
- `D` queda abajo.

Para `U` y `D`:

- `L` queda a la izquierda.
- `R` queda a la derecha.

Esta orientación se mantiene independientemente de la cara que se esté observando.

Por lo tanto, las direcciones `u`, `d`, `l` y `r` siempre se interpretan desde el punto de vista del observador situado frente a la cara indicada.

---

## 4. Estructura general de un movimiento

La forma general es:

    FACE [RANGE] MOVEMENT [MULTIPLIER]

donde:

- `FACE` identifica la cara desde la que se describe el movimiento.
- `[RANGE]` es opcional y determina las posiciones afectadas.
- `MOVEMENT` determina cómo se mueven esas posiciones.
- `[MULTIPLIER]` es opcional y permite repetir el movimiento.

Los espacios separan movimientos consecutivos.

Por ejemplo:

    R U R' U'

representa cuatro movimientos consecutivos.

---

## 5. Rangos

Cuando se especifica un rango, este se escribe obligatoriamente entre corchetes:

    [...]

Los corchetes permiten distinguir claramente un rango de cualquier otro elemento de la notación.

Existen cinco formas básicas:

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

Las formas abreviadas son equivalentes a:

    [:3]  = [1:3]
    [3:]  = [3:N]
    [:]   = [1:N]

También pueden utilizarse las formas explícitas:

    [T:3]
    [3:B]

No se prohíbe ninguna de las dos formas; las abreviaturas simplemente permiten una escritura más compacta.

El orden de los extremos es indistinto:

    F[2:5]
    F[5:2]

son equivalentes.

---

## 6. Coordenadas

Las coordenadas pueden ser números o expresiones numéricas.

### Coordenadas simbólicas

Se utilizan letras que permiten recordar fácilmente su significado:

    T = Top     = 1
    t = top     = 2

    B = Bottom  = N
    b = bottom  = N-1

    L = Left    = 1
    l = left    = 2

    R = Right   = N
    r = right   = N-1

    c = center inferior
    C = Center superior

Las coordenadas `c` y `C` representan las posiciones centrales:

- En cubos impares, `c` y `C` son equivalentes.
- En cubos pares:

      c = N/2
      C = N/2 + 1

Las letras utilizadas como coordenadas tienen este significado **cuando aparecen dentro de un rango `[...]`**.

Por ejemplo:

    F[T:B]

    F[t:C]

    F[L:R]

### Expresiones

Las coordenadas pueden utilizarse dentro de expresiones numéricas:

    T+1
    B-2
    c+1
    C-1

También pueden utilizarse las variables `i`, `j` y `k` cuando el movimiento forma parte de un método parametrizado.

Por ejemplo:

    F[T+i:B-k]

---

## 7. Direcciones

Existen seis direcciones:

    u d l r c a

Las cuatro primeras representan desplazamientos lineales:

    u = up
    d = down
    l = left
    r = right

Las dos últimas representan rotaciones:

    c = clockwise
    a = anticlockwise

La dirección determina además qué representa el rango seleccionado.

### `u` / `d`: columnas

Cuando la dirección es `u` o `d`, el rango representa columnas de la cara indicada.

Por ejemplo:

    F[2:3]d

significa:

> Tomar las columnas 2 y 3 de F y moverlas hacia abajo.

### `l` / `r`: filas

Cuando la dirección es `l` o `r`, el rango representa filas de la cara indicada.

Por ejemplo:

    F[2:3]r

significa:

> Tomar las filas 2 y 3 de F y moverlas hacia la derecha.

### `c` / `a`: capas

Cuando la dirección es `c` o `a`, el rango representa capas contadas desde la cara indicada.

Por ejemplo:

    F[2:3]c

significa:

> Tomar las capas 2 y 3 desde F y rotarlas en sentido horario.

---

## 8. Multiplicadores

El multiplicador aparece después de la dirección.

Puede ser:

    2
    '

o puede omitirse.

### Sin multiplicador

    F[2:3]d

significa ejecutar el movimiento una vez.

### Multiplicador `2`

    F[2:3]d2

significa ejecutar el movimiento dos veces.

### Apóstrofe `'`

    F[2:3]d'

significa ejecutar el movimiento una vez en la dirección contraria.

El apóstrofe se conserva también por compatibilidad con la notación estándar de Rubik.

### Dirección en mayúscula

Una dirección escrita en mayúscula es una abreviatura de dos ejecuciones de esa dirección:

    u2 = U
    d2 = D
    l2 = L
    r2 = R
    c2 = C
    a2 = A

cuando la letra aparece en la posición sintáctica correspondiente a una dirección.

Por ejemplo:

    F[2:3]D

es equivalente a:

    F[2:3]d2

Esta abreviatura no cambia el significado de las letras cuando aparecen en otros contextos.

Por ejemplo:

    F

es una cara, mientras que en:

    F[2:3]D

la `D` funciona como dirección `d` ejecutada dos veces.

---

## 9. Compatibilidad con la notación estándar

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

puede escribirse exactamente de la misma manera.

---

## 10. Restricciones geométricas

No toda combinación de cara, rango y dirección representa un movimiento geométricamente válido.

La dirección determina el tipo de selección:

    u / d  → filas
    l / r  → columnas
    c / a  → capas

Por ejemplo:

    F[2:3]d

selecciona las filas 2 y 3.

Mientras que:

    F[2:3]r

selecciona las columnas 2 y 3.

Y:

    F[2:3]c

selecciona las capas 2 y 3 desde F.

Por lo tanto, `F[2:3]d` y `F[2:3]c` tienen sintaxis similar pero representan cosas geométricamente diferentes.

---

## 11. Ausencia de rango

Cuando no se especifica un rango, se selecciona únicamente la posición `1` de la cara indicada:

    F = F[1]
    R = R[1]
    U = U[1]
    D = D[1]
    B = B[1]
    L = L[1]

En particular, los movimientos de rotación estándar pueden expresarse como:

    F  = F[1]c
    F' = F[1]a
    F2 = F[1]c2

Los movimientos lineales `u`, `d`, `l` y `r` requieren una selección cuyo tipo permita determinar las filas o columnas involucradas.

---

## 12. Representaciones equivalentes

Un mismo movimiento físico puede tener diferentes representaciones válidas.

La notación no requiere una representación canónica única.

Por ejemplo, un movimiento que resulte incómodo de describir desde `B` puede expresarse desde `F` si ambas expresiones producen exactamente la misma transformación.

La representación puede elegirse buscando:

1. Facilidad de ejecución.
2. Facilidad de memorización.
3. Claridad del algoritmo.
4. Similitud con otros movimientos del mismo algoritmo.

Por lo tanto, la representación más corta no necesariamente es la mejor.

---

## 13. Movimientos estándar adicionales

Se pueden conservar las convenciones habituales:

    M E S
    x y z

como abreviaturas convenientes.

No forman parte de la sintaxis fundamental de la notación.

La sintaxis general es suficientemente expresiva como para representar los movimientos que estas abreviaturas describen.

Esto permite utilizar algoritmos publicados con notación tradicional sin renunciar a la expresividad necesaria para cubos NxN.

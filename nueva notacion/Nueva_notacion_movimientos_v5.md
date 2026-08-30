OJO!! Esta no es la notación que está implementada, es una nueva muy parecida a la anterior, que voy a usar en otros proyectos

# Notación de movimientos para cubos NxN

## 1. Caras

Las caras se identifican siguiendo la nomenclatura estándar de Rubik (`U, D, F, B, L, R`):

    [U]p, [D]own, [F]ront, [B]ack, [L]eft, [R]ight

---

## 2. Convención geométrica

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

Por lo tanto, las direcciones arriba, abajo, derecha, izquierda, sentido horario y antihorario, siempre se interpretan desde el punto de vista del observador situado frente a la cara indicada.

---

## 3. Estructura general de un movimiento

La forma general es:

    FACE [RANGE] [MOVEMENT] [MULTIPLIER]

donde:

- `FACE` identifica la cara desde la que se describe el movimiento.
- `[RANGE]` determina las posiciones afectadas. Si se omite, se utiliza `[1]`.
- `[MOVEMENT]` determina cómo se mueven esas posiciones. Si se omite, se utiliza `c` (clockwise).
- `[MULTIPLIER]` permite repetir el movimiento.

Por lo tanto:

    F

es equivalente a:

    F[1]c

Los espacios separan movimientos consecutivos.

Por ejemplo:

    R U R' U'

representa cuatro movimientos consecutivos.

---

## 4. Rangos

Cuando se especifica un rango, este se escribe obligatoriamente entre corchetes:

    [...]

Existen cinco formas básicas (`N` = tamaño del cubo):

    [n:m]     desde n hasta m
    [n]       una sola posición, equivalente a [n:n]
    [:m]      desde 1 hasta m
    [n:]      desde n hasta N
    [:]       desde 1 hasta N

Los extremos son inclusivos.

Ejemplos:

    F[2], F[2:5], F[:3], F[3:], F[:]

El orden de los extremos es indistinto:

    F[2:5] = F[5:2]

---

## 5. Coordenadas

Las coordenadas pueden ser números o expresiones numéricas.

Las coordenadas siempre se interpretan respecto de la orientación de la `FACE` indicada, independientemente de la dirección del movimiento.

Por ejemplo, en:

    F[2:4]d

las posiciones `2:4` se determinan mirando directamente la cara `F`, aunque el movimiento sea hacia abajo.

Una coordenada también puede ser negativa, y en ese caso se empieza a contar por el otro extremo, por ejemplo:

    1 = primera posición, -1 = última posición
    2 = segunda posición, -2 = penúltima posición
    3 = tercera posición, -3 = tercera contando desde el otro extremo

    ...

    `N` = última posición, -`N` = primera posición

### Coordenadas simbólicas

Se utilizan letras que permiten recordar fácilmente su significado:

    T = Top     = 1
    t = top     = 2

    B = Bottom  = -1
    b = bottom  = -2

    L = Left    = 1
    l = left    = 2

    R = Right   = -1
    r = right   = -2

    c = center inferior
    C = Center superior

Las coordenadas `c` y `C` representan las posiciones centrales:

- En cubos con `N` impar, `c` y `C` son equivalentes.
- En cubos con `N` par:

      c = N/2
      C = N/2 + 1

Las letras utilizadas como coordenadas tienen este significado **cuando aparecen dentro de un rango `[...]`**.

Por ejemplo:

    F[T:B], F[t:C], F[L:R]

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

## 6. Direcciones

Existen seis direcciones (`u`, `d`, `l`, `r`, `c`, `a`):

Las cuatro primeras representan desplazamientos lineales:

    [u]p, [d]own, [l]eft, [r]ight

Las dos últimas representan rotaciones:

    [c]lockwise, [a]nticlockwise

La dirección determina tanto **qué tipo de elemento representa el rango** como **hacia dónde se mueve**.

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

Por lo tanto:

    u / d  → columnas → up / down
    l / r  → filas    → left / right
    c / a  → capas    → clockwise / anticlockwise

No existen combinaciones geométricamente inválidas de cara, rango y dirección: cualquier cara, cualquier rango y cualquier dirección pueden combinarse libremente.

---

## 7. Multiplicadores

El multiplicador aparece después de la dirección:

    (nada)   ejecuta el movimiento una vez
    2        ejecuta el movimiento dos veces
    '        ejecuta el movimiento una vez en la dirección contraria

Por ejemplo:

    F[2:3]d    F[2:3]d2    F[2:3]d'

El apóstrofe se conserva por compatibilidad con la notación estándar de Rubik.

---

## 8. Compatibilidad con la notación estándar

Los defaults para rangos, direcciones y multiplicadores son tales que la notación clásica de Rubik sigue siendo válida.

Por ejemplo:

    F = F[1]c
    F' = F[1]a
    F2 = F[1]c2

Por lo tanto, un algoritmo estándar como:

    R U R' U'

puede escribirse exactamente de la misma manera.

---

## 9. Representaciones equivalentes

Una característica importante de esta notación es que **un mismo movimiento físico puede tener diferentes representaciones válidas**.

La notación no requiere una representación canónica única. Una transformación puede describirse desde diferentes caras o utilizando diferentes tipos de dirección, siempre que las expresiones produzcan exactamente la misma transformación.

Por ejemplo:

    F[2]d = L[2]c

representan exactamente el mismo giro físico.

La primera expresión lo describe como:

> columna 2 de F hacia abajo.

La segunda como:

> capa 2 desde L en sentido horario.

Esto permite elegir la representación más conveniente para cada situación. La elección puede buscar:

1. Facilidad de ejecución.
2. Facilidad de memorización.
3. Claridad del algoritmo.
4. Similitud con otros movimientos del mismo algoritmo.

Por lo tanto, **la representación más corta no necesariamente es la mejor**.

---

## 10. Movimientos estándar adicionales

Se pueden conservar las convenciones habituales:

    M E S
    x y z

como abreviaturas convenientes, también expresables mediante la sintaxis general.

### M, E, S

Estos movimientos están definidos únicamente para cubos de lado mayor o igual a 3.

Por convención, M sigue la dirección de L, E la de D, y S la de F:

    M = L[t:b]c = F[l:r]d
    E = D[t:b]c = F[t:b]r
    S = F[t:b]c = L[l:r]u = U[t:b]r

`[t:b]` / `[l:r]` selecciona todas las capas interiores, excluyendo las dos caras exteriores.

### x, y, z

    x = R[:]c = F[:]u
    y = U[:]c = F[:]l
    z = F[:]c = U[:]r

`[:]` toma todas las capas, por lo que estos movimientos rotan el cubo completo.

Los movimientos estándar pueden utilizarse directamente o reemplazarse por sus equivalentes cuando resulte más conveniente para leer o memorizar un algoritmo.

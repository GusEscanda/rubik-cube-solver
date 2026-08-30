# Cheat Sheet — Notación de movimientos NxN

**Formato:** `FACE[RANGE]MOVEMENT[MULTIPLIER]`
Defaults: sin rango → `[1]` · sin movimiento → `c` → por lo tanto `F` = `F[1]c`

## Caras
`U`p · `D`own · `F`ront · `B`ack · `L`eft · `R`ight

## Convención geométrica
- `F`, `B`, `L`, `R`: se miran con `U` arriba, `D` abajo
- `U`, `D`: se miran con `L` a la izquierda, `R` a la derecha

Es una convención (no la única posible). Las direcciones arriba, abajo, derecha, izquierda, sentido horario y antihorario, siempre se interpretan desde el punto de vista del observador situado frente a la cara indicada.

## Rangos
| Forma | Significa |
|---|---|
| `[n]` | posición n |
| `[n:m]` | de n a m (orden indistinto) |
| `[:m]` | de 1 a m |
| `[n:]` | de n a N |
| `[:]` | todo (1 a N) |

Negativos: `-1`=última · `-2`=penúltima · ... · `-N`=primera

## Coordenadas simbólicas
| | Valor | | Valor |
|---|---|---|---|
| `T` | 1 | `B` | -1 (=N) |
| `t` | 2 | `b` | -2 (=N-1) |
| `L` | 1 | `R` | -1 (=N) |
| `l` | 2 | `r` | -2 (=N-1) |
| `c` | N/2 | `C` | N/2+1 |

(en N impar, `c`=`C`)

⚠️ `F[2]u` y `F[2]d` son la misma columna — la dirección no cambia la numeración, solo hacia dónde se mueve.

## Direcciones
| Dir | Rango = | Mueve hacia |
|---|---|---|
| `u` / `d` | columnas | arriba / abajo |
| `l` / `r` | filas | izquierda / derecha |
| `c` / `a` | capas | horario / antihorario |

## Multiplicador
`(nada)` = 1 vez · `2` = 2 veces · `'` = invertido

## Representaciones equivalentes
Un mismo giro físico puede escribirse de varias formas — no hay forma canónica.
Ej: `F[2]d` = `L[2]c`

## M, E, S, x, y, z
(M/E/S solo definidos para N ≥ 3)

| | Definición | Forma amigable |
|---|---|---|
| `M` | `L[t:b]c` | `F[l:r]d` |
| `E` | `D[t:b]c` | `F[t:b]r` |
| `S` | `F[t:b]c` | `U[t:b]r` |
| `x` | `R[:]c` | `F[:]u` |
| `y` | `U[:]c` | `F[:]l` |
| `z` | `F[:]c` | `U[:]r` |

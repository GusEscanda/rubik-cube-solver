# CHEAT SHEET

## Caras

    U = Up
    D = Down
    F = Front
    B = Back
    L = Left
    R = Right

## Rangos

    [n]       una posición
    [n:m]     n hasta m
    [:m]      1 hasta m
    [n:]      n hasta N
    [:]       1 hasta N

## Coordenadas

    T = Top     = 1
    t = top     = 2

    B = Bottom  = N
    b = bottom  = N-1

    c = center inferior
    C = Center superior

    L = Left
    l = left

    R = Right
    r = right

    También:
    T+1   B-2   c+1   C-1   i   j   k

## Direcciones

    u = up
    d = down
    l = left
    r = right

    c = clockwise
    a = anticlockwise

    u / d → filas
    l / r → columnas
    c / a → capas

## Multiplicadores

    nada  = ×1
    2     = ×2
    '     = ×(-1)

    Dirección MAYÚSCULA = ×2

    d2 = D
    r2 = R
    c2 = C
    a2 = A
    u2 = U
    l2 = L

## Ejemplos

    F
    F'
    F2

    F[2]d
    F[2:3]d
    F[:3]d
    F[3:]r
    F[:]

    F[2:3]r
    F[2:3]c
    F[2:3]a
    F[2:3]D

    F[T+i:B-k]d

## Forma general

    FACE [RANGE] MOVEMENT [MULTIPLIER]

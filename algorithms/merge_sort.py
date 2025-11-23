def merge_sort(data, key_func):
    """
    Implementación manual de Merge Sort (Divide y Vencerás).
    :param data: Lista de diccionarios a ordenar.
    :param key_func: Función lambda para saber por qué campo ordenar (ej: fecha).
    :return: Lista ordenada.
    """
    # Caso base: si la lista tiene 0 o 1 elemento, ya está ordenada
    if len(data) <= 1:
        return data

    # DIVIDE: Encontramos el punto medio
    mid = len(data) // 2
    left_half = data[:mid]
    right_half = data[mid:]

    # VENCERÁS (Recursividad): Ordenamos cada mitad
    left_sorted = merge_sort(left_half, key_func)
    right_sorted = merge_sort(right_half, key_func)

    # COMBINAR: Mezclamos las dos mitades ordenadas
    return merge(left_sorted, right_sorted, key_func)

def merge(left, right, key_func):
    sorted_list = []
    i = j = 0

    # Comparar elementos de ambas listas y agregar el menor
    while i < len(left) and j < len(right):
        # Usamos key_func para obtener el valor de comparación (ej: la fecha '2025-10-04')
        if key_func(left[i]) <= key_func(right[j]):
            sorted_list.append(left[i])
            i += 1
        else:
            sorted_list.append(right[j])
            j += 1

    # Agregar los elementos restantes (si quedaron)
    sorted_list.extend(left[i:])
    sorted_list.extend(right[j:])

    return sorted_list
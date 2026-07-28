/**
 * Ejecuta una tarea asíncrona sobre muchos elementos sin lanzarlos todos a la
 * vez.
 *
 * @param items Elementos que hay que procesar.
 * @param concurrency Número máximo de trabajadores simultáneos.
 * @param worker Función que procesa un elemento.
 * @returns Resultados en el mismo orden que `items`.
 *
 * Esto protege a la wiki de ráfagas enormes de peticiones y reduce bloqueos.
 */
export const runWithConcurrency = async <TItem, TResult>(
  items: TItem[],
  concurrency: number,
  worker: (
    item: TItem,
    index: number
  ) => Promise<TResult>
): Promise<TResult[]> => {
  if (concurrency < 1) {
    throw new Error('La concurrencia debe ser al menos 1')
  }

  if (items.length === 0) {
    return []
  }

  const results = new Array<TResult>(items.length)
  let nextIndex = 0

  /**
   * Cada trabajador toma el siguiente índice libre, ejecuta la tarea y repite
   * hasta que ya no quedan elementos.
   */
  const workers = Array.from(
    { length: Math.min(concurrency, items.length) },
    async () => {
      while (true) {
        const currentIndex = nextIndex
        nextIndex += 1

        if (currentIndex >= items.length) {
          return
        }

        results[currentIndex] = await worker(
          items[currentIndex]!,
          currentIndex
        )
      }
    }
  )

  await Promise.all(workers)

  return results
}

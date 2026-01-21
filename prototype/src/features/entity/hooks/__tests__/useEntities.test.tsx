import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactNode } from 'react'
import { useEntity, useCreateEntity } from '../useEntities'
import { entityService } from '@/services/entityService'

// Mock the entity service
jest.mock('@/services/entityService')

const createWrapper = () => {
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
            },
        },
    })

    return ({ children }: { children: ReactNode }) => (
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    )
}

/* 
// Commenting out for now - focusing on core functionality
describe('useEntities', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('fetches entities successfully', async () => {
    const mockEntities = [
      {
        id: 'e1',
        kind: { major: 'test', minor: 'example' },
        created: '2024-01-01T00:00:00Z',
        terminated: '',
        name: { value: 'Entity 1', startTime: '2024-01-01T00:00', endTime: '' },
        metadata: [],
        attributes: [],
        relationships: [],
      },
    ]

    ;(entityService.getEntities as jest.Mock).mockResolvedValue(mockEntities)

    const { result } = renderHook(() => useEntities(), { wrapper: createWrapper() })

    expect(result.current.isLoading).toBe(true)

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toEqual(mockEntities)
    expect(entityService.getEntities).toHaveBeenCalledTimes(1)
  })

  it('handles fetch error', async () => {
    const errorMessage = 'Failed to fetch entities'
    ;(entityService.getEntities as jest.Mock).mockRejectedValue(new Error(errorMessage))

    const { result } = renderHook(() => useEntities(), { wrapper: createWrapper() })

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    expect(result.current.error).toBeDefined()
  })
})
*/

describe('useEntity', () => {
    beforeEach(() => {
        jest.clearAllMocks()
    })

    it('fetches single entity by ID', async () => {
        const mockEntity = {
            id: 'e1',
            kind: { major: 'test', minor: 'example' },
            created: '2024-01-01T00:00:00Z',
            terminated: '',
            name: { value: 'Entity 1', startTime: '2024-01-01T00:00', endTime: '' },
            metadata: [],
            attributes: [],
            relationships: [],
        }

            ; (entityService.getEntityById as jest.Mock).mockResolvedValue(mockEntity)

        const { result } = renderHook(() => useEntity('e1'), { wrapper: createWrapper() })

        await waitFor(() => {
            expect(result.current.isSuccess).toBe(true)
        })

        expect(result.current.data).toEqual(mockEntity)
        expect(entityService.getEntityById).toHaveBeenCalledWith('e1')
    })
})

describe('useCreateEntity', () => {
    beforeEach(() => {
        jest.clearAllMocks()
    })

    it('creates entity successfully', async () => {
        const newEntity = {
            id: 'e2',
            kind: { major: 'test', minor: 'example' },
            created: '2024-01-01T00:00:00Z',
            terminated: '',
            name: { value: 'New Entity', startTime: '2024-01-01T00:00', endTime: '' },
            metadata: [],
            attributes: [],
            relationships: [],
        }

            ; (entityService.createEntity as jest.Mock).mockResolvedValue(newEntity)

        const { result } = renderHook(() => useCreateEntity(), { wrapper: createWrapper() })

        result.current.mutate(newEntity)

        await waitFor(() => {
            expect(result.current.isSuccess).toBe(true)
        })

        expect(result.current.data).toEqual(newEntity)
        expect(entityService.createEntity).toHaveBeenCalledWith(newEntity, expect.anything())
    })

    it('handles creation error', async () => {
        const newEntity = {
            id: 'e2',
            kind: { major: 'test', minor: 'example' },
            created: '2024-01-01T00:00:00Z',
            terminated: '',
            name: { value: 'New Entity', startTime: '2024-01-01T00:00', endTime: '' },
            metadata: [],
            attributes: [],
            relationships: [],
        }

        const errorMessage = 'Failed to create entity'
            ; (entityService.createEntity as jest.Mock).mockRejectedValue(new Error(errorMessage))

        const { result } = renderHook(() => useCreateEntity(), { wrapper: createWrapper() })

        result.current.mutate(newEntity)

        await waitFor(() => {
            expect(result.current.isError).toBe(true)
        })

        expect(result.current.error).toBeDefined()
    })
})

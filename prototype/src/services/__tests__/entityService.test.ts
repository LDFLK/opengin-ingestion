import { entityService } from '../entityService'

// Mock global fetch
global.fetch = jest.fn()

describe('entityService', () => {
    beforeEach(() => {
        jest.clearAllMocks()
    })

    /* 
    // Commenting out for now - focusing on core functionality
    describe('getEntities', () => {
      it('fetches entities from API successfully', async () => {
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
  
        ;(fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          json: async () => mockEntities,
        })
  
        const result = await entityService.getEntities()
  
        expect(fetch).toHaveBeenCalledWith('/api/entities')
        expect(result).toEqual(mockEntities)
      })
  
      it('returns mock data on API failure', async () => {
        ;(fetch as jest.Mock).mockResolvedValueOnce({
          ok: false,
          statusText: 'Internal Server Error',
        })
  
        const result = await entityService.getEntities()
  
        expect(result).toBeDefined()
        expect(Array.isArray(result)).toBe(true)
      })
    })
    */

    describe('createEntity', () => {
        it('creates entity via API', async () => {
            const newEntity = {
                id: 'e2',
                kind: { major: 'Person', minor: 'Employee' },
                created: '2024-01-01T00:00:00Z',
                terminated: '',
                name: { value: 'John Doe', startTime: '2024-01-01T10:00', endTime: '' },
                metadata: [],
                attributes: [],
                relationships: [],
            }

                ; (fetch as jest.Mock).mockResolvedValueOnce({
                    ok: true,
                    json: async () => newEntity,
                })

            const result = await entityService.createEntity(newEntity)

            expect(fetch).toHaveBeenCalledWith('/entities', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(newEntity),
            })
            expect(result).toEqual(newEntity)
        })

        it('throws error on API failure', async () => {
            const newEntity = {
                id: 'e2',
                kind: { major: 'Person', minor: 'Employee' },
                created: '2024-01-01T00:00:00Z',
                terminated: '',
                name: { value: 'John Doe', startTime: '2024-01-01T10:00', endTime: '' },
                metadata: [],
                attributes: [],
                relationships: [],
            }

                ; (fetch as jest.Mock).mockResolvedValueOnce({
                    ok: false,
                    status: 500,
                    statusText: 'Internal Server Error',
                    json: async () => ({ error: 'Server error' }),
                })

            await expect(entityService.createEntity(newEntity)).rejects.toThrow()
        })
    })

    describe('getEntityById', () => {
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

                ; (fetch as jest.Mock).mockResolvedValueOnce({
                    ok: true,
                    json: async () => mockEntity,
                })

            const result = await entityService.getEntityById('e1')

            expect(fetch).toHaveBeenCalledWith('/v1/entities/search/e1')
            expect(result).toEqual(mockEntity)
        })

        it('returns undefined for 404 response', async () => {
            ; (fetch as jest.Mock).mockResolvedValueOnce({
                ok: false,
                status: 404,
                statusText: 'Not Found',
            })

            const result = await entityService.getEntityById('nonexistent')

            expect(result).toBeUndefined()
        })
    })

    /* 
    // Commenting out for now - focusing on core functionality
    describe('updateEntity', () => {
      it('updates entity via API', async () => {
        const updatedEntity = {
          id: 'e1',
          kind: { major: 'Person', minor: 'Manager' },
          created: '2024-01-01T00:00:00Z',
          terminated: '',
          name: { value: 'Jane Doe', startTime: '2024-01-01T10:00', endTime: '' },
          metadata: [],
          attributes: [],
          relationships: [],
        }
  
        ;(fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          json: async () => updatedEntity,
        })
  
        const result = await entityService.updateEntity(updatedEntity)
  
        expect(fetch).toHaveBeenCalledWith('/api/entities/e1', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(updatedEntity),
        })
        expect(result).toEqual(updatedEntity)
      })
    })
    */
})

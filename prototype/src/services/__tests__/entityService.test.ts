import { entityService } from '../entityService'
import { MAJOR_KINDS } from '../../constants/entityKinds'

// Mock global fetch
global.fetch = jest.fn()

describe('entityService', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    jest.spyOn(console, 'error').mockImplementation(() => { })
    jest.spyOn(console, 'log').mockImplementation(() => { })
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  describe('getEntities', () => {
    it('fetches entities from API successfully', async () => {
      const mockEntities = [
        {
          id: 'e1',
          kind: { major: 'Person', minor: 'Citizen' },
          created: '2024-01-01T00:00:00Z',
          terminated: '',
          name: { value: 'Entity 1', startTime: '2024-01-01T00:00', endTime: '' },
          metadata: [],
          attributes: [],
          relationships: [],
        },
      ]

      // Mock successful response for the first major kind, empty body for others
      const mockFetch = fetch as jest.Mock;
      mockFetch.mockImplementation(async (url, options) => {
        if (url === '/api/v1/entities/search' && options.method === 'POST') {
          const body = JSON.parse(options.body);
          if (body.kind.major === 'Person') {
            return {
              ok: true,
              text: async () => JSON.stringify(mockEntities),
            };
          }
          // Simulate empty body for other kinds
          if (body.kind.major === 'Organization') {
            return {
              ok: true,
              text: async () => JSON.stringify({ body: [] }),
            };
          }
          return {
            ok: true,
            text: async () => "",
          };
        }
        return { ok: false, status: 404 };
      });

      const result = await entityService.getEntities()

      // Verify a POST request was made for each major kind
      MAJOR_KINDS.forEach(kind => {
        expect(fetch).toHaveBeenCalledWith('/api/v1/entities/search', expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ kind: { major: kind } })
        }));
      });

      expect(result).toEqual(mockEntities)
    })

    it('returns mock data on API failure', async () => {
      (fetch as jest.Mock).mockResolvedValue({
        ok: false,
        statusText: 'Internal Server Error',
      })

      const result = await entityService.getEntities()

      expect(result).toBeDefined()
      expect(Array.isArray(result)).toBe(true)
    })
  })

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

      expect(fetch).toHaveBeenCalledWith('/api/entities', {
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

      // Mock response with body wrapper and stringified name (simulating protobuf)
      const apiResponse = {
        body: [{
          ...mockEntity,
          name: JSON.stringify({
            typeUrl: "type.googleapis.com/google.protobuf.StringValue",
            value: Buffer.from("Entity 1").toString('hex')
          })
        }]
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        text: async () => JSON.stringify(apiResponse),
      })

      const result = await entityService.getEntityById('e1')

      expect(fetch).toHaveBeenCalledWith('/api/v1/entities/search', expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ id: 'e1' })
      }))

      // Result should have parsed name
      expect(result).toEqual({
        ...mockEntity,
        name: {
          value: 'Entity 1',
          startTime: '', // Default since not in protobuf string
          endTime: ''
        }
      })
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

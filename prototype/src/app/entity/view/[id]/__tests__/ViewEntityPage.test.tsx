import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import ViewEntityPage from '../page'
import { useRouter } from 'next/navigation'
import { useEntity } from '@/features/entity/hooks/useEntities'

// Mock dependencies
jest.mock('next/navigation', () => ({
    useRouter: jest.fn(),
    useParams: jest.fn(),
}))

jest.mock('@/features/entity/hooks/useEntities', () => ({
    useEntity: jest.fn(),
}))

describe('ViewEntityPage', () => {
    const mockRouter = {
        push: jest.fn(),
        back: jest.fn(),
    }
    const mockParams = Promise.resolve({ id: 'e1' })

    beforeEach(() => {
        jest.clearAllMocks();
        (useRouter as jest.Mock).mockReturnValue(mockRouter);
    })

    it('renders entity details correctly', async () => {
        const mockEntity = {
            id: 'e1',
            kind: { major: 'TestMajor', minor: 'TestMinor' },
            name: { value: 'Test Entity', startTime: '2024-01-01T10:00:00Z' },
            created: '2024-01-01T10:00:00Z',
            terminated: '',
            metadata: [],
            attributes: [],
            relationships: [],
        };

        (useEntity as jest.Mock).mockReturnValue({
            data: mockEntity,
            isLoading: false,
        })

        // We need to await the component render if it was async, but here it's a client component using useEffect for params
        // However, we must wait for the state update
        render(<ViewEntityPage params={mockParams} />)

        expect(await screen.findByText('Entity Details')).toBeInTheDocument()
        expect(screen.getByText('Test Entity')).toBeInTheDocument()
        expect(screen.getByText('TestMajor')).toBeInTheDocument()
        expect(screen.getByText('TestMinor')).toBeInTheDocument()
        expect(screen.getByText('2024-01-01T10:00:00Z')).toBeInTheDocument()
    })

    it('navigates back when Back button is clicked', async () => {
        const mockEntity = {
            id: 'e1',
            kind: { major: 'TestMajor', minor: 'TestMinor' },
            name: { value: 'Test Entity' },
            created: '2024-01-01T10:00:00Z',
            metadata: [], attributes: [], relationships: []
        };
        (useEntity as jest.Mock).mockReturnValue({
            data: mockEntity,
            isLoading: false,
        })

        render(<ViewEntityPage params={mockParams} />)

        // Wait for render
        await screen.findByText('Entity Details')

        fireEvent.click(screen.getByRole('button', { name: /Back/i }))

        expect(mockRouter.back).toHaveBeenCalled()
    })

    it('navigates to edit page when Edit button is clicked', async () => {
        const mockEntity = {
            id: 'e1',
            kind: { major: 'TestMajor', minor: 'TestMinor' },
            name: { value: 'Test Entity' },
            created: '2024-01-01T10:00:00Z',
            metadata: [], attributes: [], relationships: []
        };
        (useEntity as jest.Mock).mockReturnValue({
            data: mockEntity,
            isLoading: false,
        })

        render(<ViewEntityPage params={mockParams} />)

        // Wait for render
        await screen.findByText('Entity Details')

        fireEvent.click(screen.getByRole('button', { name: /Edit/i }))

        expect(mockRouter.push).toHaveBeenCalledWith('/entity/update/e1')
    })
})

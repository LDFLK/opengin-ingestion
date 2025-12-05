import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import EntityPage from '../page'
import { useRouter } from 'next/navigation'
import { useEntities } from '@/features/entity/hooks/useEntities'

// Mock dependencies
jest.mock('next/navigation', () => ({
    useRouter: jest.fn(),
}))

jest.mock('@/features/entity/hooks/useEntities', () => ({
    useEntities: jest.fn(),
}))

describe('EntityPage', () => {
    const mockRouter = {
        push: jest.fn(),
    }

    beforeEach(() => {
        jest.clearAllMocks();
        (useRouter as jest.Mock).mockReturnValue(mockRouter);
    })

    it('renders the entity list correctly', () => {
        const mockEntities = [
            {
                id: 'e1',
                kind: { major: 'TestMajor', minor: 'TestMinor' },
                name: { value: 'Entity 1' },
                created: '2024-01-01T10:00:00Z',
            },
            {
                id: 'e2',
                kind: { major: 'OtherMajor', minor: 'OtherMinor' },
                name: { value: 'Entity 2' },
                created: '2024-01-02T10:00:00Z',
            },
        ];

        (useEntities as jest.Mock).mockReturnValue({
            data: mockEntities,
            isLoading: false,
        })

        render(<EntityPage />)

        expect(screen.getByText('Entities')).toBeInTheDocument()
        expect(screen.getByText('Create and manage entities in the system.')).toBeInTheDocument()
        expect(screen.getByText('Entity 1')).toBeInTheDocument()
        expect(screen.getByText('Entity 2')).toBeInTheDocument()
        expect(screen.getByText('TestMajor / TestMinor')).toBeInTheDocument()
    })

    it('navigates to create page when New Entity button is clicked', () => {
        (useEntities as jest.Mock).mockReturnValue({
            data: [],
            isLoading: false,
        })

        render(<EntityPage />)

        fireEvent.click(screen.getByRole('button', { name: /New Entity/i }))

        expect(mockRouter.push).toHaveBeenCalledWith('/entity/create')
    })

    it('navigates to view page when View action/ID is clicked', () => {
        const mockEntities = [
            {
                id: 'e1',
                kind: { major: 'TestMajor', minor: 'TestMinor' },
                name: { value: 'Entity 1' },
                created: '2024-01-01T10:00:00Z',
            },
        ];

        (useEntities as jest.Mock).mockReturnValue({
            data: mockEntities,
            isLoading: false,
        })

        render(<EntityPage />)

        // Click ID link
        fireEvent.click(screen.getByText('e1'))
        expect(mockRouter.push).toHaveBeenCalledWith('/entity/view/e1')

        // Click View action button (using title="View")
        fireEvent.click(screen.getByTitle('View'))
        expect(mockRouter.push).toHaveBeenCalledWith('/entity/view/e1')
    })

    it('navigates to edit page when Edit action is clicked', () => {
        const mockEntities = [
            {
                id: 'e1',
                kind: { major: 'TestMajor', minor: 'TestMinor' },
                name: { value: 'Entity 1' },
                created: '2024-01-01T10:00:00Z',
            },
        ];

        (useEntities as jest.Mock).mockReturnValue({
            data: mockEntities,
            isLoading: false,
        })

        render(<EntityPage />)

        fireEvent.click(screen.getByTitle('Edit'))

        expect(mockRouter.push).toHaveBeenCalledWith('/entity/update/e1')
    })
})

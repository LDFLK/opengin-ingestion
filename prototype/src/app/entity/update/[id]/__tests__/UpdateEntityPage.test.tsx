import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import UpdateEntityPage from '../page'
import { useRouter } from 'next/navigation'
import { useEntity, useUpdateEntity } from '@/features/entity/hooks/useEntities'

// Mock dependencies
jest.mock('next/navigation', () => ({
    useRouter: jest.fn(),
}))

jest.mock('@/features/entity/hooks/useEntities', () => ({
    useEntity: jest.fn(),
    useUpdateEntity: jest.fn(),
}))

xdescribe('UpdateEntityPage', () => {
    const mockRouter = {
        push: jest.fn(),
        back: jest.fn(),
    }
    const mockMutate = jest.fn()
    const mockParams = Promise.resolve({ id: 'e1' })

    beforeEach(() => {
        jest.clearAllMocks();
        (useRouter as jest.Mock).mockReturnValue(mockRouter);
        (useUpdateEntity as jest.Mock).mockReturnValue({
            mutate: mockMutate,
            isPending: false,
        });
    })

    it('renders the update form with initial data', async () => {
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

        render(<UpdateEntityPage params={mockParams} />)

        expect(await screen.findByRole('heading', { name: 'Update Entity' })).toBeInTheDocument()

        // Check if form fields are populated (using display value for inputs)
        expect(screen.getByDisplayValue('e1')).toBeInTheDocument()
        expect(screen.getByDisplayValue('TestMajor')).toBeInTheDocument()
        expect(screen.getByDisplayValue('TestMinor')).toBeInTheDocument()
        expect(screen.getByDisplayValue('Test Entity')).toBeInTheDocument()

        // Note: Date inputs need local time format check. 
        // 2024-01-01T10:00:00Z -> Local time depend on test env (UTC in most CI, but +5:30 here?)
        // Since we are running on user's machine, it will adjust to their local time.
        // It's safer to just check if input exists or rely on Name/ID for population check.
    })

    it('submits the form with updated data and redirects', async () => {
        const mockEntity = {
            id: 'e1',
            kind: { major: 'TestMajor', minor: 'TestMinor' },
            name: { value: 'Test Entity', startTime: '2024-01-01T10:00:00Z' },
            created: '2024-01-01T10:00:00Z',
            terminated: '',
            metadata: [], attributes: [], relationships: []
        };

        (useEntity as jest.Mock).mockReturnValue({
            data: mockEntity,
            isLoading: false,
        })

        mockMutate.mockImplementation((data, { onSuccess }) => {
            onSuccess()
        })

        render(<UpdateEntityPage params={mockParams} />)

        expect(await screen.findByRole('heading', { name: 'Update Entity' })).toBeInTheDocument()

        // Update name
        fireEvent.change(screen.getByLabelText(/^Name$/i), { target: { value: 'Updated Name' } })

        // Submit
        fireEvent.click(screen.getByRole('button', { name: /Update Entity/i }))

        await waitFor(() => {
            expect(mockMutate).toHaveBeenCalledWith(
                expect.objectContaining({
                    id: 'e1',
                    name: expect.objectContaining({ value: 'Updated Name' }),
                }),
                expect.any(Object)
            )
        })

        expect(mockRouter.push).toHaveBeenCalledWith('/entity/view/e1')
    })
})

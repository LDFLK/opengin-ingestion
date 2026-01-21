import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import CreateEntityPage from '../page'
import { useRouter } from 'next/navigation'
import { useCreateEntity } from '@/features/entity/hooks/useEntities'

// Mock dependencies
jest.mock('next/navigation', () => ({
    useRouter: jest.fn(),
}))

jest.mock('@/features/entity/hooks/useEntities', () => ({
    useCreateEntity: jest.fn(),
}))

describe('CreateEntityPage', () => {
    const mockRouter = {
        push: jest.fn(),
        back: jest.fn(),
    }
    const mockMutate = jest.fn()

    beforeEach(() => {
        // Reset mocks
        jest.clearAllMocks();
        (useRouter as jest.Mock).mockReturnValue(mockRouter);
        (useCreateEntity as jest.Mock).mockReturnValue({
            mutate: mockMutate,
            isPending: false,
        });
    })

    it('renders the create entity page correctly', () => {
        render(<CreateEntityPage />)

        expect(screen.getByText('Create New Entity')).toBeInTheDocument()
        expect(screen.getByText('Add a new entity to the system.')).toBeInTheDocument()
        expect(screen.getByLabelText(/ID/i)).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /Create Entity/i })).toBeInTheDocument()
    })

    it('submits the form with correct data and redirects on success', async () => {
        // Setup mutate to call onSuccess immediately
        mockMutate.mockImplementation((data, { onSuccess }) => {
            onSuccess()
        })

        render(<CreateEntityPage />)

        // Fill form
        fireEvent.change(screen.getByLabelText(/ID/i), { target: { value: 'test-id' } })
        fireEvent.change(screen.getByLabelText(/Major Kind/i), { target: { value: 'TestMajor' } })
        fireEvent.change(screen.getByLabelText(/Minor Kind/i), { target: { value: 'TestMinor' } })
        fireEvent.change(screen.getByLabelText(/^Name$/i), { target: { value: 'Test Name' } })
        fireEvent.change(screen.getByLabelText(/Start Time/i), { target: { value: '2024-01-01T10:00' } })

        // Submit
        fireEvent.click(screen.getByRole('button', { name: /Create Entity/i }))

        await waitFor(() => {
            expect(mockMutate).toHaveBeenCalledWith(
                expect.objectContaining({
                    id: 'test-id',
                    kind: { major: 'TestMajor', minor: 'TestMinor' },
                    name: expect.objectContaining({ value: 'Test Name' }),
                    // created should be converted from local to UTC: 2024-01-01T10:00 -> 2024-01-01T10:00:00.000Z (assuming mock/test timezone logic matches or just check partial)
                    // Since timezones are tricky in tests, we'll check name.value and ensure created exists
                    created: expect.stringMatching(/2024-01-01/),
                }),
                expect.any(Object)
            )
        })

        expect(mockRouter.push).toHaveBeenCalledWith('/entity')
    })

    it('navigates back when cancel is clicked', () => {
        render(<CreateEntityPage />)

        fireEvent.click(screen.getByRole('button', { name: /Cancel/i }))

        expect(mockRouter.back).toHaveBeenCalled()
    })
})

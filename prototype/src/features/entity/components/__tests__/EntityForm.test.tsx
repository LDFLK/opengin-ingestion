import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { EntityForm } from '../EntityForm'
import { Entity } from '@/services/entityService'

describe('EntityForm', () => {
    const mockEntity: Partial<Entity> = {
        id: 'e1',
        kind: { major: 'test', minor: 'example' },
        name: { value: 'Test Entity', startTime: '2024-01-01T00:00', endTime: '' },
    }

    it('renders all required form fields', () => {
        const onSubmit = jest.fn()
        const onCancel = jest.fn()

        render(<EntityForm onSubmit={onSubmit} onCancel={onCancel} />)

        // Check for form fields
        expect(screen.getByLabelText(/ID/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/Major Kind/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/Minor Kind/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/^Name$/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/Start Time/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/End Time/i)).toBeInTheDocument()
    })

    it('populates form with initial data when provided', () => {
        const onSubmit = jest.fn()
        const onCancel = jest.fn()

        render(<EntityForm initialData={mockEntity} onSubmit={onSubmit} onCancel={onCancel} />)

        expect(screen.getByDisplayValue('e1')).toBeInTheDocument()
        expect(screen.getByDisplayValue('test')).toBeInTheDocument()
        expect(screen.getByDisplayValue('example')).toBeInTheDocument()
        expect(screen.getByDisplayValue('Test Entity')).toBeInTheDocument()
    })

    it('calls onSubmit with correct data when form is submitted', async () => {
        const onSubmit = jest.fn()
        const onCancel = jest.fn()

        render(<EntityForm onSubmit={onSubmit} onCancel={onCancel} />)

        // Fill out the form
        fireEvent.change(screen.getByLabelText(/ID/i), { target: { value: 'e2' } })
        fireEvent.change(screen.getByLabelText(/Major Kind/i), { target: { value: 'Person' } })
        fireEvent.change(screen.getByLabelText(/Minor Kind/i), { target: { value: 'Employee' } })
        fireEvent.change(screen.getByLabelText(/^Name$/i), { target: { value: 'John Doe' } })
        fireEvent.change(screen.getByLabelText(/Start Time/i), { target: { value: '2024-01-01T10:00' } })

        // Submit the form
        fireEvent.click(screen.getByText(/Save/i))

        await waitFor(() => {
            expect(onSubmit).toHaveBeenCalledWith(
                expect.objectContaining({
                    id: 'e2',
                    kind: { major: 'Person', minor: 'Employee' },
                    name: {
                        value: 'John Doe',
                        startTime: expect.stringMatching(/^2024-01-01/),
                        endTime: '',
                    },
                })
            )
        })
    })

    it('calls onCancel when cancel button is clicked', () => {
        const onSubmit = jest.fn()
        const onCancel = jest.fn()

        render(<EntityForm onSubmit={onSubmit} onCancel={onCancel} />)

        fireEvent.click(screen.getByText(/Cancel/i))

        expect(onCancel).toHaveBeenCalled()
        expect(onSubmit).not.toHaveBeenCalled()
    })

    it('disables submit button when isLoading is true', () => {
        const onSubmit = jest.fn()
        const onCancel = jest.fn()

        render(<EntityForm onSubmit={onSubmit} onCancel={onCancel} isLoading={true} />)

        const submitButton = screen.getByText(/Saving.../i)
        expect(submitButton).toBeDisabled()
    })

    it('auto-generates created timestamp for new entities', async () => {
        const onSubmit = jest.fn()
        const onCancel = jest.fn()

        render(<EntityForm onSubmit={onSubmit} onCancel={onCancel} />)

        fireEvent.change(screen.getByLabelText(/ID/i), { target: { value: 'e3' } })
        fireEvent.change(screen.getByLabelText(/Major Kind/i), { target: { value: 'test' } })
        fireEvent.change(screen.getByLabelText(/Minor Kind/i), { target: { value: 'test' } })
        fireEvent.change(screen.getByLabelText(/^Name$/i), { target: { value: 'Test' } })
        fireEvent.change(screen.getByLabelText(/Start Time/i), { target: { value: '2024-01-01T10:00' } })

        fireEvent.click(screen.getByText(/Save/i))

        await waitFor(() => {
            expect(onSubmit).toHaveBeenCalledWith(
                expect.objectContaining({
                    created: expect.any(String),
                    terminated: '',
                })
            )
        })
    })
})

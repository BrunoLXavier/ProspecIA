import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import TranslationsAdminPage from '@/app/admin/translations/page'
import * as apiClient from '@/lib/api/client'

// Mock the API client
vi.mock('@/lib/api/client', () => ({
  get: vi.fn(),
  post: vi.fn(),
  patch: vi.fn(),
  del: vi.fn(),
}))

// Mock react-hot-toast
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

// Mock useI18n hook
vi.mock('@/lib/hooks/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => key, // Just return the key for testing
    locale: 'pt-BR',
  }),
}))

describe('TranslationsAdminPage', () => {
  const mockTranslations = [
    {
      id: 'common:button.save',
      key: 'button.save',
      namespace: 'common',
      pt_br: 'Salvar',
      en_us: 'Save',
      es_es: 'Guardar',
      created_at: '2026-01-15T10:00:00',
      updated_at: '2026-01-15T10:00:00',
      created_by: 'system',
      updated_by: 'system',
    },
    {
      id: 'admin:button.add_key',
      key: 'button.add_key',
      namespace: 'admin',
      pt_br: 'Adicionar Chave',
      en_us: 'Add Key',
      es_es: 'Agregar Clave',
      created_at: '2026-01-15T11:00:00',
      updated_at: '2026-01-15T11:00:00',
      created_by: 'system',
      updated_by: 'system',
    },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(apiClient.get).mockResolvedValue(mockTranslations)
  })

  it('should render the translations admin page', async () => {
    render(<TranslationsAdminPage />)
    
    await waitFor(() => {
      expect(screen.getByText('admin:title')).toBeInTheDocument()
    })
  })

  it('should load and display translations', async () => {
    render(<TranslationsAdminPage />)
    
    await waitFor(() => {
      expect(vi.mocked(apiClient.get)).toHaveBeenCalledWith(
        expect.stringContaining('/system/translations')
      )
    })

    await waitFor(() => {
      expect(screen.getByText('button.save')).toBeInTheDocument()
      expect(screen.getByText('Salvar')).toBeInTheDocument()
    })
  })

  it('should filter translations by search', async () => {
    render(<TranslationsAdminPage />)
    
    await waitFor(() => {
      expect(screen.getByPlaceholderText('admin:table.search_placeholder')).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText('admin:table.search_placeholder')
    fireEvent.change(searchInput, { target: { value: 'button.add' } })

    await waitFor(() => {
      expect(screen.getByText('button.add_key')).toBeInTheDocument()
      expect(screen.queryByText('button.save')).not.toBeInTheDocument()
    })
  })

  it('should filter translations by namespace', async () => {
    render(<TranslationsAdminPage />)
    
    const namespaceSelect = screen.getByDisplayValue('') // Empty option initially
    fireEvent.change(namespaceSelect, { target: { value: 'admin' } })

    await waitFor(() => {
      expect(screen.getByText('button.add_key')).toBeInTheDocument()
      expect(screen.queryByText('button.save')).not.toBeInTheDocument()
    })
  })

  it('should open modal when clicking add button', async () => {
    render(<TranslationsAdminPage />)
    
    const addButton = screen.getByText('admin:button.add_key')
    fireEvent.click(addButton)

    await waitFor(() => {
      expect(screen.getByText('admin:modal.add_title')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('admin:form.key_placeholder')).toBeInTheDocument()
    })
  })

  it('should validate required fields in modal', async () => {
    render(<TranslationsAdminPage />)
    
    const addButton = screen.getByText('admin:button.add_key')
    fireEvent.click(addButton)

    const saveButton = await screen.findByText('admin:button.save')
    fireEvent.click(saveButton)

    // Should show error or prevent submission
    expect(vi.mocked(apiClient.post)).not.toHaveBeenCalled()
  })

  it('should submit form with valid data', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      id: 'test:new_key',
      key: 'new_key',
      namespace: 'common',
      pt_br: 'Nova Chave',
      en_us: 'New Key',
      es_es: 'Nueva Clave',
      created_at: '2026-01-15T12:00:00',
      updated_at: '2026-01-15T12:00:00',
      created_by: 'test_user',
      updated_by: 'test_user',
    })

    render(<TranslationsAdminPage />)
    
    // Open modal
    const addButton = screen.getByText('admin:button.add_key')
    fireEvent.click(addButton)

    // Fill form
    const keyInput = await screen.findByPlaceholderText('admin:form.key_placeholder')
    fireEvent.change(keyInput, { target: { value: 'new_key' } })

    const ptInput = screen.getByDisplayValue('') // First textarea
    fireEvent.change(ptInput, { target: { value: 'Nova Chave' } })

    // Submit
    const saveButton = screen.getByText('admin:button.save')
    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(vi.mocked(apiClient.post)).toHaveBeenCalled()
    })
  })

  it('should export translations', async () => {
    const { default: toast } = await import('react-hot-toast')
    
    render(<TranslationsAdminPage />)
    
    await waitFor(() => {
      const exportButton = screen.getByText('admin:button.export')
      expect(exportButton).toBeInTheDocument()
    })

    const exportButton = screen.getByText('admin:button.export')
    fireEvent.click(exportButton)

    // Mock URL.createObjectURL and document.createElement
    global.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
    
    await waitFor(() => {
      expect(vi.mocked(toast.success)).toHaveBeenCalledWith('admin:export.success')
    })
  })

  it('should delete translation with confirmation', async () => {
    global.confirm = vi.fn(() => true)
    vi.mocked(apiClient.del).mockResolvedValue({ message: 'Translation deleted' })

    render(<TranslationsAdminPage />)
    
    await waitFor(() => {
      expect(screen.getByText('button.save')).toBeInTheDocument()
    })

    // Find delete button (assuming there's one per row, we'll need to check the DOM)
    const deleteButtons = screen.getAllByText('admin:button.delete')
    fireEvent.click(deleteButtons[0])

    await waitFor(() => {
      expect(global.confirm).toHaveBeenCalled()
      expect(vi.mocked(apiClient.del)).toHaveBeenCalled()
    })
  })
})

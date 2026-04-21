import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import App from './App'

// Mock the child components to simplify the test
vi.mock('./components/Dashboard', () => ({ default: () => <div data-testid="dashboard" /> }))
vi.mock('./components/RegulationList', () => ({ default: () => <div data-testid="regulation-list" /> }))
vi.mock('./components/Analysis', () => ({ default: () => <div data-testid="analysis" /> }))
vi.mock('./components/AIQuery', () => ({ default: () => <div data-testid="ai-query" /> }))
vi.mock('./components/SourceMonitor', () => ({ default: () => <div data-testid="source-monitor" /> }))

describe('App Component - Offline Banner', () => {
  beforeEach(() => {
    // Reset fetch mock before each test
    vi.restoreAllMocks()
    global.fetch = vi.fn()
  })

  it('should not display the offline banner when the API is online', async () => {
    global.fetch.mockResolvedValueOnce({ ok: true })

    render(<App />)

    // Wait for the effect to finish and check the text doesn't exist
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('/health'))
      // The default state is true, but we still ensure the banner is not displayed
      // after the fetch resolves.
      expect(screen.queryByText(/API offline — showing cached data/)).not.toBeInTheDocument()
    })
  })

  it('should display the offline banner when the API responds with ok: false', async () => {
    global.fetch.mockResolvedValueOnce({ ok: false })

    render(<App />)

    // Wait for the effect to complete
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('/health'))
    })

    expect(await screen.findByText(/API offline — showing cached data/)).toBeInTheDocument()
  })

  it('should display the offline banner when the API fetch rejects (e.g. network error)', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'))

    render(<App />)

    // Wait for the effect to complete
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('/health'))
    })

    expect(await screen.findByText(/API offline — showing cached data/)).toBeInTheDocument()
  })
})

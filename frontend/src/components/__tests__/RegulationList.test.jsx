import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import RegulationList from '../RegulationList';

describe('RegulationList Pagination', () => {
  beforeEach(() => {
    // Reset fetch mock before each test
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders pagination and handles edge cases correctly', async () => {
    const mockData = {
      total: 50,
      total_pages: 3,
      items: [
        {
          regulation_id: 'reg1',
          title: 'Test Regulation 1',
          summary: 'Summary 1',
          status: 'active',
          type: 'rule',
          source: 'test_source',
          verticals: [{ vertical: 'finance' }]
        }
      ]
    };

    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockData)
    });

    render(<RegulationList apiBase="http://localhost:8000/api" />);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('50 Regulations')).toBeInTheDocument();
    });

    // Check pagination renders
    expect(screen.getByText('1 / 3')).toBeInTheDocument();

    // Check initial button states
    const prevButton = screen.getByRole('button', { name: /← Prev/i });
    const nextButton = screen.getByRole('button', { name: /Next →/i });

    expect(prevButton).toBeDisabled();
    expect(nextButton).not.toBeDisabled();

    // Click next button
    await userEvent.click(nextButton);

    // Verify fetch was called with page 2
    expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('page=2'));

    // Wait for re-render with page 2
    await waitFor(() => {
      expect(screen.getByText('2 / 3')).toBeInTheDocument();
    });

    // Check button states on page 2
    expect(prevButton).not.toBeDisabled();
    expect(nextButton).not.toBeDisabled();

    // Click next button to go to last page
    await userEvent.click(nextButton);

    // Verify fetch was called with page 3
    expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('page=3'));

    // Wait for re-render with page 3
    await waitFor(() => {
      expect(screen.getByText('3 / 3')).toBeInTheDocument();
    });

    // Check button states on last page
    expect(prevButton).not.toBeDisabled();
    expect(nextButton).toBeDisabled();

    // Click prev button
    await userEvent.click(prevButton);

    // Verify fetch was called with page 2 again
    expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('page=2'));

    // Wait for re-render with page 2
    await waitFor(() => {
      expect(screen.getByText('2 / 3')).toBeInTheDocument();
    });

    // Click prev to first page
    await userEvent.click(prevButton);

    // Wait for re-render with page 1
    await waitFor(() => {
      expect(screen.getByText('1 / 3')).toBeInTheDocument();
    });

    // Check prev is disabled again
    expect(prevButton).toBeDisabled();

    // Test that changing a filter resets page to 1
    // We are on page 1 now. Let's go to page 2 first.
    await userEvent.click(nextButton);
    await waitFor(() => {
      expect(screen.getByText('2 / 3')).toBeInTheDocument();
    });

    // Change filter (e.g., status)
    const select = screen.getByRole('combobox');
    await userEvent.selectOptions(select, 'proposed');

    // It should reset to page 1
    await waitFor(() => {
      expect(screen.getByText('1 / 3')).toBeInTheDocument();
    });
  });
});

/**
 * QuotaStatus Component Tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@solidjs/testing-library';
import { QuotaStatus } from '../QuotaStatus';
import { AIQuotaService } from '../../../services/ai-quota.service';

// Mock the AIQuotaService
vi.mock('../../../services/ai-quota.service', () => ({
  AIQuotaService: {
    getQuotaStatus: vi.fn()
  }
}));

describe('QuotaStatus Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should display loading state initially', () => {
    vi.mocked(AIQuotaService.getQuotaStatus).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(() => <QuotaStatus userId={1} />);
    
    expect(screen.getByRole('status', { hidden: true })).toBeInTheDocument();
  });

  it('should display quota status when loaded', async () => {
    const mockStatus = {
      user_id: 1,
      date: '2026-02-28',
      gps_enhanced_requests: 15,
      pincode_requests: 42,
      quota_limit: 20,
      remaining_quota: 5,
      quota_exceeded: false,
      next_reset: '2026-03-01T00:00:00+05:30'
    };

    vi.mocked(AIQuotaService.getQuotaStatus).mockResolvedValue(mockStatus);

    render(() => <QuotaStatus userId={1} showDetails={true} />);

    await waitFor(() => {
      expect(screen.getByText('AI Usage Today')).toBeInTheDocument();
      expect(screen.getByText(/5 of 20 remaining/)).toBeInTheDocument();
      expect(screen.getByText(/15 used/)).toBeInTheDocument();
    });
  });

  it('should show warning when quota is low', async () => {
    const mockStatus = {
      user_id: 1,
      date: '2026-02-28',
      gps_enhanced_requests: 18,
      pincode_requests: 42,
      quota_limit: 20,
      remaining_quota: 2,
      quota_exceeded: false,
      next_reset: '2026-03-01T00:00:00+05:30'
    };

    vi.mocked(AIQuotaService.getQuotaStatus).mockResolvedValue(mockStatus);

    render(() => <QuotaStatus userId={1} showDetails={true} />);

    await waitFor(() => {
      expect(screen.getByText(/Low quota: 2 GPS-enhanced requests remaining/)).toBeInTheDocument();
    });
  });

  it('should show exceeded message when quota is exceeded', async () => {
    const mockStatus = {
      user_id: 1,
      date: '2026-02-28',
      gps_enhanced_requests: 20,
      pincode_requests: 42,
      quota_limit: 20,
      remaining_quota: 0,
      quota_exceeded: true,
      next_reset: '2026-03-01T00:00:00+05:30'
    };

    vi.mocked(AIQuotaService.getQuotaStatus).mockResolvedValue(mockStatus);

    render(() => <QuotaStatus userId={1} showDetails={true} />);

    await waitFor(() => {
      expect(screen.getByText(/Daily quota exceeded/)).toBeInTheDocument();
    });
  });

  it('should display error message on failure', async () => {
    vi.mocked(AIQuotaService.getQuotaStatus).mockRejectedValue(
      new Error('Network error')
    );

    render(() => <QuotaStatus userId={1} />);

    await waitFor(() => {
      expect(screen.getByText(/Network error/)).toBeInTheDocument();
      expect(screen.getByText('Retry')).toBeInTheDocument();
    });
  });

  it('should show details when showDetails is true', async () => {
    const mockStatus = {
      user_id: 1,
      date: '2026-02-28',
      gps_enhanced_requests: 15,
      pincode_requests: 42,
      quota_limit: 20,
      remaining_quota: 5,
      quota_exceeded: false,
      next_reset: '2026-03-01T00:00:00+05:30'
    };

    vi.mocked(AIQuotaService.getQuotaStatus).mockResolvedValue(mockStatus);

    render(() => <QuotaStatus userId={1} showDetails={true} />);

    await waitFor(() => {
      expect(screen.getByText(/GPS-enhanced requests:/)).toBeInTheDocument();
      expect(screen.getByText(/Pincode-based requests:/)).toBeInTheDocument();
      expect(screen.getByText(/Resets in:/)).toBeInTheDocument();
    });
  });

  it('should use correct progress bar color based on usage', async () => {
    const mockStatus = {
      user_id: 1,
      date: '2026-02-28',
      gps_enhanced_requests: 18,
      pincode_requests: 42,
      quota_limit: 20,
      remaining_quota: 2,
      quota_exceeded: false,
      next_reset: '2026-03-01T00:00:00+05:30'
    };

    vi.mocked(AIQuotaService.getQuotaStatus).mockResolvedValue(mockStatus);

    render(() => <QuotaStatus userId={1} />);

    await waitFor(() => {
      const progressBar = screen.getByRole('progressbar', { hidden: true });
      expect(progressBar).toHaveClass('bg-orange-500'); // 90% usage
    });
  });
});

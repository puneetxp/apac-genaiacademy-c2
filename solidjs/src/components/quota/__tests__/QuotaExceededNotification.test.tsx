/**
 * QuotaExceededNotification Component Tests
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@solidjs/testing-library';
import { QuotaExceededNotification } from '../QuotaExceededNotification';

describe('QuotaExceededNotification Component', () => {
  const mockNextReset = '2026-03-01T00:00:00+05:30';

  it('should display notification when quota is exceeded', () => {
    render(() => (
      <QuotaExceededNotification
        quotaExceeded={true}
        nextResetTime={mockNextReset}
      />
    ));
    
    expect(screen.getByText(/Daily AI Quota Exceeded/)).toBeInTheDocument();
    expect(screen.getByText(/20 GPS-enhanced AI requests/)).toBeInTheDocument();
  });

  it('should not display notification when quota is not exceeded', () => {
    render(() => (
      <QuotaExceededNotification
        quotaExceeded={false}
        nextResetTime={mockNextReset}
      />
    ));
    
    expect(screen.queryByText(/Daily AI Quota Exceeded/)).not.toBeInTheDocument();
  });

  it('should display fallback features list', () => {
    render(() => (
      <QuotaExceededNotification
        quotaExceeded={true}
        nextResetTime={mockNextReset}
      />
    ));
    
    expect(screen.getByText(/pincode-based recommendations/)).toBeInTheDocument();
    expect(screen.getByText(/Regional crop analysis/)).toBeInTheDocument();
    expect(screen.getByText(/Seasonal guidance/)).toBeInTheDocument();
    expect(screen.getByText(/marketplace features/)).toBeInTheDocument();
  });

  it('should display quota reset time', () => {
    render(() => (
      <QuotaExceededNotification
        quotaExceeded={true}
        nextResetTime={mockNextReset}
      />
    ));
    
    expect(screen.getByText(/Quota resets in:/)).toBeInTheDocument();
    expect(screen.getByText(/IST/)).toBeInTheDocument();
  });

  it('should display explanation about quota limit', () => {
    render(() => (
      <QuotaExceededNotification
        quotaExceeded={true}
        nextResetTime={mockNextReset}
      />
    ));
    
    expect(screen.getByText(/Why the limit?/)).toBeInTheDocument();
    expect(screen.getByText(/cost more to provide/)).toBeInTheDocument();
  });

  it('should call onDismiss when dismiss button is clicked', () => {
    const onDismiss = vi.fn();
    render(() => (
      <QuotaExceededNotification
        quotaExceeded={true}
        nextResetTime={mockNextReset}
        onDismiss={onDismiss}
      />
    ));
    
    const dismissButton = screen.getByRole('button', { name: /dismiss/i });
    fireEvent.click(dismissButton);
    
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it('should not show dismiss button when onDismiss is not provided', () => {
    render(() => (
      <QuotaExceededNotification
        quotaExceeded={true}
        nextResetTime={mockNextReset}
      />
    ));
    
    expect(screen.queryByRole('button', { name: /dismiss/i })).not.toBeInTheDocument();
  });

  it('should format reset time correctly', () => {
    const nextReset = '2026-03-01T14:30:00+05:30';
    render(() => (
      <QuotaExceededNotification
        quotaExceeded={true}
        nextResetTime={nextReset}
      />
    ));
    
    // Should display time in IST format
    expect(screen.getByText(/02:30 PM IST/)).toBeInTheDocument();
  });

  it('should calculate time until reset correctly', () => {
    // Mock current time to be 2 hours before reset
    const now = new Date('2026-02-28T22:00:00+05:30');
    vi.setSystemTime(now);
    
    const nextReset = '2026-03-01T00:00:00+05:30';
    render(() => (
      <QuotaExceededNotification
        quotaExceeded={true}
        nextResetTime={nextReset}
      />
    ));
    
    expect(screen.getByText(/2 hours/)).toBeInTheDocument();
    
    vi.useRealTimers();
  });
});

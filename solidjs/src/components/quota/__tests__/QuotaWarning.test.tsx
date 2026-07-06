/**
 * QuotaWarning Component Tests
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@solidjs/testing-library';
import { QuotaWarning } from '../QuotaWarning';

describe('QuotaWarning Component', () => {
  it('should display warning when remaining quota is less than 5', () => {
    render(() => <QuotaWarning remainingQuota={3} quotaLimit={20} />);
    
    expect(screen.getByText(/Low AI Quota Warning/)).toBeInTheDocument();
    expect(screen.getByText(/You have only/)).toBeInTheDocument();
    expect(screen.getByText(/3/)).toBeInTheDocument();
  });

  it('should not display warning when remaining quota is 5 or more', () => {
    render(() => <QuotaWarning remainingQuota={5} quotaLimit={20} />);
    
    expect(screen.queryByText(/Low AI Quota Warning/)).not.toBeInTheDocument();
  });

  it('should not display warning when quota is 0', () => {
    render(() => <QuotaWarning remainingQuota={0} quotaLimit={20} />);
    
    expect(screen.queryByText(/Low AI Quota Warning/)).not.toBeInTheDocument();
  });

  it('should display fallback explanation', () => {
    render(() => <QuotaWarning remainingQuota={2} quotaLimit={20} />);
    
    expect(screen.getByText(/pincode-based recommendations/)).toBeInTheDocument();
    expect(screen.getByText(/regional data/)).toBeInTheDocument();
  });

  it('should display reset time information', () => {
    render(() => <QuotaWarning remainingQuota={4} quotaLimit={20} />);
    
    expect(screen.getByText(/midnight IST/)).toBeInTheDocument();
  });

  it('should call onDismiss when dismiss button is clicked', () => {
    const onDismiss = vi.fn();
    render(() => <QuotaWarning remainingQuota={3} quotaLimit={20} onDismiss={onDismiss} />);
    
    const dismissButton = screen.getByRole('button', { name: /dismiss/i });
    fireEvent.click(dismissButton);
    
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it('should not show dismiss button when onDismiss is not provided', () => {
    render(() => <QuotaWarning remainingQuota={3} quotaLimit={20} />);
    
    expect(screen.queryByRole('button', { name: /dismiss/i })).not.toBeInTheDocument();
  });

  it('should display correct remaining quota number', () => {
    render(() => <QuotaWarning remainingQuota={1} quotaLimit={20} />);
    
    expect(screen.getByText(/1/)).toBeInTheDocument();
    expect(screen.getByText(/GPS-enhanced AI requests remaining/)).toBeInTheDocument();
  });
});

/**
 * Farm Registration Page
 * Register a new farm
 */

import { Component, lazy, Suspense } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import { QuotaStatus } from '../../components/quota/QuotaStatus';

// Lazy load farm registration form
const FarmRegistrationForm = lazy(() => import('../../components/farm/FarmRegistrationForm'));

const FarmRegisterPage: Component = () => {
  const navigate = useNavigate();

  const handleSuccess = (farmId: number) => {
    navigate(`/farm/${farmId}`);
  };

  const handleCancel = () => {
    navigate('/dashboard');
  };

  return (
    <div class="min-h-screen bg-gradient-to-br from-green-50 to-green-100 py-8 px-4">
      <div class="max-w-2xl mx-auto">
        {/* Quota Status */}
        <div class="mb-4">
          <QuotaStatus userId={1} compact={true} showDetails={false} />
        </div>
        
        <Suspense fallback={<div class="bg-white rounded-lg shadow-md p-6 animate-pulse h-96" />}>
          <FarmRegistrationForm
            onSuccess={handleSuccess}
            onCancel={handleCancel}
          />
        </Suspense>
      </div>
    </div>
  );
};

export default FarmRegisterPage;

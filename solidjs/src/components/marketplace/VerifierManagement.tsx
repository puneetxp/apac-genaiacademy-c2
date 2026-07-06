/**
 * Third-Party Verifier Management Component
 * Manages registration and assignment of third-party quality verifiers
 */

import { Component, createSignal, For, Show, onMount } from 'solid-js';

interface Verifier {
  id: number;
  name: string;
  email: string;
  phone: string;
  certification: string;
  specialization: string[];
  location_state: string;
  location_district: string;
  rating: number;
  verifications_count: number;
  status: 'active' | 'inactive' | 'suspended';
  created_at: string;
}

interface VerifierManagementProps {
  bookingId?: number;
  onAssign?: (verifierId: number) => Promise<void>;
}

export const VerifierManagement: Component<VerifierManagementProps> = (props) => {
  const [verifiers, setVerifiers] = createSignal<Verifier[]>([]);
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal('');
  const [showAddForm, setShowAddForm] = createSignal(false);
  const [selectedVerifier, setSelectedVerifier] = createSignal<number | null>(null);

  // Form fields for adding new verifier
  const [name, setName] = createSignal('');
  const [email, setEmail] = createSignal('');
  const [phone, setPhone] = createSignal('');
  const [certification, setCertification] = createSignal('');
  const [specialization, setSpecialization] = createSignal<string[]>([]);
  const [locationState, setLocationState] = createSignal('');
  const [locationDistrict, setLocationDistrict] = createSignal('');

  onMount(async () => {
    await loadVerifiers();
  });

  const loadVerifiers = async () => {
    setLoading(true);
    setError('');

    try {
      // TODO: Implement actual API call
      // Mock data for now
      const mockVerifiers: Verifier[] = [
        {
          id: 1,
          name: 'Agricultural Quality Labs',
          email: 'contact@aqlabs.com',
          phone: '+91-9876543210',
          certification: 'ISO 9001:2015',
          specialization: ['Grains', 'Vegetables', 'Fruits'],
          location_state: 'Maharashtra',
          location_district: 'Pune',
          rating: 4.8,
          verifications_count: 156,
          status: 'active',
          created_at: '2024-01-15',
        },
        {
          id: 2,
          name: 'Farm Quality Inspectors',
          email: 'info@fqi.in',
          phone: '+91-9876543211',
          certification: 'NABL Accredited',
          specialization: ['Organic Produce', 'Grains'],
          location_state: 'Karnataka',
          location_district: 'Bangalore',
          rating: 4.6,
          verifications_count: 89,
          status: 'active',
          created_at: '2024-02-20',
        },
      ];

      setVerifiers(mockVerifiers);
    } catch (err: any) {
      setError(err.message || 'Failed to load verifiers');
    } finally {
      setLoading(false);
    }
  };

  const handleAddVerifier = async (e: Event) => {
    e.preventDefault();
    setError('');

    try {
      // TODO: Implement actual API call
      const newVerifier: Verifier = {
        id: Date.now(),
        name: name(),
        email: email(),
        phone: phone(),
        certification: certification(),
        specialization: specialization(),
        location_state: locationState(),
        location_district: locationDistrict(),
        rating: 0,
        verifications_count: 0,
        status: 'active',
        created_at: new Date().toISOString(),
      };

      setVerifiers([...verifiers(), newVerifier]);
      setShowAddForm(false);
      
      // Reset form
      setName('');
      setEmail('');
      setPhone('');
      setCertification('');
      setSpecialization([]);
      setLocationState('');
      setLocationDistrict('');
    } catch (err: any) {
      setError(err.message || 'Failed to add verifier');
    }
  };

  const handleAssignVerifier = async (verifierId: number) => {
    if (props.onAssign) {
      try {
        await props.onAssign(verifierId);
        setSelectedVerifier(verifierId);
      } catch (err: any) {
        setError(err.message || 'Failed to assign verifier');
      }
    }
  };

  const toggleSpecialization = (spec: string) => {
    if (specialization().includes(spec)) {
      setSpecialization(specialization().filter(s => s !== spec));
    } else {
      setSpecialization([...specialization(), spec]);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      case 'suspended':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div class="bg-white rounded-lg shadow-md p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-2xl font-bold">Third-Party Verifiers</h2>
        <button
          onClick={() => setShowAddForm(!showAddForm())}
          class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
        >
          {showAddForm() ? 'Cancel' : 'Add Verifier'}
        </button>
      </div>

      <Show when={error()}>
        <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error()}
        </div>
      </Show>

      {/* Add Verifier Form */}
      <Show when={showAddForm()}>
        <form onSubmit={handleAddVerifier} class="bg-gray-50 rounded-lg p-6 mb-6 space-y-4">
          <h3 class="text-lg font-bold mb-4">Register New Verifier</h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Organization Name *
              </label>
              <input
                type="text"
                value={name()}
                onInput={(e) => setName(e.currentTarget.value)}
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Email *
              </label>
              <input
                type="email"
                value={email()}
                onInput={(e) => setEmail(e.currentTarget.value)}
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Phone *
              </label>
              <input
                type="tel"
                value={phone()}
                onInput={(e) => setPhone(e.currentTarget.value)}
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Certification *
              </label>
              <input
                type="text"
                value={certification()}
                onInput={(e) => setCertification(e.currentTarget.value)}
                placeholder="e.g., ISO 9001:2015, NABL"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                State *
              </label>
              <input
                type="text"
                value={locationState()}
                onInput={(e) => setLocationState(e.currentTarget.value)}
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                District *
              </label>
              <input
                type="text"
                value={locationDistrict()}
                onInput={(e) => setLocationDistrict(e.currentTarget.value)}
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Specialization *
            </label>
            <div class="flex flex-wrap gap-2">
              {['Grains', 'Vegetables', 'Fruits', 'Organic Produce', 'Pulses', 'Spices'].map(spec => (
                <label class="flex items-center space-x-2 bg-white px-3 py-2 rounded-lg border border-gray-300 cursor-pointer hover:bg-gray-50">
                  <input
                    type="checkbox"
                    checked={specialization().includes(spec)}
                    onChange={() => toggleSpecialization(spec)}
                    class="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                  />
                  <span class="text-sm">{spec}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            type="submit"
            class="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 font-medium"
          >
            Register Verifier
          </button>
        </form>
      </Show>

      {/* Verifiers List */}
      <Show when={loading()}>
        <div class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
        </div>
      </Show>

      <Show when={!loading()}>
        <Show
          when={verifiers().length > 0}
          fallback={
            <p class="text-center text-gray-500 py-8">No verifiers registered yet</p>
          }
        >
          <div class="space-y-4">
            <For each={verifiers()}>
              {(verifier) => (
                <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div class="flex items-start justify-between mb-3">
                    <div class="flex-1">
                      <h3 class="text-lg font-bold">{verifier.name}</h3>
                      <p class="text-sm text-gray-600">{verifier.certification}</p>
                    </div>
                    <span class={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(verifier.status)}`}>
                      {verifier.status.toUpperCase()}
                    </span>
                  </div>

                  <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                    <div>
                      <p class="text-xs text-gray-500">Location</p>
                      <p class="text-sm font-medium">{verifier.location_district}, {verifier.location_state}</p>
                    </div>
                    <div>
                      <p class="text-xs text-gray-500">Rating</p>
                      <p class="text-sm font-medium">⭐ {verifier.rating.toFixed(1)}</p>
                    </div>
                    <div>
                      <p class="text-xs text-gray-500">Verifications</p>
                      <p class="text-sm font-medium">{verifier.verifications_count}</p>
                    </div>
                    <div>
                      <p class="text-xs text-gray-500">Contact</p>
                      <p class="text-sm font-medium">{verifier.phone}</p>
                    </div>
                  </div>

                  <div class="mb-3">
                    <p class="text-xs text-gray-500 mb-1">Specialization</p>
                    <div class="flex flex-wrap gap-2">
                      <For each={verifier.specialization}>
                        {(spec) => (
                          <span class="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded">
                            {spec}
                          </span>
                        )}
                      </For>
                    </div>
                  </div>

                  <Show when={props.bookingId}>
                    <button
                      onClick={() => handleAssignVerifier(verifier.id)}
                      disabled={selectedVerifier() === verifier.id}
                      class={`w-full py-2 rounded-lg font-medium ${
                        selectedVerifier() === verifier.id
                          ? 'bg-green-100 text-green-700'
                          : 'bg-green-600 text-white hover:bg-green-700'
                      }`}
                    >
                      {selectedVerifier() === verifier.id ? '✓ Assigned' : 'Assign to Booking'}
                    </button>
                  </Show>
                </div>
              )}
            </For>
          </div>
        </Show>
      </Show>
    </div>
  );
};

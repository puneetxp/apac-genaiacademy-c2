import { Component, For, Show, createSignal } from 'solid-js';

interface Farmer {
  listing_id: number;
  farmer_id: number;
  quantity: number;
  price: number;
}

interface SingleMatch {
  listing_id: number;
  farmer_id: number;
  match_score: number;
  matched_quantity: number;
  price_offered: number;
  explanation: string;
}

interface AggregatedOption {
  group_id: string;
  farmers: Farmer[];
  total_quantity: number;
  average_price: number;
  match_score: number;
  explanation: string;
}

interface SupplyMatchesProps {
  singleMatches: SingleMatch[];
  aggregatedOptions: AggregatedOption[];
  onAcceptSingle: (matchId: number) => Promise<void>;
  onAcceptAggregated: (groupId: string) => Promise<void>;
}

const SupplyMatches: Component<SupplyMatchesProps> = (props) => {
  const [accepting, setAccepting] = createSignal<string | null>(null);
  const [error, setError] = createSignal<string | null>(null);

  const handleAcceptSingle = async (matchId: number) => {
    setError(null);
    setAccepting(`single-${matchId}`);
    try {
      await props.onAcceptSingle(matchId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to accept match');
    } finally {
      setAccepting(null);
    }
  };

  const handleAcceptAggregated = async (groupId: string) => {
    setError(null);
    setAccepting(`agg-${groupId}`);
    try {
      await props.onAcceptAggregated(groupId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to accept match');
    } finally {
      setAccepting(null);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50';
    if (score >= 60) return 'text-yellow-600 bg-yellow-50';
    return 'text-orange-600 bg-orange-50';
  };

  return (
    <div class="space-y-6">
      <Show when={error()}>
        <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error()}
        </div>
      </Show>

      {/* Single Farmer Matches */}
      <Show when={props.singleMatches.length > 0}>
        <div>
          <h3 class="text-xl font-bold text-gray-800 mb-4">
            ✅ Single Farmer Options
          </h3>
          <p class="text-sm text-gray-600 mb-4">
            These farmers can fulfill your entire order individually
          </p>

          <div class="space-y-4">
            <For each={props.singleMatches}>
              {(match) => (
                <div class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                  <div class="flex justify-between items-start mb-4">
                    <div>
                      <div class="flex items-center gap-3 mb-2">
                        <h4 class="text-lg font-semibold text-gray-800">
                          Farmer #{match.farmer_id}
                        </h4>
                        <span class={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(match.match_score)}`}>
                          {match.match_score}% Match
                        </span>
                      </div>
                      <p class="text-sm text-gray-600">{match.explanation}</p>
                    </div>
                  </div>

                  <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
                    <div>
                      <p class="text-sm text-gray-500">Quantity Available</p>
                      <p class="text-lg font-semibold text-gray-800">
                        {match.matched_quantity.toLocaleString()} kg
                      </p>
                    </div>
                    <div>
                      <p class="text-sm text-gray-500">Price per kg</p>
                      <p class="text-lg font-semibold text-gray-800">
                        ₹{match.price_offered.toFixed(2)}
                      </p>
                    </div>
                    <div>
                      <p class="text-sm text-gray-500">Total Cost</p>
                      <p class="text-lg font-semibold text-green-600">
                        ₹{(match.matched_quantity * match.price_offered).toLocaleString()}
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={() => handleAcceptSingle(match.listing_id)}
                    disabled={accepting() !== null}
                    class="w-full bg-green-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                  >
                    {accepting() === `single-${match.listing_id}` ? 'Accepting...' : 'Accept This Match'}
                  </button>
                </div>
              )}
            </For>
          </div>
        </div>
      </Show>

      {/* Aggregated Options */}
      <Show when={props.aggregatedOptions.length > 0}>
        <div>
          <h3 class="text-xl font-bold text-gray-800 mb-4">
            🤝 Multi-Farmer Options
          </h3>
          <p class="text-sm text-gray-600 mb-4">
            Combine multiple farmers to meet your requirement
          </p>

          <div class="space-y-4">
            <For each={props.aggregatedOptions}>
              {(option) => (
                <div class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                  <div class="flex justify-between items-start mb-4">
                    <div>
                      <div class="flex items-center gap-3 mb-2">
                        <h4 class="text-lg font-semibold text-gray-800">
                          {option.farmers.length} Farmers Combined
                        </h4>
                        <span class={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(option.match_score)}`}>
                          {option.match_score}% Match
                        </span>
                      </div>
                      <p class="text-sm text-gray-600">{option.explanation}</p>
                    </div>
                  </div>

                  <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
                    <div>
                      <p class="text-sm text-gray-500">Total Quantity</p>
                      <p class="text-lg font-semibold text-gray-800">
                        {option.total_quantity.toLocaleString()} kg
                      </p>
                    </div>
                    <div>
                      <p class="text-sm text-gray-500">Average Price</p>
                      <p class="text-lg font-semibold text-gray-800">
                        ₹{option.average_price.toFixed(2)}/kg
                      </p>
                    </div>
                    <div>
                      <p class="text-sm text-gray-500">Estimated Total</p>
                      <p class="text-lg font-semibold text-green-600">
                        ₹{(option.total_quantity * option.average_price).toLocaleString()}
                      </p>
                    </div>
                  </div>

                  {/* Farmer Breakdown */}
                  <div class="bg-gray-50 rounded-lg p-4 mb-4">
                    <p class="text-sm font-medium text-gray-700 mb-3">Farmer Breakdown:</p>
                    <div class="space-y-2">
                      <For each={option.farmers}>
                        {(farmer) => (
                          <div class="flex justify-between items-center text-sm">
                            <span class="text-gray-600">Farmer #{farmer.farmer_id}</span>
                            <span class="text-gray-800">
                              {farmer.quantity.toLocaleString()} kg @ ₹{farmer.price.toFixed(2)}/kg
                            </span>
                          </div>
                        )}
                      </For>
                    </div>
                  </div>

                  <button
                    onClick={() => handleAcceptAggregated(option.group_id)}
                    disabled={accepting() !== null}
                    class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                  >
                    {accepting() === `agg-${option.group_id}` ? 'Accepting...' : 'Accept Combined Match'}
                  </button>
                </div>
              )}
            </For>
          </div>
        </div>
      </Show>

      {/* No Matches */}
      <Show when={props.singleMatches.length === 0 && props.aggregatedOptions.length === 0}>
        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <p class="text-yellow-800 font-medium mb-2">No matches found</p>
          <p class="text-sm text-yellow-700">
            No farmers currently have available supply matching your requirements.
            Try adjusting your criteria or check back later.
          </p>
        </div>
      </Show>
    </div>
  );
};

export default SupplyMatches;

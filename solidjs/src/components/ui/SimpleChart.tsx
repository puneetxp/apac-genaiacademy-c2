import { Component, For } from 'solid-js';

interface DataPoint {
  label: string;
  value: number;
  color?: string;
}

interface SimpleChartProps {
  data: DataPoint[];
  title?: string;
  type?: 'bar' | 'line';
  height?: number;
  showValues?: boolean;
}

const SimpleChart: Component<SimpleChartProps> = (props) => {
  const maxValue = () => Math.max(...props.data.map(d => d.value));
  const height = props.height || 200;

  const getBarHeight = (value: number) => {
    return (value / maxValue()) * (height - 40);
  };

  const defaultColors = [
    '#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6',
    '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#84cc16'
  ];

  return (
    <div class="w-full">
      {props.title && (
        <h4 class="text-sm font-medium text-gray-700 mb-3">{props.title}</h4>
      )}
      
      <div class="relative" style={{ height: `${height}px` }}>
        {/* Y-axis labels */}
        <div class="absolute left-0 top-0 bottom-10 w-12 flex flex-col justify-between text-xs text-gray-500">
          <span>{maxValue().toFixed(0)}</span>
          <span>{(maxValue() * 0.75).toFixed(0)}</span>
          <span>{(maxValue() * 0.5).toFixed(0)}</span>
          <span>{(maxValue() * 0.25).toFixed(0)}</span>
          <span>0</span>
        </div>

        {/* Chart area */}
        <div class="absolute left-14 right-0 top-0 bottom-10">
          {/* Grid lines */}
          <div class="absolute inset-0 flex flex-col justify-between">
            <For each={[0, 1, 2, 3, 4]}>
              {() => <div class="border-t border-gray-200" />}
            </For>
          </div>

          {/* Bars */}
          <div class="absolute inset-0 flex items-end justify-around gap-2">
            <For each={props.data}>
              {(point, index) => (
                <div class="flex-1 flex flex-col items-center">
                  <div
                    class="w-full rounded-t transition-all duration-300 hover:opacity-80 cursor-pointer relative group"
                    style={{
                      height: `${getBarHeight(point.value)}px`,
                      'background-color': point.color || defaultColors[index() % defaultColors.length]
                    }}
                  >
                    {props.showValues && (
                      <div class="absolute -top-6 left-1/2 transform -translate-x-1/2 text-xs font-medium text-gray-700 opacity-0 group-hover:opacity-100 transition-opacity">
                        {point.value.toFixed(0)}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </For>
          </div>
        </div>

        {/* X-axis labels */}
        <div class="absolute left-14 right-0 bottom-0 h-10 flex items-center justify-around gap-2">
          <For each={props.data}>
            {(point) => (
              <div class="flex-1 text-center">
                <span class="text-xs text-gray-600 truncate block">{point.label}</span>
              </div>
            )}
          </For>
        </div>
      </div>
    </div>
  );
};

export default SimpleChart;

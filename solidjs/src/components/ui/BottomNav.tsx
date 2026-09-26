import { Component, Show } from 'solid-js';
import { useDeviceInfo } from '../../utils/useResponsive';

interface NavItem {
  path: string;
  icon: string;
  label: string;
}

/**
 * Mobile-optimized bottom navigation bar
 * Only shows on mobile devices for better UX
 * Uses native anchor tags with history API for client-side navigation
 */
const BottomNav: Component = () => {
  const deviceInfo = useDeviceInfo();

  const navItems: NavItem[] = [
    { path: '/dashboard', icon: '🏠', label: 'Home' },
    { path: '/strategy/request', icon: '🌾', label: 'Strategy' },
    { path: '/livestock', icon: '🐄', label: 'Pashu' },
    { path: '/marketplace', icon: '🛒', label: 'Market' },
    { path: '/farm/register', icon: '🚜', label: 'Farm' },
    { path: '/menu', icon: '☰', label: 'Menu' },
  ];

  const isActive = (path: string) => {
    return window.location.pathname === path || window.location.pathname.startsWith(path + '/');
  };

  const handleClick = (e: MouseEvent, path: string) => {
    e.preventDefault();
    // Use history API for client-side navigation
    window.history.pushState({}, '', path);
    // Dispatch popstate event to trigger router
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  return (
    <Show when={deviceInfo().isMobile}>
      <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 bottom-nav z-50 safe-area-bottom">
        <div class="flex justify-around items-center h-16">
          {navItems.map((item) => (
            <a
              href={item.path}
              onClick={(e) => handleClick(e, item.path)}
              class={`flex flex-col items-center justify-center flex-1 h-full min-w-touch transition-colors no-select ${
                isActive(item.path)
                  ? 'text-primary-600'
                  : 'text-gray-500 active:text-primary-500'
              }`}
              aria-label={item.label}
            >
              <span class="text-2xl mb-1">{item.icon}</span>
              <span class="text-xs font-medium">{item.label}</span>
            </a>
          ))}
        </div>
      </nav>
      {/* Spacer to prevent content from being hidden behind bottom nav */}
      <div class="h-16" />
    </Show>
  );
};

export default BottomNav;

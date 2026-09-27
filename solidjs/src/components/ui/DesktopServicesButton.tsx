/**
 * Desktop Services Button
 * BottomNav is mobile-only, so on larger screens this floating button is the
 * way into every service from any page: it opens the profile drawer, which
 * holds the full searchable services menu.
 */

import { Component, Show, createSignal } from 'solid-js';
import { useLocation } from '@solidjs/router';
import { useDeviceInfo } from '../../utils/useResponsive';
import { isAuthenticated } from '../../stores/auth.store';
import ProfileDrawer from './ProfileDrawer';
import { t } from '../../stores/i18n.store';

const DesktopServicesButton: Component = () => {
  const deviceInfo = useDeviceInfo();
  const location = useLocation();
  const [open, setOpen] = createSignal(false);

  // Nothing to navigate to before sign-in, and the auth pages have their own flow.
  const visible = () =>
    !deviceInfo().isMobile && isAuthenticated() && !location.pathname.startsWith('/auth');

  return (
    <Show when={visible()}>
      <button
        type="button"
        onClick={() => setOpen(true)}
        class="fixed bottom-6 right-6 z-40 px-5 py-3 rounded-full bg-teal-700 hover:bg-teal-800 text-white font-semibold shadow-lg flex items-center gap-2 transition-colors"
        aria-label="All services"
        title="All services"
      >
        <span class="text-lg">☰</span> {t('menu.services')}
      </button>
      <ProfileDrawer open={open()} onClose={() => setOpen(false)} />
    </Show>
  );
};

export default DesktopServicesButton;

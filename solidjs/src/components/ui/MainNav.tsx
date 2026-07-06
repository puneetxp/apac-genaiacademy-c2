import { Component, For, Show } from 'solid-js';
import { A, useLocation } from '@solidjs/router';
import { isAuthenticated } from '../../stores/auth.store';

interface LinkConfig {
  href: string;
  label: string;
  authOnly?: boolean;
}

const linkConfigs: LinkConfig[] = [
  { href: '/', label: 'Home' },
  { href: '/dashboard', label: 'Dashboard', authOnly: true },
  { href: '/marketplace', label: 'Marketplace' },
  { href: '/strategy/request', label: 'Strategy', authOnly: true },
  { href: '/users/profile', label: 'Profile', authOnly: true },
];

const MainNav: Component = () => {
  const location = useLocation();

  const filteredLinks = () =>
    linkConfigs.filter((link) => !link.authOnly || isAuthenticated());

  const isActive = (href: string) => location.pathname.startsWith(href);

  return (
    <header class="bg-white/90 backdrop-blur supports-[backdrop-filter]:backdrop-blur sticky top-0 z-40 border-b border-slate-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <span class="text-2xl" aria-hidden="true">🌱</span>
          <div>
            <p class="text-xs uppercase tracking-widest text-slate-400 font-semibold">
              Rural Farming Platform
            </p>
            <strong class="text-base text-slate-900">Bharat Crop Intelligence</strong>
          </div>
        </div>

        <nav aria-label="Primary" class="hidden md:flex items-center gap-2">
          <For each={filteredLinks()}>
            {(link) => (
              <A
                href={link.href}
                class={`px-4 py-2 rounded-full text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-500 focus-visible:ring-offset-2 ${
                  isActive(link.href)
                    ? 'bg-green-600 text-white shadow-lg'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
                aria-current={isActive(link.href) ? 'page' : undefined}
              >
                {link.label}
              </A>
            )}
          </For>
        </nav>

        <div class="ml-auto md:ml-0 flex items-center gap-2">
          <Show when={!isAuthenticated()}>
            <A
              href="/auth/signin"
              class="px-4 py-2 text-sm font-semibold text-slate-700 rounded-full hover:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-slate-400"
            >
              Sign In
            </A>
            <A
              href="/auth/signup"
              class="px-4 py-2 text-sm font-semibold bg-slate-900 text-white rounded-full hover:bg-black focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-slate-900"
            >
              Get Started
            </A>
          </Show>
          <Show when={isAuthenticated()}>
            <A
              href="/users/profile"
              class="px-4 py-2 text-sm font-semibold bg-slate-900 text-white rounded-full hover:bg-black focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-slate-900"
            >
              View Profile
            </A>
          </Show>
        </div>
      </div>
    </header>
  );
};

export default MainNav;

/**
 * All Services (/menu)
 * Full-page menu of every service in the app, grouped by area.
 */

import { Component } from 'solid-js';
import ServicesMenu from '../components/ui/ServicesMenu';
import LanguageSwitcher from '../components/ui/LanguageSwitcher';
import { t } from '../stores/i18n.store';

const AllServices: Component = () => (
    <div class="min-h-screen bg-gray-50 pb-24">
        <header class="bg-white shadow sticky top-0 z-10 px-4 sm:px-6 lg:px-8 py-4">
            <div class="max-w-7xl mx-auto flex justify-between items-center gap-3">
                <div>
                <h1 class="text-2xl font-bold text-gray-900">{t('menu.title')}</h1>
                <p class="text-sm text-gray-600 mt-1">{t('menu.subtitle')}</p>
                </div>
                <LanguageSwitcher />
            </div>
        </header>
        <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <ServicesMenu variant="grid" searchable />
        </main>
    </div>
);

export default AllServices;

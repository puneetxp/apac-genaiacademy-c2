/**
 * All Services (/menu)
 * Full-page menu of every service in the app, grouped by area.
 */

import { Component } from 'solid-js';
import ServicesMenu from '../components/ui/ServicesMenu';

const AllServices: Component = () => (
    <div class="min-h-screen bg-slate-100 pb-24">
        <header class="bg-teal-700 text-white px-4 pt-5 pb-4 shadow">
            <div class="max-w-3xl mx-auto">
                <h1 class="text-2xl font-bold">सभी सेवाएं</h1>
                <p class="text-sm text-teal-100">पशु, खेती, बाज़ार — सब एक जगह</p>
            </div>
        </header>
        <main class="max-w-3xl mx-auto px-4 pt-4">
            <ServicesMenu variant="grid" searchable />
        </main>
    </div>
);

export default AllServices;

/**
 * Profile Drawer
 * Slides in from the right when the profile avatar is tapped: who is signed
 * in, quick account links, every service in the app, and sign out.
 */

import { Component, Show, createEffect, onCleanup } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import { FiX, FiLogOut, FiChevronRight } from 'solid-icons/fi';
import { user, signOut } from '../../stores/auth.store';
import ServicesMenu from './ServicesMenu';

interface ProfileDrawerProps {
    open: boolean;
    onClose: () => void;
}

const ProfileDrawer: Component<ProfileDrawerProps> = (props) => {
    const navigate = useNavigate();

    // While open: Escape closes, and the page behind doesn't scroll
    createEffect(() => {
        if (!props.open) return;
        const onKey = (e: KeyboardEvent) => e.key === 'Escape' && props.onClose();
        const prevOverflow = document.body.style.overflow;
        document.body.style.overflow = 'hidden';
        window.addEventListener('keydown', onKey);
        onCleanup(() => {
            document.body.style.overflow = prevOverflow;
            window.removeEventListener('keydown', onKey);
        });
    });

    const handleSignOut = async () => {
        props.onClose();
        await signOut();
        navigate('/auth/signin');
    };

    return (
        <Show when={props.open}>
            <div class="fixed inset-0 z-[60] flex justify-end">
                <div class="absolute inset-0 bg-black/40" onClick={props.onClose} />
                <aside role="dialog" aria-modal="true" aria-label="सभी सेवाएं" class="relative w-[88%] max-w-sm h-full bg-slate-100 overflow-y-auto shadow-2xl animate-[slideIn_.2s_ease-out]">
                    {/* Profile header */}
                    <div class="bg-teal-700 text-white px-4 pt-6 pb-5">
                        <div class="flex justify-end">
                            <button onClick={props.onClose} class="p-2 -mr-2 text-2xl" aria-label="बंद करें">
                                <FiX />
                            </button>
                        </div>
                        <button
                            onClick={() => { navigate('/users/profile'); props.onClose(); }}
                            class="w-full flex items-center gap-3 text-left"
                        >
                            <span class="w-14 h-14 rounded-full bg-amber-100 text-3xl flex items-center justify-center border-2 border-white">
                                👳
                            </span>
                            <span class="flex-1 min-w-0">
                                <span class="block text-lg font-bold truncate">{user()?.full_name || 'किसान भाई'}</span>
                                <span class="block text-sm text-teal-100 truncate">{user()?.phone_number || user()?.email || 'प्रोफ़ाइल देखें'}</span>
                            </span>
                            <FiChevronRight class="text-xl" />
                        </button>
                    </div>

                    <div class="p-4 space-y-5">
                        <h2 class="text-lg font-bold text-slate-800">सभी सेवाएं</h2>
                        <ServicesMenu variant="list" searchable onNavigate={props.onClose} />

                        <button
                            onClick={handleSignOut}
                            class="w-full flex items-center justify-center gap-2 py-3 rounded-2xl bg-white text-rose-600 font-semibold border border-rose-100"
                        >
                            <FiLogOut /> लॉग आउट
                        </button>
                    </div>
                </aside>
            </div>
        </Show>
    );
};

export default ProfileDrawer;

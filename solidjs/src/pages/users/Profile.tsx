/**
 * User Profile Page
 * Premium interface for managing personal information and account status
 */

import { Component, createResource, createSignal, Show } from 'solid-js';
import { A } from '@solidjs/router';
import { user } from '../../stores/auth.store';
import { UserService } from '../../services/user.service';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { ErrorDisplay } from '../../components/ui/ErrorDisplay';
import { showToast } from '../../components/ui/Toast';
import ServicesMenu from '../../components/ui/ServicesMenu';

const Profile: Component = () => {
    const [isEditing, setIsEditing] = createSignal(false);
    const [fullName, setFullName] = createSignal(user()?.full_name || '');
    const [phone, setPhone] = createSignal(user()?.phone_number || '');
    const [language, setLanguage] = createSignal(user()?.language_preference || 'en');

    const [profile, { mutate, refetch }] = createResource(UserService.getProfile);

    const handleUpdate = async (e: Event) => {
        e.preventDefault();
        try {
            const updatedUser = await UserService.updateProfile({
                full_name: fullName(),
                phone_number: phone(),
                language_preference: language()
            });
            showToast('success', 'Profile updated successfully');
            setIsEditing(false);
            refetch();
        } catch (err) {
            showToast('error', 'Failed to update profile');
        }
    };

    return (
        <div class="min-h-screen bg-slate-50 pb-20">
            {/* Premium Header with Gradient */}
            <div class="bg-gradient-to-r from-green-600 to-teal-700 pt-12 pb-24 px-4 sm:px-6 lg:px-8 shadow-lg">
                <div class="max-w-4xl mx-auto flex flex-col md:flex-row items-center gap-6">
                    <div class="w-24 h-24 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center text-4xl border-2 border-white/30 shadow-xl">
                        👤
                    </div>
                    <div class="text-center md:text-left">
                        <h1 class="text-3xl font-extrabold text-white tracking-tight">
                            {profile()?.user.full_name || user()?.full_name || 'Your Profile'}
                        </h1>
                        <p class="text-green-100 font-medium opacity-90">
                            {profile()?.user.user_type.toUpperCase()} • {profile()?.user.username}
                        </p>
                    </div>
                    <div class="md:ml-auto flex gap-3">
                        <A
                            href="/users/security"
                            class="px-4 py-2 bg-white/10 hover:bg-white/20 backdrop-blur-sm text-white rounded-lg border border-white/20 transition-all font-medium text-sm flex items-center gap-2"
                        >
                            🔒 Security
                        </A>
                        <button
                            onClick={() => setIsEditing(!isEditing())}
                            class={`px-4 py-2 ${isEditing() ? 'bg-amber-500 hover:bg-amber-600' : 'bg-white text-green-700 hover:bg-green-50'} rounded-lg transition-all font-bold text-sm shadow-md flex items-center gap-2`}
                        >
                            {isEditing() ? 'Cancel' : 'Edit Profile'}
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Content - Overlapping Card */}
            <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 -mt-12">
                <Show when={!profile.loading} fallback={<LoadingSpinner />}>
                    <Show when={!profile.error} fallback={<ErrorDisplay error={profile.error} onRetry={refetch} />}>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">

                            {/* Left Column: Stats/Status */}
                            <div class="space-y-6">
                                <div class="bg-white rounded-2xl shadow-xl p-6 border border-slate-200">
                                    <h3 class="font-bold text-slate-800 mb-4 flex items-center gap-2">
                                        <span class="text-green-600">📊</span> Account Status
                                    </h3>
                                    <div class="space-y-4">
                                        <div class="flex justify-between items-center">
                                            <span class="text-slate-500 text-sm">Status</span>
                                            <span class={`text-xs px-2 py-1 rounded-full font-bold ${profile()?.user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                                {profile()?.user.is_active ? 'ACTIVE' : 'INACTIVE'}
                                            </span>
                                        </div>
                                        <div class="flex justify-between items-center">
                                            <span class="text-slate-500 text-sm">Email</span>
                                            <span class={`text-xs px-2 py-1 rounded-full font-bold ${profile()?.user.is_verified ? 'bg-blue-100 text-blue-700' : 'bg-amber-100 text-amber-700'}`}>
                                                {profile()?.user.is_verified ? 'VERIFIED' : 'PENDING'}
                                            </span>
                                        </div>
                                        <div class="flex justify-between items-center">
                                            <span class="text-slate-500 text-sm">Member Since</span>
                                            <span class="text-slate-800 text-xs font-medium">March 2024</span>
                                        </div>
                                    </div>
                                </div>

                                <div class="bg-gradient-to-br from-indigo-600 to-blue-700 rounded-2xl shadow-xl p-6 text-white overflow-hidden relative">
                                    <div class="relative z-10">
                                        <h3 class="font-bold mb-2">Platform Quota</h3>
                                        <p class="text-indigo-100 text-sm mb-4">You have used 15% of your AI capacity for this month.</p>
                                        <div class="w-full bg-white/20 rounded-full h-2 mb-4">
                                            <div class="bg-white h-full rounded-full" style="width: 15%"></div>
                                        </div>
                                        <A href="/quota/history" class="text-xs font-bold underline decoration-white/30 hover:decoration-white transition-all">View Details</A>
                                    </div>
                                    <div class="absolute -right-4 -bottom-4 text-7xl opacity-10">📈</div>
                                </div>
                            </div>

                            {/* Middle/Right Column: Main Form */}
                            <div class="md:col-span-2">
                                <div class="bg-white rounded-2xl shadow-xl p-8 border border-slate-200 overflow-hidden relative">
                                    <div class="absolute top-0 right-0 p-4 opacity-5 text-8xl pointer-events-none">🌿</div>

                                    <h2 class="text-xl font-bold text-slate-900 mb-8 border-b pb-4">Personal Details</h2>

                                    <form onSubmit={handleUpdate} class="space-y-6">
                                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
                                            <div class="space-y-2">
                                                <label class="text-sm font-bold text-slate-700 ml-1">Full Name</label>
                                                <input
                                                    type="text"
                                                    value={fullName()}
                                                    onInput={(e) => setFullName(e.currentTarget.value)}
                                                    disabled={!isEditing()}
                                                    class={`w-full px-4 py-3 rounded-xl border ${isEditing() ? 'border-green-200 bg-white ring-4 ring-green-500/10' : 'border-slate-100 bg-slate-50 cursor-not-allowed'} transition-all outline-none text-slate-800`}
                                                />
                                            </div>
                                            <div class="space-y-2">
                                                <label class="text-sm font-bold text-slate-700 ml-1">Email Address</label>
                                                <input
                                                    type="email"
                                                    value={profile()?.user.email || ''}
                                                    disabled
                                                    class="w-full px-4 py-3 rounded-xl border border-slate-100 bg-slate-50 cursor-not-allowed transition-all text-slate-500"
                                                />
                                                <p class="text-[10px] text-slate-400 italic mt-1 ml-1">* Email changes require security verification</p>
                                            </div>
                                            <div class="space-y-2">
                                                <label class="text-sm font-bold text-slate-700 ml-1">Phone Number</label>
                                                <input
                                                    type="text"
                                                    value={phone()}
                                                    onInput={(e) => setPhone(e.currentTarget.value)}
                                                    disabled={!isEditing()}
                                                    class={`w-full px-4 py-3 rounded-xl border ${isEditing() ? 'border-green-200 bg-white ring-4 ring-green-500/10' : 'border-slate-100 bg-slate-50 cursor-not-allowed'} transition-all outline-none text-slate-800`}
                                                />
                                            </div>
                                            <div class="space-y-2">
                                                <label class="text-sm font-bold text-slate-700 ml-1">Language Preference</label>
                                                <select
                                                    value={language()}
                                                    onChange={(e) => setLanguage(e.currentTarget.value)}
                                                    disabled={!isEditing()}
                                                    class={`w-full px-4 py-3 rounded-xl border ${isEditing() ? 'border-green-200 bg-white ring-4 ring-green-500/10' : 'border-slate-100 bg-slate-50 cursor-not-allowed'} transition-all outline-none text-slate-800 font-medium`}
                                                >
                                                    <option value="en">English</option>
                                                    <option value="hi">Hindi (हिन्दी)</option>
                                                    <option value="mr">Marathi (मराठी)</option>
                                                    <option value="pa">Punjabi (ਪੰਜਾਬੀ)</option>
                                                </select>
                                            </div>
                                        </div>

                                        <div class="pt-6 flex justify-end">
                                            <Show when={isEditing()}>
                                                <button
                                                    type="submit"
                                                    class="px-8 py-3 bg-green-600 hover:bg-green-700 text-white rounded-xl shadow-lg transition-all transform hover:scale-105 font-bold"
                                                >
                                                    Save Changes
                                                </button>
                                            </Show>
                                        </div>
                                    </form>
                                </div>

                                {/* Additional Info / Tags */}
                                <div class="mt-8 grid grid-cols-2 sm:grid-cols-4 gap-4">
                                    <div class="bg-indigo-50 border border-indigo-100 rounded-xl p-4 text-center group hover:bg-indigo-100 transition-all">
                                        <div class="text-2xl mb-1">🏙️</div>
                                        <p class="text-[10px] text-indigo-400 font-bold uppercase tracking-wider">Region</p>
                                        <p class="text-sm font-bold text-indigo-900">Maharashtra</p>
                                    </div>
                                    <div class="bg-emerald-50 border border-emerald-100 rounded-xl p-4 text-center group hover:bg-emerald-100 transition-all">
                                        <div class="text-2xl mb-1">🌾</div>
                                        <p class="text-[10px] text-emerald-400 font-bold uppercase tracking-wider">Activity</p>
                                        <p class="text-sm font-bold text-emerald-900">Heavy</p>
                                    </div>
                                    <div class="bg-amber-50 border border-amber-100 rounded-xl p-4 text-center group hover:bg-amber-100 transition-all">
                                        <div class="text-2xl mb-1">⭐</div>
                                        <p class="text-[10px] text-amber-400 font-bold uppercase tracking-wider">Rating</p>
                                        <p class="text-sm font-bold text-amber-900">4.9/5</p>
                                    </div>
                                    <div class="bg-rose-50 border border-rose-100 rounded-xl p-4 text-center group hover:bg-rose-100 transition-all">
                                        <div class="text-2xl mb-1">🔗</div>
                                        <p class="text-[10px] text-rose-400 font-bold uppercase tracking-wider">Connected</p>
                                        <p class="text-sm font-bold text-rose-900">3 Apps</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* All services */}
                        <div class="mt-8 bg-slate-100 rounded-2xl p-4 sm:p-6 border border-slate-200">
                            <h2 class="text-xl font-bold text-slate-900 mb-4">सभी सेवाएं <span class="text-sm font-medium text-slate-500">· All services</span></h2>
                            <ServicesMenu variant="grid" />
                        </div>
                    </Show>
                </Show>
            </main>
        </div>
    );
};

export default Profile;

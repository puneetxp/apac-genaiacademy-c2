/**
 * Security Settings Page
 * Interface for password changes, MFA management, and login session overview
 */

import { Component, createResource, createSignal, Show } from 'solid-js';
import { A } from '@solidjs/router';
import { user } from '../../stores/auth.store';
import { UserService } from '../../services/user.service';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { showToast } from '../../components/ui/Toast';

const Security: Component = () => {
    const [prevPassword, setPrevPassword] = createSignal('');
    const [newPassword, setNewPassword] = createSignal('');
    const [confirmPassword, setConfirmPassword] = createSignal('');
    const [isChangingPassword, setIsChangingPassword] = createSignal(false);

    const [profile, { refetch }] = createResource(UserService.getProfile);

    const handlePasswordChange = async (e: Event) => {
        e.preventDefault();
        if (newPassword() !== confirmPassword()) {
            showToast('error', 'New passwords do not match');
            return;
        }

        setIsChangingPassword(true);
        try {
            await UserService.changePassword({
                previous_password: prevPassword(),
                proposed_password: newPassword()
            });
            showToast('success', 'Password changed successfully');
            setPrevPassword('');
            setNewPassword('');
            setConfirmPassword('');
        } catch (err) {
            showToast('error', 'Failed to change password');
        } finally {
            setIsChangingPassword(false);
        }
    };

    const toggleMFA = async () => {
        const isMFAEnabled = profile()?.cognito_attributes?.UserMFASettingList?.includes('SMS_MFA');
        try {
            if (isMFAEnabled) {
                await UserService.disableMFA();
                showToast('success', 'MFA disabled successfully');
            } else {
                await UserService.enableMFA();
                showToast('success', 'MFA enabled successfully');
            }
            refetch();
        } catch (err) {
            showToast('error', 'Failed to update MFA settings');
        }
    };

    return (
        <div class="min-h-screen bg-slate-50 pb-20">
            <div class="bg-gradient-to-r from-slate-800 to-indigo-900 pt-12 pb-24 px-4 sm:px-6 lg:px-8 shadow-lg">
                <div class="max-w-4xl mx-auto flex items-center gap-6">
                    <A href="/users/profile" class="w-12 h-12 rounded-xl bg-white/10 backdrop-blur-md flex items-center justify-center text-xl border border-white/20 hover:bg-white/20 transition-all text-white">
                        ←
                    </A>
                    <div>
                        <h1 class="text-3xl font-extrabold text-white tracking-tight">Security Settings</h1>
                        <p class="text-indigo-100 font-medium opacity-90">Protect your account and managed sessions</p>
                    </div>
                </div>
            </div>

            <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 -mt-12">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">

                    {/* Factor Authentication Card */}
                    <div class="space-y-8">
                        <div class="bg-white rounded-2xl shadow-xl p-8 border border-slate-200">
                            <div class="flex items-center justify-between mb-6">
                                <h3 class="font-bold text-slate-800 flex items-center gap-2 text-lg">
                                    <span class="text-indigo-600">📱</span> Multi-Factor Auth
                                </h3>
                                <Show when={!profile.loading} fallback={<LoadingSpinner size="sm" />}>
                                    <div class={`px-2 py-1 rounded-md text-[10px] font-black tracking-widest ${profile()?.cognito_attributes?.UserMFASettingList?.includes('SMS_MFA') ? 'bg-green-500 text-white' : 'bg-slate-200 text-slate-500'}`}>
                                        {profile()?.cognito_attributes?.UserMFASettingList?.includes('SMS_MFA') ? 'ENABLED' : 'DISABLED'}
                                    </div>
                                </Show>
                            </div>
                            <p class="text-slate-600 text-sm mb-6 leading-relaxed">
                                Add an extra layer of security to your account by requiring a code sent to your phone number (+91 {user()?.phone_number}) during sign in.
                            </p>
                            <button
                                onClick={toggleMFA}
                                disabled={profile.loading}
                                class={`w-full py-4 rounded-xl font-bold transition-all shadow-md ${profile()?.cognito_attributes?.UserMFASettingList?.includes('SMS_MFA') ? 'bg-slate-100 text-slate-600 hover:bg-slate-200' : 'bg-indigo-600 text-white hover:bg-indigo-700'}`}
                            >
                                {profile()?.cognito_attributes?.UserMFASettingList?.includes('SMS_MFA') ? 'Disable MFA' : 'Enable MFA'}
                            </button>
                        </div>

                        <div class="bg-white rounded-2xl shadow-xl p-8 border border-slate-200">
                            <h3 class="font-bold text-slate-800 flex items-center gap-2 text-lg mb-6">
                                <span class="text-blue-600">📡</span> Login Sessions
                            </h3>
                            <div class="space-y-4">
                                <div class="p-4 bg-blue-50/50 rounded-xl border border-blue-100 flex items-center gap-4">
                                    <div class="text-2xl">💻</div>
                                    <div>
                                        <p class="text-sm font-bold text-slate-800">Chrome on macOS</p>
                                        <p class="text-[10px] text-blue-500 font-medium">Currently Active • Mumbai, India</p>
                                    </div>
                                </div>
                                <button class="w-full py-3 text-xs font-bold text-rose-600 hover:bg-rose-50 rounded-lg transition-all border border-rose-100 italic">
                                    Log out of all other sessions
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Change Password Card */}
                    <div class="bg-white rounded-2xl shadow-xl p-8 border border-slate-200 relative overflow-hidden">
                        <div class="absolute -right-10 -bottom-10 p-4 opacity-5 text-9xl pointer-events-none select-none italic font-black">PWD</div>

                        <h3 class="font-bold text-slate-800 flex items-center gap-2 text-lg mb-8">
                            <span class="text-emerald-600">🔑</span> Change Password
                        </h3>

                        <form onSubmit={handlePasswordChange} class="space-y-6">
                            <div class="space-y-2">
                                <label class="text-xs font-bold text-slate-500 ml-1 uppercase tracking-wider">Current Password</label>
                                <input
                                    type="password"
                                    value={prevPassword()}
                                    onInput={(e) => setPrevPassword(e.currentTarget.value)}
                                    required
                                    placeholder="••••••••"
                                    class="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-200 transition-all text-slate-800"
                                />
                            </div>
                            <div class="space-y-2">
                                <label class="text-xs font-bold text-slate-500 ml-1 uppercase tracking-wider">New Password</label>
                                <input
                                    type="password"
                                    value={newPassword()}
                                    onInput={(e) => setNewPassword(e.currentTarget.value)}
                                    required
                                    placeholder="••••••••"
                                    class="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-200 transition-all text-slate-800"
                                />
                            </div>
                            <div class="space-y-2">
                                <label class="text-xs font-bold text-slate-500 ml-1 uppercase tracking-wider">Confirm New Password</label>
                                <input
                                    type="password"
                                    value={confirmPassword()}
                                    onInput={(e) => setConfirmPassword(e.currentTarget.value)}
                                    required
                                    placeholder="••••••••"
                                    class="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-200 transition-all text-slate-800"
                                />
                            </div>

                            <div class="p-4 bg-amber-50 rounded-xl border border-amber-100">
                                <p class="text-[10px] text-amber-700 leading-relaxed font-medium">
                                    <span class="font-bold">Recommendation:</span> Use at least 12 characters, including numbers and symbols for better security.
                                </p>
                            </div>

                            <button
                                type="submit"
                                disabled={isChangingPassword()}
                                class={`w-full py-4 ${isChangingPassword() ? 'bg-slate-400' : 'bg-emerald-600 hover:bg-emerald-700 shadow-emerald-200/50'} text-white rounded-xl shadow-lg transition-all transform hover:scale-[1.02] font-extrabold flex items-center justify-center gap-2`}
                            >
                                <Show when={isChangingPassword()}><LoadingSpinner size="sm" /></Show>
                                Update Password
                            </button>
                        </form>
                    </div>

                </div>
            </main>
        </div>
    );
};

export default Security;

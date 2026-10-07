/**
 * Farm journey (Dashboard)
 * The whole season as one strip: land → soil → plan → sow → protect → harvest
 * → sell, with livestock alongside. Each stage shows where the farmer is from
 * their own data and links to the next thing to do, so the dashboard covers
 * every process, not only one of them.
 */

import { Component, For, createResource } from 'solid-js';
import { A } from '@solidjs/router';
import { t } from '../../stores/i18n.store';
import type { TKey } from '../../i18n/en';
import { user } from '../../stores/auth.store';
import { BoardService } from '../../services/board.service';
import type { DashboardData } from '../../services/dashboard.service';

type Status = 'done' | 'active' | 'todo';

interface Stage {
    id: string;
    icon: string;
    status: Status;
    /** Short fact from the farmer's data, e.g. "2 farms" */
    detail: string;
    href: string;
}

interface Props {
    farms: any[];
    hasStrategies: boolean;
    data?: DashboardData;
}

const STYLE: Record<Status, string> = {
    done: 'border-green-300 bg-green-50',
    active: 'border-amber-300 bg-amber-50',
    todo: 'border-gray-200 bg-white',
};
const BADGE: Record<Status, string> = { done: '✓', active: '●', todo: '○' };
const BADGE_STYLE: Record<Status, string> = { done: 'text-green-700', active: 'text-amber-600', todo: 'text-gray-400' };

const FarmJourney: Component<Props> = (props) => {
    const [livestock] = createResource(() => user()?.id, (id) => BoardService.getLivestock(id));

    const stages = (): Stage[] => {
        const farms = props.farms || [];
        const crops = props.data?.active_crops || [];
        const alerts = props.data?.weather_alerts || [];
        const listings = props.data?.active_listings || [];
        const buyers = props.data?.buyer_interests || [];
        const tested = farms.filter((f) => f.ph_level || f.nitrogen || f.primary_soil_type).length;
        const dueSoon = crops.filter((c) => Number(c.days_until_harvest) <= 14).length;
        const heads = (livestock() || []).reduce((sum, l) => sum + (Number(l.quantity) || 0), 0);
        const n = (key: TKey, count: number) => t(key, { n: String(count) });

        return [
            { id: 'land', icon: '🏡', href: farms.length ? '/farm' : '/farm/register',
              status: farms.length ? 'done' : 'active', detail: farms.length ? n('journey.farms', farms.length) : t('journey.start') },
            { id: 'soil', icon: '🧪', href: '/soil/hub',
              status: !farms.length ? 'todo' : tested === farms.length ? 'done' : 'active',
              detail: farms.length ? n('journey.tested', tested) : '—' },
            { id: 'plan', icon: '📋', href: '/strategy/select-farm',
              status: props.hasStrategies ? 'done' : farms.length ? 'active' : 'todo',
              detail: props.hasStrategies ? t('journey.planReady') : t('journey.aiPlan') },
            { id: 'sow', icon: '🌱', href: '/crops/plant',
              status: crops.length ? 'done' : farms.length ? 'active' : 'todo',
              detail: n('journey.crops', crops.length) },
            { id: 'protect', icon: '🛡️', href: alerts.length ? '/climate/hub' : '/diagnose',
              status: !crops.length ? 'todo' : alerts.length ? 'active' : 'done',
              detail: alerts.length ? n('journey.alerts', alerts.length) : t('journey.noAlerts') },
            { id: 'harvest', icon: '🌾', href: '/crops/my-crops',
              status: dueSoon ? 'active' : crops.length ? 'done' : 'todo',
              detail: dueSoon ? n('journey.dueSoon', dueSoon) : '—' },
            { id: 'sell', icon: '🛒', href: '/marketplace/my-listings',
              status: listings.length ? 'done' : dueSoon || crops.length ? 'active' : 'todo',
              detail: listings.length ? n('journey.listings', listings.length) + (buyers.length ? ` · ${n('journey.buyers', buyers.length)}` : '') : '—' },
            { id: 'livestock', icon: '🐄', href: '/livestock',
              status: heads ? 'done' : 'todo', detail: livestock.loading ? '…' : n('journey.animals', heads) },
        ];
    };

    return (
        <section class="bg-white rounded-lg shadow p-4 sm:p-5" aria-label={t('journey.title')}>
            <div class="flex items-baseline justify-between gap-2 mb-3">
                <h2 class="text-lg font-semibold text-gray-900">{t('journey.title')}</h2>
                <span class="text-xs text-gray-500">{t('journey.hint')}</span>
            </div>
            <ol class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
                <For each={stages()}>
                    {(s) => (
                        <li>
                            <A href={s.href} class={`block h-full rounded-lg border p-3 hover:shadow-sm transition-shadow ${STYLE[s.status]}`}>
                                <div class="flex items-center justify-between">
                                    <span class="text-xl" aria-hidden="true">{s.icon}</span>
                                    <span class={`text-sm font-bold ${BADGE_STYLE[s.status]}`} title={t(`journey.status.${s.status}` as TKey)}>
                                        {BADGE[s.status]}
                                    </span>
                                </div>
                                <p class="mt-1 text-sm font-semibold text-gray-900">{t(`journey.${s.id}` as TKey)}</p>
                                <p class="text-xs text-gray-600 truncate">{s.detail}</p>
                            </A>
                        </li>
                    )}
                </For>
            </ol>
        </section>
    );
};

export default FarmJourney;

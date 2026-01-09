/**
 * DashboardGrid - Dashboard Menu Cards Grid
 * 
 * Displays 6 main dashboard sections as interactive cards:
 * - Ingestion: Data ingestion management
 * - Funding Sources: Funding opportunities tracking
 * - Clients: Client relationship management
 * - Interactions: Client interaction history
 * - Portfolio: Institutes and projects portfolio
 * - Opportunities: Pipeline and opportunities
 * 
 * @example
 * <DashboardGrid />
 */

'use client';

import Link from 'next/link';
import { useI18n } from '@/lib/hooks/useI18n';

interface DashboardCard {
  href: string;
  titleKey: string;
  descriptionKey: string;
  icon: string;
  color: string;
}

const DASHBOARD_CARDS: DashboardCard[] = [
  {
    href: '/dashboard/ingestion',
    titleKey: 'ingestion.title',
    descriptionKey: 'ingestion.description',
    icon: '📥',
    color: 'from-blue-500 to-blue-600',
  },
  {
    href: '/dashboard/funding-sources',
    titleKey: 'funding_sources.title',
    descriptionKey: 'funding_sources.description',
    icon: '💰',
    color: 'from-green-500 to-green-600',
  },
  {
    href: '/dashboard/clients',
    titleKey: 'clients.title',
    descriptionKey: 'clients.description',
    icon: '👤',
    color: 'from-purple-500 to-purple-600',
  },
  {
    href: '/dashboard/interactions',
    titleKey: 'interactions.title',
    descriptionKey: 'interactions.description',
    icon: '💬',
    color: 'from-orange-500 to-orange-600',
  },
  {
    href: '/dashboard/portfolio',
    titleKey: 'portfolio.title',
    descriptionKey: 'portfolio.description',
    icon: '📁',
    color: 'from-indigo-500 to-indigo-600',
  },
  {
    href: '/dashboard/opportunities',
    titleKey: 'opportunities.title',
    descriptionKey: 'opportunities.description',
    icon: '🚀',
    color: 'from-pink-500 to-pink-600',
  },
];

export function DashboardGrid() {
  const { t } = useI18n();

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {DASHBOARD_CARDS.map((card) => (
        <Link
          key={card.href}
          href={card.href}
          className="group relative overflow-hidden rounded-lg bg-white shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
        >
          <div className={`absolute inset-0 bg-gradient-to-br ${card.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />
          
          <div className="relative p-6">
            <div className="flex items-start justify-between mb-4">
              <span className="text-4xl" role="img" aria-label={t(card.titleKey)}>
                {card.icon}
              </span>
              <svg
                className="w-5 h-5 text-gray-400 group-hover:text-gray-600 transition-colors"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </div>
            
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {t(card.titleKey)}
            </h3>
            
            <p className="text-sm text-gray-600">
              {t(card.descriptionKey)}
            </p>
          </div>
          
          <div className={`h-1 bg-gradient-to-r ${card.color}`} />
        </Link>
      ))}
    </div>
  );
}

/**
 * AdminGrid - Administration Menu Cards Grid
 * 
 * Displays 3 administration sections as interactive cards:
 * - Settings: System configuration and preferences
 * - ACL: Access control list and permissions management
 * - Translations: i18n translation management
 * 
 * @example
 * <AdminGrid />
 */

'use client';

import Link from 'next/link';
import { useI18n } from '@/lib/hooks/useI18n';

interface AdminCard {
  href: string;
  titleKey: string;
  descriptionKey: string;
  icon: string;
  color: string;
}

const ADMIN_CARDS: AdminCard[] = [
  {
    href: '/admin/model-configs',
    titleKey: 'admin.model_config.title',
    descriptionKey: 'admin.model_config.description',
    icon: '⚙️',
    color: 'from-gray-500 to-gray-600',
  },
  {
    href: '/admin/acl',
    titleKey: 'admin.acl.title',
    descriptionKey: 'admin.acl.description',
    icon: '🔒',
    color: 'from-red-500 to-red-600',
  },
  {
    href: '/admin/translations',
    titleKey: 'admin.translations.title',
    descriptionKey: 'admin.translations.description',
    icon: '🌐',
    color: 'from-blue-500 to-blue-600',
  },
];

export function AdminGrid() {
  const { t } = useI18n();

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {ADMIN_CARDS.map((card) => (
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

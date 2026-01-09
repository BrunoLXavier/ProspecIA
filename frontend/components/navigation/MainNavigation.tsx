/**
 * MainNavigation - Main Navigation Component with Active State
 * 
 * Provides navigation between Dashboard and Admin sections with:
 * - Active route highlighting using Next.js usePathname()
 * - Responsive design with mobile menu support
 * - ACL-aware menu items (future enhancement)
 * 
 * @example
 * <MainNavigation />
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useI18n } from '@/lib/hooks/useI18n';
import { useState } from 'react';

interface NavigationItem {
  href: string;
  labelKey: string;
  icon: string;
  children?: NavigationItem[];
}

const NAVIGATION_ITEMS: NavigationItem[] = [
  {
    href: '/dashboard',
    labelKey: 'nav.dashboard',
    icon: '🏠',
    children: [
      { href: '/dashboard/ingestion', labelKey: 'ingestion.title', icon: '📥' },
      { href: '/dashboard/funding-sources', labelKey: 'funding_sources.title', icon: '💰' },
      { href: '/dashboard/clients', labelKey: 'clients.title', icon: '👤' },
      { href: '/dashboard/interactions', labelKey: 'interactions.title', icon: '💬' },
      { href: '/dashboard/portfolio', labelKey: 'portfolio.title', icon: '📁' },
      { href: '/dashboard/opportunities', labelKey: 'opportunities.title', icon: '🚀' },
    ],
  },
  {
    href: '/admin',
    labelKey: 'nav.admin',
    icon: '⚙️',
    children: [
      { href: '/admin/model-configs', labelKey: 'admin.model_config.title', icon: '⚙️' },
      { href: '/admin/acl', labelKey: 'admin.acl.title', icon: '🔒' },
      { href: '/admin/translations', labelKey: 'admin.translations.title', icon: '🌐' },
    ],
  },
];

export function MainNavigation() {
  const pathname = usePathname();
  const { t } = useI18n();
  const [expandedSections, setExpandedSections] = useState<string[]>(['/dashboard', '/admin']);

  const toggleSection = (href: string) => {
    setExpandedSections((prev) =>
      prev.includes(href) ? prev.filter((item) => item !== href) : [...prev, href]
    );
  };

  const isActive = (href: string) => {
    if (href === '/dashboard' || href === '/admin') {
      return pathname === href;
    }
    return pathname?.startsWith(href);
  };

  const isParentActive = (item: NavigationItem) => {
    if (pathname === item.href) return true;
    return item.children?.some((child) => pathname?.startsWith(child.href)) || false;
  };

  return (
    <nav className="w-64 bg-white shadow-lg min-h-screen">
      <div className="p-6">


        <ul className="space-y-2">
          {NAVIGATION_ITEMS.map((item) => {
            const parentActive = isParentActive(item);
            const expanded = expandedSections.includes(item.href);

            return (
              <li key={item.href}>
                {/* Parent Item */}
                <div className="flex items-center">
                  <Link
                    href={item.href}
                    className={`flex-1 flex items-center space-x-3 px-4 py-2 rounded-lg transition-colors ${
                      isActive(item.href)
                        ? 'bg-blue-100 text-blue-700 font-semibold border-l-4 border-blue-600'
                        : parentActive
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <span className="text-xl">{item.icon}</span>
                    <span>{t(item.labelKey)}</span>
                  </Link>
                  
                  {item.children && (
                    <button
                      onClick={() => toggleSection(item.href)}
                      className="p-2 text-gray-500 hover:text-gray-700"
                      aria-label={expanded ? 'Collapse' : 'Expand'}
                    >
                      <svg
                        className={`w-4 h-4 transition-transform ${
                          expanded ? 'rotate-180' : ''
                        }`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 9l-7 7-7-7"
                        />
                      </svg>
                    </button>
                  )}
                </div>

                {/* Children Items */}
                {item.children && expanded && (
                  <ul className="ml-4 mt-1 space-y-1">
                    {item.children.map((child) => (
                      <li key={child.href}>
                        <Link
                          href={child.href}
                          className={`flex items-center space-x-3 px-4 py-2 rounded-lg transition-colors ${
                            isActive(child.href)
                              ? 'bg-blue-100 text-blue-700 font-semibold border-l-4 border-blue-600'
                              : 'text-gray-600 hover:bg-gray-100'
                          }`}
                        >
                          <span className="text-lg">{child.icon}</span>
                          <span className="text-sm">{t(child.labelKey)}</span>
                        </Link>
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            );
          })}
        </ul>
      </div>
    </nav>
  );
}

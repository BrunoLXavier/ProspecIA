import Link from 'next/link';
import { useI18n } from '@/lib/hooks/useI18n';

const DASHBOARD_MENU = [
  { href: '/dashboard', labelKey: 'dashboard.title', icon: '🏠' },
  { href: '/funding-sources', labelKey: 'funding_sources.title', icon: '💰' },
  { href: '/clients', labelKey: 'clients.title', icon: '👤' },
  { href: '/interactions', labelKey: 'interactions.title', icon: '💬' },
  { href: '/portfolio', labelKey: 'portfolio.title', icon: '📁' },
  { href: '/pipeline', labelKey: 'opportunities.title', icon: '🚀' }
];

export default function DashboardSidebar() {
  const { t } = useI18n();
  return (
    <aside className="w-64 bg-white shadow-lg">
      <nav className="p-6">
        <h2 className="text-xl font-bold mb-6 text-primary-600">{t('dashboard.menu_title')}</h2>
        <ul className="space-y-2">
          {DASHBOARD_MENU.map((item) => (
            <li key={item.href}>
              <Link
                href={item.href}
                className={`flex items-center space-x-3 px-4 py-2 rounded-lg transition-colors text-gray-700 hover:bg-gray-100`}
              >
                <span className="text-xl">{item.icon}</span>
                <span>{t(item.labelKey)}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}

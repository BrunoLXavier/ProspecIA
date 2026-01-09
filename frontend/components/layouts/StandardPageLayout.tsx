/**
 * StandardPageLayout - Standard Page Layout Component
 * 
 * Provides consistent layout structure for all Dashboard and Admin pages:
 * 1. Breadcrumb navigation
 * 2. Page title
 * 3. Page description
 * 4. Collapsible form section (Headless UI Disclosure, defaultOpen=true)
 * 5. Filtered data table with CRUD operations
 * 6. Back button
 * 
 * Supports:
 * - Status filtering (active/inactive/deleted) with ACL check for deleted items
 * - Soft delete for non-admin users (sets status='deleted')
 * - Hard delete for admins only (permanent deletion)
 * 
 * @example
 * <StandardPageLayout
 *   breadcrumbs={[{ label: 'Dashboard' }, { label: 'Clients' }]}
 *   title="Manage Clients"
 *   description="View and manage client records"
 *   formComponent={<ClientForm onSubmit={handleSubmit} />}
 *   resource="clients"
 *   data={filteredClients}
 *   columns={clientColumns}
 *   onEdit={handleEdit}
 *   onDelete={handleDelete}
 *   onHardDelete={handleHardDelete}
 * />
 */

import { ReactNode, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Disclosure } from '@headlessui/react';
import { ChevronUpIcon } from '@heroicons/react/24/outline';
import { ACLButton, ACLSection, ACLTable } from '@/components/acl';
import { useI18n } from '@/lib/hooks/useI18n';

interface Breadcrumb {
  label: string;
  href?: string;
}

interface StatusFilter {
  active: boolean;
  inactive: boolean;
  deleted: boolean;
}

interface StandardPageLayoutProps<T> {
  // Header section
  breadcrumbs: Breadcrumb[];
  title: string;
  description: string;

  // Form section
  formComponent: ReactNode;
  formTitle?: string;

  // Table section
  resource: string;
  data: T[];
  columns: Array<{
    key: string;
    header: string;
    render: (item: T) => ReactNode;
  }>;
  keyExtractor: (item: T) => string | number;
  onEdit?: (item: T) => void;
  onDelete?: (item: T) => void;
  onHardDelete?: (item: T) => void;
  emptyMessage?: string;

  // Status filtering
  showStatusFilter?: boolean;
  statusField?: keyof T;
  onStatusFilterChange?: (filter: StatusFilter) => void;

  // Back button
  showBackButton?: boolean;
  backHref?: string;
}

export function StandardPageLayout<T>({
  breadcrumbs,
  title,
  description,
  formComponent,
  formTitle,
  resource,
  data,
  columns,
  keyExtractor,
  onEdit,
  onDelete,
  onHardDelete,
  emptyMessage,
  showStatusFilter = true,
  statusField = 'status' as keyof T,
  onStatusFilterChange,
  showBackButton = true,
  backHref,
}: StandardPageLayoutProps<T>) {
  const router = useRouter();
  const { t } = useI18n();

  const [statusFilter, setStatusFilter] = useState<StatusFilter>({
    active: true,
    inactive: false,
    deleted: false,
  });

  const handleStatusFilterChange = (newFilter: Partial<StatusFilter>) => {
    const updatedFilter = { ...statusFilter, ...newFilter };
    setStatusFilter(updatedFilter);
    onStatusFilterChange?.(updatedFilter);
  };

  const handleBack = () => {
    if (backHref) {
      router.push(backHref);
    } else {
      router.back();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb Navigation */}
        <nav className="flex mb-4" aria-label="Breadcrumb">
          <ol className="inline-flex items-center space-x-1 md:space-x-3">
            {breadcrumbs.map((breadcrumb, index) => (
              <li key={index} className="inline-flex items-center">
                {index > 0 && (
                  <svg
                    className="w-3 h-3 text-gray-400 mx-1"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
                {breadcrumb.href ? (
                  <a
                    href={breadcrumb.href}
                    className="text-sm font-medium text-gray-700 hover:text-blue-600"
                  >
                    {breadcrumb.label}
                  </a>
                ) : (
                  <span className="text-sm font-medium text-gray-500">
                    {breadcrumb.label}
                  </span>
                )}
              </li>
            ))}
          </ol>
        </nav>

        {/* Page Title and Description */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
          <p className="mt-2 text-sm text-gray-600">{description}</p>
        </div>

        {/* Collapsible Form Section */}
        <div className="bg-white shadow sm:rounded-lg mb-8">
          <Disclosure defaultOpen={true}>
            {({ open }) => (
              <>
                <Disclosure.Button className="flex w-full justify-between items-center px-6 py-4 text-left text-lg font-medium text-gray-900 hover:bg-gray-50 focus:outline-none focus-visible:ring focus-visible:ring-blue-500 focus-visible:ring-opacity-75">
                  <span>{formTitle || t('common.form')}</span>
                  <ChevronUpIcon
                    className={`${
                      open ? 'transform rotate-180' : ''
                    } w-5 h-5 text-gray-500 transition-transform`}
                  />
                </Disclosure.Button>
                <Disclosure.Panel className="px-6 pb-6 pt-2">
                  {formComponent}
                </Disclosure.Panel>
              </>
            )}
          </Disclosure>
        </div>

        {/* Status Filter Section */}
        {showStatusFilter && (
          <ACLSection
            resource={resource}
            action="read"
            className="bg-white shadow sm:rounded-lg mb-4 p-4"
          >
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-gray-700">
                {t('common.statusFilter')}:
              </span>
              <label className="inline-flex items-center">
                <input
                  type="checkbox"
                  checked={statusFilter.active}
                  onChange={(e) =>
                    handleStatusFilterChange({ active: e.target.checked })
                  }
                  className="form-checkbox h-4 w-4 text-blue-600"
                />
                <span className="ml-2 text-sm text-gray-700">
                  {t('status.active')}
                </span>
              </label>
              <label className="inline-flex items-center">
                <input
                  type="checkbox"
                  checked={statusFilter.inactive}
                  onChange={(e) =>
                    handleStatusFilterChange({ inactive: e.target.checked })
                  }
                  className="form-checkbox h-4 w-4 text-yellow-600"
                />
                <span className="ml-2 text-sm text-gray-700">
                  {t('status.inactive')}
                </span>
              </label>
              <ACLSection
                resource={resource}
                action="hard_delete"
                showSkeleton={false}
              >
                <label className="inline-flex items-center">
                  <input
                    type="checkbox"
                    checked={statusFilter.deleted}
                    onChange={(e) =>
                      handleStatusFilterChange({ deleted: e.target.checked })
                    }
                    className="form-checkbox h-4 w-4 text-red-600"
                  />
                  <span className="ml-2 text-sm text-gray-700">
                    {t('status.deleted')}
                  </span>
                </label>
              </ACLSection>
            </div>
          </ACLSection>
        )}

        {/* Data Table */}
        <div className="bg-white shadow sm:rounded-lg mb-8">
          <ACLTable
            resource={resource}
            data={data}
            columns={columns}
            keyExtractor={keyExtractor}
            onEdit={onEdit}
            onDelete={onDelete}
            onHardDelete={onHardDelete}
            emptyMessage={emptyMessage}
          />
        </div>

        {/* Back Button */}
        {showBackButton && (
          <div className="flex justify-start">
            <button
              onClick={handleBack}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
              {t('common.back')}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

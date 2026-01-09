/**
 * ACLTable - Access Control List Table Component
 * 
 * Extends standard table with ACL-aware action columns.
 * Conditionally renders Edit/Delete/Hard Delete buttons based on user permissions.
 * 
 * Supports:
 * - Soft delete (sets status='deleted', visible to admins only)
 * - Hard delete (permanent deletion, admin-only)
 * - Custom action buttons with ACL checks
 * 
 * @example
 * <ACLTable
 *   resource="clients"
 *   data={clients}
 *   onEdit={handleEdit}
 *   onDelete={handleDelete}
 *   onHardDelete={handleHardDelete}
 * />
 */

import { ReactNode } from 'react';
import { useACL } from '@/lib/hooks/useACL';
import { ACLButton } from './ACLButton';

interface ACLTableColumn<T> {
  key: string;
  header: string;
  render: (item: T) => ReactNode;
}

interface ACLTableProps<T> {
  resource: string;
  data: T[];
  columns: ACLTableColumn<T>[];
  onEdit?: (item: T) => void;
  onDelete?: (item: T) => void;
  onHardDelete?: (item: T) => void;
  customActions?: Array<{
    action: string;
    label: string;
    variant?: 'primary' | 'secondary' | 'danger';
    onClick: (item: T) => void;
  }>;
  emptyMessage?: string;
  keyExtractor: (item: T) => string | number;
}

export function ACLTable<T>({
  resource,
  data,
  columns,
  onEdit,
  onDelete,
  onHardDelete,
  customActions = [],
  emptyMessage = 'No data available',
  keyExtractor,
}: ACLTableProps<T>) {
  const { allowed: canUpdate } = useACL(resource, 'update');
  const { allowed: canDelete } = useACL(resource, 'delete');
  const { allowed: canHardDelete } = useACL(resource, 'hard_delete');

  const hasActions = (onEdit && canUpdate) || (onDelete && canDelete) || (onHardDelete && canHardDelete) || customActions.length > 0;

  if (data.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">{emptyMessage}</h3>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
      <table className="min-w-full divide-y divide-gray-300">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                scope="col"
                className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
              >
                {column.header}
              </th>
            ))}
            {hasActions && (
              <th
                scope="col"
                className="px-3 py-3.5 text-right text-sm font-semibold text-gray-900"
              >
                Actions
              </th>
            )}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {data.map((item) => (
            <tr key={keyExtractor(item)} className="hover:bg-gray-50">
              {columns.map((column) => (
                <td
                  key={column.key}
                  className="whitespace-nowrap px-3 py-4 text-sm text-gray-900"
                >
                  {column.render(item)}
                </td>
              ))}
              {hasActions && (
                <td className="whitespace-nowrap px-3 py-4 text-right text-sm font-medium space-x-2">
                  {onEdit && canUpdate && (
                    <button
                      onClick={() => onEdit(item)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Edit
                    </button>
                  )}
                  {onDelete && canDelete && (
                    <button
                      onClick={() => onDelete(item)}
                      className="text-yellow-600 hover:text-yellow-900"
                    >
                      Delete
                    </button>
                  )}
                  {onHardDelete && canHardDelete && (
                    <button
                      onClick={() => onHardDelete(item)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Hard Delete
                    </button>
                  )}
                  {customActions.map((customAction) => (
                    <ACLButton
                      key={customAction.action}
                      resource={resource}
                      action={customAction.action}
                      onClick={() => customAction.onClick(item)}
                      variant={customAction.variant || 'secondary'}
                      className="ml-2"
                    >
                      {customAction.label}
                    </ACLButton>
                  ))}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

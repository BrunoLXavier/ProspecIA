/**
 * ACLButton - Access Control List Button Component
 * 
 * Renders a button only if the current user has the specified permission.
 * Shows loading state during permission check, hides button if access denied.
 * 
 * @example
 * <ACLButton resource="clients" action="create" onClick={handleCreate}>
 *   Create Client
 * </ACLButton>
 */

import { ReactNode } from 'react';
import { useACL } from '@/lib/hooks/useACL';

interface ACLButtonProps {
  resource: string;
  action: string;
  onClick?: () => void;
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
  disabled?: boolean;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
}

export function ACLButton({
  resource,
  action,
  onClick,
  children,
  variant = 'primary',
  disabled = false,
  className = '',
  type = 'button',
}: ACLButtonProps) {
  const { allowed, loading } = useACL(resource, action);

  // Don't render if no permission
  if (!loading && !allowed) {
    return null;
  }

  const baseStyles = 'inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors';
  
  const variantStyles = {
    primary: 'text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500 disabled:bg-blue-300',
    secondary: 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 focus:ring-blue-500 disabled:bg-gray-100',
    danger: 'text-white bg-red-600 hover:bg-red-700 focus:ring-red-500 disabled:bg-red-300',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`${baseStyles} ${variantStyles[variant]} ${className}`}
    >
      {loading ? (
        <>
          <svg
            className="animate-spin -ml-1 mr-2 h-4 w-4 text-current"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          Loading...
        </>
      ) : (
        children
      )}
    </button>
  );
}

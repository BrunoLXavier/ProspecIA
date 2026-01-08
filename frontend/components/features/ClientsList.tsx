/**
 * Clients and Interactions feature components
 */

'use client';

import React, { useState, useMemo } from 'react';
import { DataTable } from '@/components/ui/DataTable';
import { useI18n } from '@/lib/hooks/useI18n';
import { useClients } from '@/lib/hooks/useClients';
import { Client, ClientMaturity } from '@/lib/api/clients';

const maturityColors: Record<ClientMaturity, string> = {
  prospect: 'bg-yellow-100 text-yellow-800',
  lead: 'bg-blue-100 text-blue-800',
  opportunity: 'bg-emerald-100 text-emerald-800',
  client: 'bg-indigo-100 text-indigo-800',
  advocate: 'bg-purple-100 text-purple-800',
};

export function ClientsList() {
  const { t } = useI18n();
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [filterMaturity, setFilterMaturity] = useState<ClientMaturity | ''>('');

  const { data, isLoading } = useClients({ maturity: filterMaturity || undefined, limit: 100 });

  const clients = useMemo(() => data?.items ?? [], [data]);

  const columns = [
    {
      key: 'name' as keyof Client,
      label: t('fields.client.name') || 'Name',
      sortable: true,
      width: '30%',
    },
    {
      key: 'cnpj' as keyof Client,
      label: t('fields.client.cnpj') || 'CNPJ',
      render: (value: string) => {
        // Mask CNPJ for display
        return value?.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5') || '';
      },
    },
    {
      key: 'maturity' as keyof Client,
      label: t('fields.client.maturity') || 'Maturity',
      render: (value: string) => (
        <span
          className={`px-2 py-1 text-xs rounded ${
            maturityColors[value as keyof typeof maturityColors] ||
            'bg-gray-100 text-gray-800'
          }`}
        >
          {value}
        </span>
      ),
    },
    {
      key: 'email' as keyof Client,
      label: t('common.email') || 'Email',
      sortable: true,
    },
    {
      key: 'phone' as keyof Client,
      label: t('common.phone') || 'Phone',
    },
    {
      key: 'status' as keyof Client,
      label: t('common.status') || 'Status',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">
          {t('navigation.clients') || 'Clients'}
        </h1>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          {t('common.create') || 'Create'}
        </button>
      </div>

      <div className="flex gap-2">
        <label className="flex items-center gap-2">
          <span className="text-sm font-medium">
            {t('common.filter') || 'Filter'} {t('fields.client.maturity') || 'Maturity'}:
          </span>
          <select
            value={filterMaturity}
            onChange={(e) => setFilterMaturity((e.target.value as ClientMaturity) || '')}
            className="px-3 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">All</option>
            <option value="prospect">Prospect</option>
            <option value="lead">Lead</option>
            <option value="opportunity">Opportunity</option>
            <option value="client">Client</option>
            <option value="advocate">Advocate</option>
          </select>
        </label>
      </div>

      <DataTable
        columns={columns}
        data={clients}
        rowKey="id"
        loading={isLoading}
        onRowClick={setSelectedClient}
      />

      {selectedClient && (
        <ClientDetail
          client={selectedClient}
          onClose={() => setSelectedClient(null)}
        />
      )}
    </div>
  );
}

interface ClientDetailProps {
  client: Client;
  onClose: () => void;
}

export function ClientDetail({ client, onClose }: ClientDetailProps) {
  const { t } = useI18n();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-xl font-bold">{client.name}</h2>
            <span
              className={`inline-block mt-2 px-2 py-1 text-xs rounded ${
                maturityColors[client.maturity as keyof typeof maturityColors] ||
                'bg-gray-100 text-gray-800'
              }`}
            >
              {client.maturity}
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                {t('fields.client.cnpj') || 'CNPJ'}
              </label>
              <p className="text-gray-600">
                {client.cnpj?.replace(
                  /(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/,
                  '$1.$2.$3/$4-$5'
                )}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                {t('common.website') || 'Website'}
              </label>
              <p className="text-gray-600">
                {client.website ? (
                  <a
                    href={client.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    {client.website}
                  </a>
                ) : (
                  '-'
                )}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                {t('common.email') || 'Email'}
              </label>
              <p className="text-gray-600">{client.email}</p>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              {t('common.phone') || 'Phone'}
            </label>
            <p className="text-gray-600">{client.phone}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              {t('common.status') || 'Status'}
            </label>
            <p className="text-gray-600">{client.status}</p>
          </div>

          {client.address && (
            <div>
              <label className="block text-sm font-medium text-gray-700">
                {t('common.address') || 'Address'}
              </label>
              <p className="text-gray-600 whitespace-pre-wrap">{client.address}</p>
            </div>
          )}
        </div>

        <div className="flex justify-end gap-2 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            {t('common.close') || 'Close'}
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            {t('common.edit') || 'Edit'}
          </button>
        </div>
      </div>
    </div>
  );
}

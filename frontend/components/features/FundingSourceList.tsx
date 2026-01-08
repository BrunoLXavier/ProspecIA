/**
 * Funding Sources feature components
 */

'use client';

import React, { useState, useEffect } from 'react';
import { wave2API } from '@/lib/api/wave2';
import { useI18n } from '@/lib/hooks/useI18n';
import { DataTable } from '@/components/ui/DataTable';

interface FundingSource {
  id: string;
  name: string;
  type: string;
  description: string;
  trl_min: number;
  trl_max: number;
  total_budget: string;
  available_budget: string;
  deadline: string;
  sectors: string[];
  status: string;
}

export function FundingSourceList() {
  const { t } = useI18n();
  const [sources, setSources] = useState<FundingSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSource, setSelectedSource] = useState<FundingSource | null>(null);

  useEffect(() => {
    loadSources();
  }, []);

  const loadSources = async () => {
    try {
      setLoading(true);
      const data = await wave2API.getFundingSources();
      setSources(data.items);
    } catch (error) {
      console.error('Error loading funding sources:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      key: 'name' as keyof FundingSource,
      label: t('fields.funding_source.name') || 'Name',
      sortable: true,
      width: '25%',
    },
    {
      key: 'type' as keyof FundingSource,
      label: t('fields.funding_source.type') || 'Type',
      render: (value: string) => (
        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
          {value}
        </span>
      ),
    },
    {
      key: 'sectors' as keyof FundingSource,
      label: t('fields.funding_source.sectors') || 'Sectors',
      render: (value: string[]) => (
        <div className="flex flex-wrap gap-1">
          {value?.map((sector) => (
            <span
              key={sector}
              className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded"
            >
              {sector}
            </span>
          ))}
        </div>
      ),
    },
    {
      key: 'trl_min' as keyof FundingSource,
      label: 'TRL Range',
      render: (value: number, row: FundingSource) =>
        `${row.trl_min} - ${row.trl_max}`,
    },
    {
      key: 'deadline' as keyof FundingSource,
      label: t('common.deadline') || 'Deadline',
      render: (value: string) => new Date(value).toLocaleDateString(),
    },
    {
      key: 'status' as keyof FundingSource,
      label: t('common.status') || 'Status',
      render: (value: string) => (
        <span
          className={`px-2 py-1 text-xs rounded ${
            value === 'active'
              ? 'bg-green-100 text-green-800'
              : 'bg-gray-100 text-gray-800'
          }`}
        >
          {value}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">
          {t('navigation.funding_sources') || 'Funding Sources'}
        </h1>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          {t('common.create') || 'Create'}
        </button>
      </div>

      <DataTable
        columns={columns}
        data={sources}
        rowKey="id"
        loading={loading}
        onRowClick={setSelectedSource}
      />

      {selectedSource && (
        <FundingSourceDetail
          source={selectedSource}
          onClose={() => setSelectedSource(null)}
        />
      )}
    </div>
  );
}

interface FundingSourceDetailProps {
  source: FundingSource;
  onClose: () => void;
}

export function FundingSourceDetail({ source, onClose }: FundingSourceDetailProps) {
  const { t } = useI18n();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">{source.name}</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              {t('common.description') || 'Description'}
            </label>
            <p className="text-gray-600">{source.description}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                {t('common.type') || 'Type'}
              </label>
              <p className="text-gray-600">{source.type}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                TRL Range
              </label>
              <p className="text-gray-600">
                {source.trl_min} - {source.trl_max}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                {t('common.total_budget') || 'Total Budget'}
              </label>
              <p className="text-gray-600">
                R$ {parseFloat(source.total_budget).toLocaleString('pt-BR')}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                {t('common.available_budget') || 'Available Budget'}
              </label>
              <p className="text-gray-600">
                R$ {parseFloat(source.available_budget).toLocaleString('pt-BR')}
              </p>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              {t('fields.funding_source.sectors') || 'Sectors'}
            </label>
            <div className="flex flex-wrap gap-2 mt-2">
              {source.sectors?.map((sector) => (
                <span
                  key={sector}
                  className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded"
                >
                  {sector}
                </span>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              {t('common.deadline') || 'Deadline'}
            </label>
            <p className="text-gray-600">
              {new Date(source.deadline).toLocaleDateString('pt-BR')}
            </p>
          </div>
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

/**
 * Opportunities pipeline components (Kanban view)
 */

'use client';

import React, { useState, useEffect } from 'react';
import { wave2API } from '@/lib/api/wave2';
import { useI18n } from '@/lib/hooks/useI18n';

interface Opportunity {
  id: string;
  title: string;
  description: string;
  client_id: string;
  funding_source_id: string;
  stage: string;
  status: string;
  score: number;
  probability: number;
  expected_close_date: string;
}

const STAGES = ['intelligence', 'validation', 'approach', 'registration', 'conversion', 'post_sale'];

const stageLabels: Record<string, string> = {
  intelligence: 'Inteligência',
  validation: 'Validação',
  approach: 'Abordagem',
  registration: 'Registro',
  conversion: 'Conversão',
  post_sale: 'Pós-venda',
};

const stageColors: Record<string, string> = {
  intelligence: 'bg-blue-50 border-blue-200',
  validation: 'bg-purple-50 border-purple-200',
  approach: 'bg-yellow-50 border-yellow-200',
  registration: 'bg-orange-50 border-orange-200',
  conversion: 'bg-green-50 border-green-200',
  post_sale: 'bg-cyan-50 border-cyan-200',
};

export function OpportunitiesPipeline() {
  const { t } = useI18n();
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedOpp, setSelectedOpp] = useState<Opportunity | null>(null);

  useEffect(() => {
    loadOpportunities();
  }, []);

  const loadOpportunities = async () => {
    try {
      setLoading(true);
      const data = await wave2API.getOpportunities(100);
      setOpportunities(data.items);
    } catch (error) {
      console.error('Error loading opportunities:', error);
    } finally {
      setLoading(false);
    }
  };

  const groupByStage = () => {
    const grouped: Record<string, Opportunity[]> = {};
    STAGES.forEach((stage) => {
      grouped[stage] = opportunities.filter((opp) => opp.stage === stage);
    });
    return grouped;
  };

  const grouped = groupByStage();

  if (loading) {
    return <div className="p-4 text-center">{t('common.loading')}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">
          {t('navigation.pipeline') || 'Pipeline'}
        </h1>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          {t('common.create') || 'Create'}
        </button>
      </div>

      <div className="grid grid-cols-6 gap-4 overflow-x-auto pb-4">
        {STAGES.map((stage) => (
          <div
            key={stage}
            className={`flex-1 min-w-[280px] border-l-4 rounded-lg p-4 ${stageColors[stage]}`}
          >
            <div className="mb-4">
              <h3 className="font-semibold text-gray-900">
                {stageLabels[stage]}
              </h3>
              <p className="text-sm text-gray-600">
                {grouped[stage].length} {t('common.items') || 'items'}
              </p>
            </div>

            <div className="space-y-3">
              {grouped[stage].map((opp) => (
                <OpportunityCard
                  key={opp.id}
                  opportunity={opp}
                  onClick={() => setSelectedOpp(opp)}
                  onStageChange={(newStage) => {
                    wave2API
                      .transitionOpportunity(opp.id, newStage)
                      .then(() => loadOpportunities())
                      .catch(console.error);
                  }}
                />
              ))}
            </div>
          </div>
        ))}
      </div>

      {selectedOpp && (
        <OpportunityDetail
          opportunity={selectedOpp}
          onClose={() => setSelectedOpp(null)}
          onTransition={(newStage) => {
            wave2API
              .transitionOpportunity(selectedOpp.id, newStage)
              .then(() => {
                loadOpportunities();
                setSelectedOpp(null);
              })
              .catch(console.error);
          }}
        />
      )}
    </div>
  );
}

interface OpportunityCardProps {
  opportunity: Opportunity;
  onClick: () => void;
  onStageChange?: (stage: string) => void;
}

function OpportunityCard({
  opportunity,
  onClick,
  onStageChange,
}: OpportunityCardProps) {
  const scoreColor =
    opportunity.score >= 75
      ? 'text-green-600'
      : opportunity.score >= 50
      ? 'text-yellow-600'
      : 'text-red-600';

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg p-3 border border-gray-200 hover:shadow-md cursor-pointer transition-shadow"
    >
      <h4 className="font-medium text-sm text-gray-900 truncate">
        {opportunity.title}
      </h4>
      <p className="text-xs text-gray-600 mt-1 truncate">
        {opportunity.description}
      </p>
      <div className="flex justify-between items-end mt-3">
        <div className="text-right">
          <div className={`text-lg font-bold ${scoreColor}`}>
            {opportunity.score}
          </div>
          <div className="text-xs text-gray-500">Score</div>
        </div>
      </div>
    </div>
  );
}

interface OpportunityDetailProps {
  opportunity: Opportunity;
  onClose: () => void;
  onTransition: (stage: string) => void;
}

function OpportunityDetail({
  opportunity,
  onClose,
  onTransition,
}: OpportunityDetailProps) {
  const { t } = useI18n();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">{opportunity.title}</h2>
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
            <p className="text-gray-600">{opportunity.description}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Score
              </label>
              <div className="flex items-center gap-2 mt-1">
                <div className="text-2xl font-bold text-blue-600">
                  {opportunity.score}
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${opportunity.score}%` }}
                  ></div>
                </div>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Probability
              </label>
              <div className="flex items-center gap-2 mt-1">
                <div className="text-2xl font-bold text-green-600">
                  {opportunity.probability}%
                </div>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Current Stage
            </label>
            <div className="mt-2">
              <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded">
                {stageLabels[opportunity.stage]}
              </span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Move to Stage
            </label>
            <div className="grid grid-cols-3 gap-2">
              {STAGES.map((stage) => (
                <button
                  key={stage}
                  onClick={() => onTransition(stage)}
                  disabled={stage === opportunity.stage}
                  className="px-3 py-2 text-sm rounded border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {stageLabels[stage]}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Expected Close Date
            </label>
            <p className="text-gray-600">
              {new Date(opportunity.expected_close_date).toLocaleDateString('pt-BR')}
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
        </div>
      </div>
    </div>
  );
}

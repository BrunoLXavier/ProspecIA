/**
 * Portfolio feature components (Institutes, Projects, Competences)
 */

'use client';

import React, { useState, useEffect } from 'react';
import { wave2API } from '@/lib/api/wave2';
import { useI18n } from '@/lib/hooks/useI18n';
import { DataTable } from '@/components/ui/DataTable';

interface Institute {
  id: string;
  name: string;
  description: string;
  status: string;
  established_year: number;
  headquarters_city: string;
  contact_email: string;
}

interface Project {
  id: string;
  institute_id: string;
  name: string;
  description: string;
  trl: number;
  start_date: string;
  end_date: string;
  budget: string;
  status: string;
}

export function PortfolioView() {
  const { t } = useI18n();
  const [activeTab, setActiveTab] = useState<'institutes' | 'projects'>('institutes');

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">
          {t('navigation.portfolio') || 'Portfolio'}
        </h1>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          {t('common.create') || 'Create'}
        </button>
      </div>

      <div className="flex gap-4 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('institutes')}
          className={`px-4 py-2 font-medium border-b-2 ${
            activeTab === 'institutes'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          {t('navigation.institutes') || 'Institutes'}
        </button>
        <button
          onClick={() => setActiveTab('projects')}
          className={`px-4 py-2 font-medium border-b-2 ${
            activeTab === 'projects'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          {t('navigation.projects') || 'Projects'}
        </button>
      </div>

      {activeTab === 'institutes' && <InstitutesList />}
      {activeTab === 'projects' && <ProjectsList />}
    </div>
  );
}

function InstitutesList() {
  const { t } = useI18n();
  const [institutes, setInstitutes] = useState<Institute[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedInstitute, setSelectedInstitute] = useState<Institute | null>(null);

  useEffect(() => {
    loadInstitutes();
  }, []);

  const loadInstitutes = async () => {
    try {
      setLoading(true);
      const data = await wave2API.getInstitutes();
      setInstitutes(data.items);
    } catch (error) {
      console.error('Error loading institutes:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      key: 'name' as keyof Institute,
      label: t('common.name') || 'Name',
      sortable: true,
      width: '30%',
    },
    {
      key: 'headquarters_city' as keyof Institute,
      label: t('common.city') || 'City',
      sortable: true,
    },
    {
      key: 'established_year' as keyof Institute,
      label: t('common.established') || 'Established',
      sortable: true,
    },
    {
      key: 'contact_email' as keyof Institute,
      label: t('common.email') || 'Email',
    },
    {
      key: 'status' as keyof Institute,
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
    <div className="space-y-4">
      <DataTable
        columns={columns}
        data={institutes}
        rowKey="id"
        loading={loading}
        onRowClick={setSelectedInstitute}
      />

      {selectedInstitute && (
        <InstituteDetail
          institute={selectedInstitute}
          onClose={() => setSelectedInstitute(null)}
        />
      )}
    </div>
  );
}

function ProjectsList() {
  const { t } = useI18n();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [filterTRL, setFilterTRL] = useState<number | ''>('');

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const data = await wave2API.getProjects();
      setProjects(data.items);
    } catch (error) {
      console.error('Error loading projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredProjects = filterTRL
    ? projects.filter((p) => p.trl >= filterTRL)
    : projects;

  const columns = [
    {
      key: 'name' as keyof Project,
      label: t('common.name') || 'Name',
      sortable: true,
      width: '35%',
    },
    {
      key: 'trl' as keyof Project,
      label: 'TRL',
      sortable: true,
      render: (value: number) => (
        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded">
          TRL {value}
        </span>
      ),
    },
    {
      key: 'budget' as keyof Project,
      label: t('common.budget') || 'Budget',
      render: (value: string) =>
        `R$ ${parseFloat(value).toLocaleString('pt-BR')}`,
    },
    {
      key: 'start_date' as keyof Project,
      label: t('common.start_date') || 'Start',
      render: (value: string) => new Date(value).toLocaleDateString('pt-BR'),
    },
    {
      key: 'status' as keyof Project,
      label: t('common.status') || 'Status',
      render: (value: string) => (
        <span
          className={`px-2 py-1 text-xs rounded ${
            value === 'active'
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}
        >
          {value}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <label className="flex items-center gap-2">
          <span className="text-sm font-medium">
            {t('common.filter')} TRL ≥:
          </span>
          <select
            value={filterTRL}
            onChange={(e) => setFilterTRL(e.target.value ? parseInt(e.target.value) : '')}
            className="px-3 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">All</option>
            {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((trl) => (
              <option key={trl} value={trl}>
                {trl}
              </option>
            ))}
          </select>
        </label>
      </div>

      <DataTable
        columns={columns}
        data={filteredProjects}
        rowKey="id"
        loading={loading}
        onRowClick={setSelectedProject}
      />

      {selectedProject && (
        <ProjectDetail
          project={selectedProject}
          onClose={() => setSelectedProject(null)}
        />
      )}
    </div>
  );
}

interface InstituteDetailProps {
  institute: Institute;
  onClose: () => void;
}

function InstituteDetail({ institute, onClose }: InstituteDetailProps) {
  const { t } = useI18n();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">{institute.name}</h2>
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
            <p className="text-gray-600">{institute.description}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                {t('common.city') || 'City'}
              </label>
              <p className="text-gray-600">{institute.headquarters_city}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                {t('common.established') || 'Established'}
              </label>
              <p className="text-gray-600">{institute.established_year}</p>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              {t('common.email') || 'Email'}
            </label>
            <p className="text-gray-600">{institute.contact_email}</p>
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

interface ProjectDetailProps {
  project: Project;
  onClose: () => void;
}

function ProjectDetail({ project, onClose }: ProjectDetailProps) {
  const { t } = useI18n();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">{project.name}</h2>
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
            <p className="text-gray-600">{project.description}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                TRL
              </label>
              <span className="inline-block mt-1 px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded">
                TRL {project.trl}
              </span>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                {t('common.budget') || 'Budget'}
              </label>
              <p className="text-gray-600">
                R$ {parseFloat(project.budget).toLocaleString('pt-BR')}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                {t('common.start_date') || 'Start Date'}
              </label>
              <p className="text-gray-600">
                {new Date(project.start_date).toLocaleDateString('pt-BR')}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                {t('common.end_date') || 'End Date'}
              </label>
              <p className="text-gray-600">
                {new Date(project.end_date).toLocaleDateString('pt-BR')}
              </p>
            </div>
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

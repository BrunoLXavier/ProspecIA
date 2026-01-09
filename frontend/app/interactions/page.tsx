"use client";

import React, { useEffect, useState } from 'react';
import DashboardSidebar from '@/components/layout/DashboardSidebar';
import { useI18n } from '@/lib/hooks/useI18n';
import InteractionForm from './InteractionForm';

interface Interaction {
  id: string;
  client_id: string;
  title: string;
  description: string;
  type: string;
  date: string;
  participants: string[];
  outcome: string;
  next_steps: string;
  status: string;
}

const fetchInteractions = async (): Promise<Interaction[]> => {
  const res = await fetch('http://localhost:8000/interactions');
  if (!res.ok) throw new Error('Erro ao buscar interações');
  const data = await res.json();
  return data.items || [];
};

export default function InteractionsPage() {
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Interaction | null>(null);
  const [editId, setEditId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<Partial<Interaction>>({});
  const [editLoading, setEditLoading] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);
  const { t } = useI18n();
  const handleRowClick = (interaction: Interaction) => {
    setSelected(interaction);
    setEditId(null);
  };

  const handleEditClick = (interaction: Interaction) => {
    setEditId(interaction.id);
    setEditForm({ ...interaction });
    setSelected(null);
  };

  const handleEditChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setEditForm({ ...editForm, [e.target.name]: e.target.value });
  };

  const handleEditSave = async () => {
    setEditLoading(true);
    setEditError(null);
    try {
      const res = await fetch(`http://localhost:8000/interactions/${editId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editForm),
      });
      if (!res.ok) throw new Error('Erro ao editar interação');
      setEditId(null);
      setEditForm({});
      loadInteractions();
    } catch (err: any) {
      setEditError(err.message);
    } finally {
      setEditLoading(false);
    }
  };

  const loadInteractions = () => {
    setLoading(true);
    fetchInteractions()
      .then(setInteractions)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadInteractions();
    // eslint-disable-next-line
  }, []);

  return (
    <main className="flex min-h-screen bg-gray-100">
      {/* Sidebar */}
      <DashboardSidebar />
      {/* Main Content */}
      <section className="flex-1 flex flex-col items-center justify-start pt-6 sm:pt-12 lg:pt-24 px-6 sm:px-12 lg:px-24 pb-24">
        <div className="w-full max-w-5xl">
          <h1 className="text-4xl font-bold text-primary-600 mb-4">{t('interactions.title')}</h1>
          <InteractionForm onCreated={loadInteractions} />
          {loading && <p>{t('interactions.loading')}</p>}
          {error && <p className="text-red-500">{error}</p>}
          <table className="min-w-full border">
            <thead>
              <tr>
                <th className="border px-2 py-1">{t('interactions.table.title')}</th>
                <th className="border px-2 py-1">{t('interactions.table.client')}</th>
                <th className="border px-2 py-1">{t('interactions.table.type')}</th>
                <th className="border px-2 py-1">{t('interactions.table.date')}</th>
                <th className="border px-2 py-1">{t('interactions.table.status')}</th>
                <th className="border px-2 py-1">{t('interactions.table.actions')}</th>
              </tr>
            </thead>
            <tbody>
          {interactions.map((i) => (
            editId === i.id ? (
              <tr key={i.id} className="bg-yellow-50">
                <td className="border px-2 py-1">
                  <input name="title" value={editForm.title || ''} onChange={handleEditChange} className="border px-1" />
                </td>
                <td className="border px-2 py-1">{i.client_id}</td>
                <td className="border px-2 py-1">
                  <input name="type" value={editForm.type || ''} onChange={handleEditChange} className="border px-1" />
                </td>
                <td className="border px-2 py-1">
                  <input name="date" type="date" value={editForm.date ? editForm.date.slice(0,10) : ''} onChange={handleEditChange} className="border px-1" />
                </td>
                <td className="border px-2 py-1">
                  <input name="status" value={editForm.status || ''} onChange={handleEditChange} className="border px-1" />
                </td>
                <td className="border px-2 py-1">
                  <button className="bg-green-600 text-white px-2 py-1 rounded mr-2" onClick={handleEditSave} disabled={editLoading}>{t('interactions.save')}</button>
                  <button className="bg-gray-400 text-white px-2 py-1 rounded" onClick={() => setEditId(null)}>{t('interactions.cancel')}</button>
                  {editError && <div className="text-red-500">{editError}</div>}
                </td>
              </tr>
            ) : (
              <tr key={i.id} className={selected?.id === i.id ? 'bg-blue-50' : ''} onClick={() => handleRowClick(i)}>
                <td className="border px-2 py-1">{i.title}</td>
                <td className="border px-2 py-1">{i.client_id}</td>
                <td className="border px-2 py-1">{i.type}</td>
                <td className="border px-2 py-1">{new Date(i.date).toLocaleDateString()}</td>
                <td className="border px-2 py-1">{i.status}</td>
                <td className="border px-2 py-1">
                  <button className="bg-yellow-600 text-white px-2 py-1 rounded" onClick={(e) => {e.stopPropagation(); handleEditClick(i);}}>{t('interactions.edit')}</button>
                </td>
              </tr>
            )
          ))}
        </tbody>
      </table>
      {selected && (
        <div className="mt-6 p-4 border rounded bg-gray-50">
          <h3 className="font-bold text-lg mb-2">{t('interactions.details.title')}</h3>
          <div><b>{t('interactions.details.title_label')}:</b> {selected.title}</div>
          <div><b>{t('interactions.details.client')}:</b> {selected.client_id}</div>
          <div><b>{t('interactions.details.type')}:</b> {selected.type}</div>
          <div><b>{t('interactions.details.date')}:</b> {new Date(selected.date).toLocaleDateString()}</div>
          <div><b>{t('interactions.details.status')}:</b> {selected.status}</div>
          <div><b>{t('interactions.details.description')}:</b> {selected.description}</div>
          <div><b>{t('interactions.details.participants')}:</b> {selected.participants?.join(', ')}</div>
          <div><b>{t('interactions.details.outcome')}:</b> {selected.outcome}</div>
          <div><b>{t('interactions.details.next_steps')}:</b> {selected.next_steps}</div>
        </div>
      )}
        </div>
      </section>
    </main>
  );
}
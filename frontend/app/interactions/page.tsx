"use client";

import React, { useEffect, useState } from 'react';
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

const InteractionsPage: React.FC = () => {
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Interaction | null>(null);
  const [editId, setEditId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<Partial<Interaction>>({});
  const [editLoading, setEditLoading] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);
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
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Interações</h1>
      <InteractionForm onCreated={loadInteractions} />
      {loading && <p>Carregando...</p>}
      {error && <p className="text-red-500">{error}</p>}
      <table className="min-w-full border">
        <thead>
          <tr>
            <th className="border px-2 py-1">Título</th>
            <th className="border px-2 py-1">Cliente</th>
            <th className="border px-2 py-1">Tipo</th>
            <th className="border px-2 py-1">Data</th>
            <th className="border px-2 py-1">Status</th>
            <th className="border px-2 py-1">Ações</th>
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
                  <button className="bg-green-600 text-white px-2 py-1 rounded mr-2" onClick={handleEditSave} disabled={editLoading}>Salvar</button>
                  <button className="bg-gray-400 text-white px-2 py-1 rounded" onClick={() => setEditId(null)}>Cancelar</button>
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
                  <button className="bg-yellow-600 text-white px-2 py-1 rounded" onClick={(e) => {e.stopPropagation(); handleEditClick(i);}}>Editar</button>
                </td>
              </tr>
            )
          ))}
        </tbody>
      </table>
      {selected && (
        <div className="mt-6 p-4 border rounded bg-gray-50">
          <h3 className="font-bold text-lg mb-2">Detalhes da Interação</h3>
          <div><b>Título:</b> {selected.title}</div>
          <div><b>Cliente:</b> {selected.client_id}</div>
          <div><b>Tipo:</b> {selected.type}</div>
          <div><b>Data:</b> {new Date(selected.date).toLocaleDateString()}</div>
          <div><b>Status:</b> {selected.status}</div>
          <div><b>Descrição:</b> {selected.description}</div>
          <div><b>Participantes:</b> {selected.participants?.join(', ')}</div>
          <div><b>Resultado:</b> {selected.outcome}</div>
          <div><b>Próximos Passos:</b> {selected.next_steps}</div>
        </div>
      )}
    </div>
  );
};

export default InteractionsPage;

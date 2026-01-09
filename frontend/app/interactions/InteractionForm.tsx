import React, { useState } from 'react';
import ClientAutocomplete from './ClientAutocomplete';

interface InteractionFormProps {
  onCreated: () => void;
}

const initialState = {
  client_id: '',
  title: '',
  description: '',
  type: '',
  date: '',
  participants: '',
  outcome: '',
  next_steps: '',
};

const InteractionForm: React.FC<InteractionFormProps> = ({ onCreated }) => {
  const [form, setForm] = useState(initialState);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);


  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleClientChange = (id: string) => {
    setForm({ ...form, client_id: id });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      const res = await fetch('http://localhost:8000/interactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          participants: form.participants.split(',').map((p) => p.trim()),
        }),
      });
      if (!res.ok) throw new Error('Erro ao criar interação');
      setForm(initialState);
      setSuccess(true);
      onCreated();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="mb-8 p-4 border rounded" onSubmit={handleSubmit}>
      <h2 className="text-lg font-semibold mb-2">Nova Interação</h2>
      <div className="mb-2">
        <ClientAutocomplete value={form.client_id} onChange={handleClientChange} />
      </div>
      <div className="mb-2">
        <input name="title" value={form.title} onChange={handleChange} placeholder="Título" className="border px-2 py-1 w-full" required />
      </div>
      <div className="mb-2">
        <textarea name="description" value={form.description} onChange={handleChange} placeholder="Descrição" className="border px-2 py-1 w-full" />
      </div>
      <div className="mb-2">
        <input name="type" value={form.type} onChange={handleChange} placeholder="Tipo" className="border px-2 py-1 w-full" required />
      </div>
      <div className="mb-2">
        <input name="date" type="date" value={form.date} onChange={handleChange} className="border px-2 py-1 w-full" required />
      </div>
      <div className="mb-2">
        <input name="participants" value={form.participants} onChange={handleChange} placeholder="Participantes (separados por vírgula)" className="border px-2 py-1 w-full" />
      </div>
      <div className="mb-2">
        <input name="outcome" value={form.outcome} onChange={handleChange} placeholder="Resultado" className="border px-2 py-1 w-full" />
      </div>
      <div className="mb-2">
        <input name="next_steps" value={form.next_steps} onChange={handleChange} placeholder="Próximos Passos" className="border px-2 py-1 w-full" />
      </div>
      <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded" disabled={loading || !form.client_id || !form.title || !form.type || !form.date}>Criar</button>
      {loading && <span className="ml-2">Enviando...</span>}
      {error && <div className="text-red-500 mt-2">{error}</div>}
      {success && <div className="text-green-600 mt-2">Interação criada com sucesso!</div>}
    </form>
  );
};

export default InteractionForm;

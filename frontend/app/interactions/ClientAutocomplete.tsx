import React, { useState, useEffect } from 'react';

interface Client {
  id: string;
  name: string;
}

interface ClientAutocompleteProps {
  value: string;
  onChange: (id: string) => void;
}

const ClientAutocomplete: React.FC<ClientAutocompleteProps> = ({ value, onChange }) => {
  const [clients, setClients] = useState<Client[]>([]);
  const [query, setQuery] = useState('');
  const [showList, setShowList] = useState(false);

  useEffect(() => {
    fetch('http://localhost:8000/clients')
      .then((res) => res.json())
      .then((data) => setClients(data.items || []));
  }, []);

  const filtered = clients.filter((c) =>
    c.name.toLowerCase().includes(query.toLowerCase()) || c.id.includes(query)
  );

  return (
    <div className="relative">
      <input
        name="client_id"
        value={query || value}
        onChange={(e) => {
          setQuery(e.target.value);
          setShowList(true);
        }}
        placeholder="Buscar cliente por nome ou ID"
        className="border px-2 py-1 w-full"
        autoComplete="off"
        onFocus={() => setShowList(true)}
        onBlur={() => setTimeout(() => setShowList(false), 200)}
        required
      />
      {showList && filtered.length > 0 && (
        <ul className="absolute z-10 bg-white border w-full max-h-40 overflow-y-auto">
          {filtered.map((c) => (
            <li
              key={c.id}
              className="px-2 py-1 cursor-pointer hover:bg-blue-100"
              onMouseDown={() => {
                onChange(c.id);
                setQuery(c.name);
                setShowList(false);
              }}
            >
              {c.name} <span className="text-xs text-gray-500">({c.id})</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ClientAutocomplete;

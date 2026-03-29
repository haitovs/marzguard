import { useEffect, useState } from 'react'
import { api } from '../api/client'

interface Policy {
  id: number
  name: string
  default_ip_limit: number | null
  auto_reenable: boolean
  reenable_delay_sec: number
  notify_on_violation: boolean
  user_count: number
}

export default function Policies() {
  const [policies, setPolicies] = useState<Policy[]>([])
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ name: '', default_ip_limit: '', auto_reenable: true, reenable_delay_sec: '300', notify_on_violation: true })

  const load = () => api.getPolicies().then(setPolicies)
  useEffect(() => { load() }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.createPolicy({
      ...form,
      default_ip_limit: form.default_ip_limit ? parseInt(form.default_ip_limit) : null,
      reenable_delay_sec: parseInt(form.reenable_delay_sec),
    })
    setShowCreate(false)
    setForm({ name: '', default_ip_limit: '', auto_reenable: true, reenable_delay_sec: '300', notify_on_violation: true })
    load()
  }

  const handleDelete = async (id: number) => {
    if (confirm('Delete this policy?')) {
      await api.deletePolicy(id)
      load()
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">Policies</h1>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded text-sm"
        >
          {showCreate ? 'Cancel' : 'New Policy'}
        </button>
      </div>

      {showCreate && (
        <form onSubmit={handleCreate} className="bg-gray-800 rounded-lg p-4 mb-6 space-y-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Name</label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm"
                required
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">IP Limit</label>
              <input
                type="number"
                value={form.default_ip_limit}
                onChange={(e) => setForm({ ...form, default_ip_limit: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm"
                placeholder="No limit"
                min="1"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Re-enable Delay (sec)</label>
              <input
                type="number"
                value={form.reenable_delay_sec}
                onChange={(e) => setForm({ ...form, reenable_delay_sec: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm"
              />
            </div>
            <div className="flex items-end space-x-4">
              <label className="flex items-center space-x-2 text-sm text-gray-300">
                <input
                  type="checkbox"
                  checked={form.auto_reenable}
                  onChange={(e) => setForm({ ...form, auto_reenable: e.target.checked })}
                  className="rounded"
                />
                <span>Auto re-enable</span>
              </label>
              <label className="flex items-center space-x-2 text-sm text-gray-300">
                <input
                  type="checkbox"
                  checked={form.notify_on_violation}
                  onChange={(e) => setForm({ ...form, notify_on_violation: e.target.checked })}
                  className="rounded"
                />
                <span>Notify</span>
              </label>
            </div>
          </div>
          <button type="submit" className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded text-sm">
            Create Policy
          </button>
        </form>
      )}

      <div className="bg-gray-800 rounded-lg overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase">Name</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase">IP Limit</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase">Auto Re-enable</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase">Delay</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase">Users</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody>
            {policies.map((policy) => (
              <tr key={policy.id} className="border-b border-gray-700/50">
                <td className="px-4 py-3 text-white font-medium">{policy.name}</td>
                <td className="px-4 py-3 text-gray-300">{policy.default_ip_limit ?? 'Global default'}</td>
                <td className="px-4 py-3 text-gray-300">{policy.auto_reenable ? 'Yes' : 'No'}</td>
                <td className="px-4 py-3 text-gray-300">{policy.reenable_delay_sec}s</td>
                <td className="px-4 py-3 text-gray-300">{policy.user_count}</td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => handleDelete(policy.id)}
                    className="text-red-400 text-xs hover:text-red-300"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
            {policies.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                  No policies created yet
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

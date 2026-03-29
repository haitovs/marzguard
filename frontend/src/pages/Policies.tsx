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
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState({
    name: '', default_ip_limit: '', auto_reenable: true, reenable_delay_sec: '300', notify_on_violation: true,
  })
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    api.getPolicies().then(setPolicies).finally(() => setLoading(false))
  }
  useEffect(() => { load() }, [])

  const resetForm = () => {
    setForm({ name: '', default_ip_limit: '', auto_reenable: true, reenable_delay_sec: '300', notify_on_violation: true })
    setEditingId(null)
    setShowCreate(false)
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    const payload = {
      ...form,
      default_ip_limit: form.default_ip_limit ? parseInt(form.default_ip_limit) : null,
      reenable_delay_sec: parseInt(form.reenable_delay_sec),
    }
    if (editingId) {
      await api.updatePolicy(editingId, payload)
    } else {
      await api.createPolicy(payload)
    }
    resetForm()
    load()
  }

  const handleEdit = (policy: Policy) => {
    setForm({
      name: policy.name,
      default_ip_limit: policy.default_ip_limit?.toString() || '',
      auto_reenable: policy.auto_reenable,
      reenable_delay_sec: policy.reenable_delay_sec.toString(),
      notify_on_violation: policy.notify_on_violation,
    })
    setEditingId(policy.id)
    setShowCreate(true)
  }

  const handleDelete = async (id: number) => {
    if (confirm('Delete this policy? Users assigned to it will fall back to the global default.')) {
      await api.deletePolicy(id)
      load()
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Policies</h1>
          <p className="text-sm text-gray-400 mt-1">{policies.length} policies</p>
        </div>
        <button
          onClick={() => { if (showCreate) resetForm(); else setShowCreate(true) }}
          className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded text-sm transition-colors"
        >
          {showCreate ? 'Cancel' : 'New Policy'}
        </button>
      </div>

      {showCreate && (
        <form onSubmit={handleCreate} className="bg-gray-800 rounded-lg border border-gray-700/50 p-5 mb-6">
          <h3 className="text-white font-medium mb-4">{editingId ? 'Edit Policy' : 'Create Policy'}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Name</label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-emerald-400 transition-colors"
                required
                placeholder="e.g., Premium, Basic"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">IP Limit</label>
              <input
                type="number"
                value={form.default_ip_limit}
                onChange={(e) => setForm({ ...form, default_ip_limit: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-emerald-400 transition-colors"
                placeholder="0 = no limit (uses global)"
                min="0"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Re-enable Delay (seconds)</label>
              <input
                type="number"
                value={form.reenable_delay_sec}
                onChange={(e) => setForm({ ...form, reenable_delay_sec: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-emerald-400 transition-colors"
                min="0"
              />
            </div>
            <div className="flex items-end space-x-6">
              <label className="flex items-center space-x-2 text-sm text-gray-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.auto_reenable}
                  onChange={(e) => setForm({ ...form, auto_reenable: e.target.checked })}
                  className="rounded bg-gray-700 border-gray-600 text-emerald-500 focus:ring-emerald-500"
                />
                <span>Auto re-enable</span>
              </label>
              <label className="flex items-center space-x-2 text-sm text-gray-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.notify_on_violation}
                  onChange={(e) => setForm({ ...form, notify_on_violation: e.target.checked })}
                  className="rounded bg-gray-700 border-gray-600 text-emerald-500 focus:ring-emerald-500"
                />
                <span>Notify on violation</span>
              </label>
            </div>
          </div>
          <div className="flex items-center space-x-3 mt-4 pt-4 border-t border-gray-700/50">
            <button type="submit" className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded text-sm font-medium transition-colors">
              {editingId ? 'Save Changes' : 'Create Policy'}
            </button>
            <button type="button" onClick={resetForm} className="text-gray-400 hover:text-white text-sm transition-colors">
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="bg-gray-800 rounded-lg border border-gray-700/50 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">Name</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">IP Limit</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">Auto Re-enable</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">Delay</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">Notify</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">Users</th>
              <th className="text-right px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} className="px-4 py-12 text-center text-gray-500">Loading...</td>
              </tr>
            ) : policies.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-12 text-center text-gray-500">
                  No policies yet — create one to group users with shared IP limits
                </td>
              </tr>
            ) : policies.map((policy) => (
              <tr key={policy.id} className="border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors">
                <td className="px-4 py-3 text-white font-medium">{policy.name}</td>
                <td className="px-4 py-3 text-gray-300">
                  {policy.default_ip_limit ? policy.default_ip_limit : <span className="text-gray-500">Global default</span>}
                </td>
                <td className="px-4 py-3">
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    policy.auto_reenable ? 'bg-emerald-500/10 text-emerald-400' : 'bg-gray-600/20 text-gray-500'
                  }`}>
                    {policy.auto_reenable ? 'Yes' : 'No'}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-300 text-sm tabular-nums">{policy.reenable_delay_sec}s</td>
                <td className="px-4 py-3">
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    policy.notify_on_violation ? 'bg-blue-500/10 text-blue-400' : 'bg-gray-600/20 text-gray-500'
                  }`}>
                    {policy.notify_on_violation ? 'Yes' : 'No'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className="text-sm text-gray-300 tabular-nums">{policy.user_count}</span>
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="flex items-center justify-end space-x-2">
                    <button
                      onClick={() => handleEdit(policy)}
                      className="text-blue-400 hover:text-blue-300 text-xs transition-colors"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(policy.id)}
                      className="text-red-400 hover:text-red-300 text-xs transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

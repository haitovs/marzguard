import { useEffect, useState } from 'react'
import { api } from '../api/client'
import IPBadge from '../components/IPBadge'

interface User {
  id: number
  username: string
  ip_limit: number | null
  policy_name: string | null
  is_monitored: boolean
  is_exempt: boolean
  active_ip_count: number
  active_ips: string[]
  effective_limit: number
  disabled_at: string | null
}

export default function Users() {
  const [users, setUsers] = useState<User[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [syncing, setSyncing] = useState(false)
  const [editingUser, setEditingUser] = useState<string | null>(null)
  const [editLimit, setEditLimit] = useState('')

  const loadUsers = () => {
    api.getUsers(page, search).then((data) => {
      setUsers(data.users)
      setTotal(data.total)
    })
  }

  useEffect(loadUsers, [page, search])

  const handleSync = async () => {
    setSyncing(true)
    try {
      const result = await api.syncUsers()
      alert(`Synced: ${result.added} new users added (${result.total} total)`)
      loadUsers()
    } finally {
      setSyncing(false)
    }
  }

  const handleSaveLimit = async (username: string) => {
    const limit = editLimit === '' ? null : parseInt(editLimit)
    await api.updateUser(username, { ip_limit: limit })
    setEditingUser(null)
    loadUsers()
  }

  const handleToggleDisable = async (user: User) => {
    if (user.disabled_at) {
      await api.enableUser(user.username)
    } else {
      await api.disableUser(user.username)
    }
    loadUsers()
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">Users</h1>
        <button
          onClick={handleSync}
          disabled={syncing}
          className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded text-sm disabled:opacity-50"
        >
          {syncing ? 'Syncing...' : 'Sync from Marzban'}
        </button>
      </div>

      <div className="mb-4">
        <input
          type="text"
          placeholder="Search users..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1) }}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white w-64 focus:outline-none focus:border-emerald-400"
        />
      </div>

      <div className="bg-gray-800 rounded-lg overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase">Username</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase">Policy</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase">Limit</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase">Active IPs</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase">Status</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                <td className="px-4 py-3 font-mono text-sm text-white">{user.username}</td>
                <td className="px-4 py-3 text-sm text-gray-300">{user.policy_name || '-'}</td>
                <td className="px-4 py-3 text-sm">
                  {editingUser === user.username ? (
                    <div className="flex items-center space-x-2">
                      <input
                        type="number"
                        value={editLimit}
                        onChange={(e) => setEditLimit(e.target.value)}
                        className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-white w-16 text-sm"
                        placeholder="auto"
                        min="0"
                      />
                      <button
                        onClick={() => handleSaveLimit(user.username)}
                        className="text-emerald-400 text-xs"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => setEditingUser(null)}
                        className="text-gray-400 text-xs"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <span
                      className="cursor-pointer hover:text-emerald-400"
                      onClick={() => { setEditingUser(user.username); setEditLimit(user.ip_limit?.toString() || '') }}
                    >
                      {user.ip_limit ?? user.effective_limit}
                      {user.ip_limit === null && <span className="text-gray-500 text-xs ml-1">(inherited)</span>}
                    </span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <span className={`text-sm font-medium ${user.active_ip_count > user.effective_limit ? 'text-red-400' : 'text-emerald-400'}`}>
                    {user.active_ip_count}/{user.effective_limit}
                  </span>
                  <div className="mt-1">
                    {user.active_ips.map((ip) => (
                      <IPBadge key={ip} ip={ip} />
                    ))}
                  </div>
                </td>
                <td className="px-4 py-3">
                  {user.disabled_at ? (
                    <span className="text-red-400 text-xs font-medium">Disabled</span>
                  ) : user.is_exempt ? (
                    <span className="text-blue-400 text-xs font-medium">Exempt</span>
                  ) : (
                    <span className="text-emerald-400 text-xs font-medium">Active</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => handleToggleDisable(user)}
                    className={`text-xs px-2 py-1 rounded ${
                      user.disabled_at
                        ? 'bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/40'
                        : 'bg-red-600/20 text-red-400 hover:bg-red-600/40'
                    }`}
                  >
                    {user.disabled_at ? 'Enable' : 'Disable'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {total > 50 && (
        <div className="flex justify-center space-x-2 mt-4">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="text-gray-400 hover:text-white disabled:opacity-30 text-sm"
          >
            Previous
          </button>
          <span className="text-gray-400 text-sm">Page {page}</span>
          <button
            onClick={() => setPage(page + 1)}
            disabled={page * 50 >= total}
            className="text-gray-400 hover:text-white disabled:opacity-30 text-sm"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}

import { useEffect, useState } from 'react'
import { api } from '../api/client'
import IPBadge from '../components/IPBadge'

interface User {
  id: number
  username: string
  admin_username: string | null
  ip_limit: number | null
  policy_name: string | null
  is_monitored: boolean
  is_exempt: boolean
  active_ip_count: number
  active_ips: string[]
  effective_limit: number
  disabled_at: string | null
  disabled_reason: string | null
  auto_reenable: boolean
}

export default function Users() {
  const [users, setUsers] = useState<User[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [adminFilter, setAdminFilter] = useState('')
  const [admins, setAdmins] = useState<string[]>([])
  const [syncing, setSyncing] = useState(false)
  const [editingUser, setEditingUser] = useState<string | null>(null)
  const [editLimit, setEditLimit] = useState('')
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState('')
  const pageSize = 50

  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  useEffect(() => {
    api.getAdmins().then((data) => setAdmins(data.admins)).catch(() => {})
  }, [])

  const loadUsers = () => {
    setLoading(true)
    api.getUsers(page, search, adminFilter).then((data) => {
      setUsers(data.users)
      setTotal(data.total)
    }).finally(() => setLoading(false))
  }

  useEffect(loadUsers, [page, search, adminFilter])

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
    try {
      setError('')
      const limit = editLimit === '' ? null : parseInt(editLimit)
      await api.updateUser(username, { ip_limit: limit })
      setEditingUser(null)
      loadUsers()
    } catch (e: any) {
      setError(e.message || 'Failed to update user')
    }
  }

  const handleToggleDisable = async (user: User) => {
    try {
      setError('')
      if (user.disabled_at) {
        await api.enableUser(user.username)
      } else {
        await api.disableUser(user.username)
      }
      loadUsers()
    } catch (e: any) {
      setError(e.message || 'Failed to toggle user status')
    }
  }

  const handleToggleMonitored = async (user: User) => {
    try {
      setError('')
      await api.updateUser(user.username, { is_monitored: !user.is_monitored })
      loadUsers()
    } catch (e: any) {
      setError(e.message || 'Failed to update user')
    }
  }

  const handleToggleExempt = async (user: User) => {
    try {
      setError('')
      await api.updateUser(user.username, { is_exempt: !user.is_exempt })
      loadUsers()
    } catch (e: any) {
      setError(e.message || 'Failed to update user')
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Users</h1>
          <p className="text-sm text-gray-400 mt-1">{total} users total</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => {
              setRefreshing(true)
              loadUsers()
              setTimeout(() => setRefreshing(false), 600)
            }}
            disabled={refreshing}
            className={`px-3 py-2 rounded text-sm transition-all ${
              refreshing
                ? 'bg-emerald-700 text-emerald-200 scale-95'
                : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
            }`}
          >
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
          <button
            onClick={handleSync}
            disabled={syncing}
            className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded text-sm disabled:opacity-50 transition-colors"
          >
            {syncing ? 'Syncing...' : 'Sync from Marzban'}
          </button>
        </div>
      </div>

      <div className="flex items-center space-x-3 mb-4">
        <input
          type="text"
          placeholder="Search users..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1) }}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white w-72 focus:outline-none focus:border-emerald-400 transition-colors"
        />
        {admins.length > 0 && (
          <select
            value={adminFilter}
            onChange={(e) => { setAdminFilter(e.target.value); setPage(1) }}
            className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-emerald-400 transition-colors"
          >
            <option value="">All Admins</option>
            {admins.map((a) => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>
        )}
        {(search || adminFilter) && (
          <button
            onClick={() => { setSearch(''); setAdminFilter(''); setPage(1) }}
            className="text-gray-400 hover:text-white text-sm transition-colors"
          >
            Clear
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3 mb-4 flex items-center justify-between">
          <p className="text-red-400 text-sm">{error}</p>
          <button onClick={() => setError('')} className="text-red-400 hover:text-red-300 text-sm ml-4">Dismiss</button>
        </div>
      )}

      <div className="bg-gray-800 rounded-lg overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">Username</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">Admin</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">Policy</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">IP Limit</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">Active IPs</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">Status</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">Monitored</th>
              <th className="text-right px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && users.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-12 text-center text-gray-500">
                  Loading...
                </td>
              </tr>
            ) : users.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-12 text-center text-gray-500">
                  {search ? 'No users match your search' : 'No users yet — click "Sync from Marzban" to import'}
                </td>
              </tr>
            ) : users.map((user) => (
              <tr key={user.id} className="border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors">
                <td className="px-4 py-3">
                  <span className="font-mono text-sm text-white">{user.username}</span>
                  {user.is_exempt && (
                    <span className="ml-2 text-[10px] bg-blue-500/20 text-blue-400 px-1.5 py-0.5 rounded">EXEMPT</span>
                  )}
                </td>
                <td className="px-4 py-3 text-sm text-gray-400">
                  {user.admin_username ? (
                    <button
                      onClick={() => { setAdminFilter(user.admin_username!); setPage(1) }}
                      className="hover:text-emerald-400 transition-colors"
                    >
                      {user.admin_username}
                    </button>
                  ) : <span className="text-gray-600">—</span>}
                </td>
                <td className="px-4 py-3 text-sm text-gray-300">{user.policy_name || <span className="text-gray-600">—</span>}</td>
                <td className="px-4 py-3 text-sm">
                  {editingUser === user.username ? (
                    <div className="flex items-center space-x-2">
                      <input
                        type="number"
                        value={editLimit}
                        onChange={(e) => setEditLimit(e.target.value)}
                        className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-white w-20 text-sm focus:outline-none focus:border-emerald-400"
                        placeholder="0=off"
                        min="0"
                        autoFocus
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleSaveLimit(user.username)
                          if (e.key === 'Escape') setEditingUser(null)
                        }}
                      />
                      <button
                        onClick={() => handleSaveLimit(user.username)}
                        className="text-emerald-400 hover:text-emerald-300 text-xs font-medium"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => setEditingUser(null)}
                        className="text-gray-400 hover:text-gray-300 text-xs"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <span
                      className="cursor-pointer hover:text-emerald-400 transition-colors group"
                      onClick={() => { setEditingUser(user.username); setEditLimit(user.ip_limit?.toString() || '') }}
                    >
                      {user.effective_limit === 0 ? (
                        <span className="text-gray-500">No limit</span>
                      ) : (
                        <>
                          {user.ip_limit ?? user.effective_limit}
                          {user.ip_limit === null && <span className="text-gray-500 text-xs ml-1">(inherited)</span>}
                        </>
                      )}
                      <span className="text-gray-600 text-xs ml-1 opacity-0 group-hover:opacity-100">edit</span>
                    </span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center space-x-2">
                    <span className={`text-sm font-medium tabular-nums ${
                      user.effective_limit > 0 && user.active_ip_count > user.effective_limit
                        ? 'text-red-400'
                        : user.active_ip_count > 0 ? 'text-emerald-400' : 'text-gray-500'
                    }`}>
                      {user.active_ip_count}
                      {user.effective_limit > 0 && <span className="text-gray-500">/{user.effective_limit}</span>}
                    </span>
                  </div>
                  {user.active_ips.length > 0 && (
                    <div className="mt-1 flex flex-wrap">
                      {user.active_ips.map((ip) => (
                        <IPBadge key={ip} ip={ip} />
                      ))}
                    </div>
                  )}
                </td>
                <td className="px-4 py-3">
                  {user.disabled_at ? (
                    <div>
                      <span className="inline-flex items-center text-red-400 text-xs font-medium bg-red-500/10 px-2 py-0.5 rounded">
                        Disabled
                      </span>
                      {user.disabled_reason && (
                        <p className="text-gray-500 text-[10px] mt-0.5 max-w-[140px] truncate" title={user.disabled_reason}>
                          {user.disabled_reason}
                        </p>
                      )}
                    </div>
                  ) : (
                    <span className="inline-flex items-center text-emerald-400 text-xs font-medium bg-emerald-500/10 px-2 py-0.5 rounded">
                      Active
                    </span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => handleToggleMonitored(user)}
                    className={`text-xs px-2 py-1 rounded transition-colors ${
                      user.is_monitored
                        ? 'bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/40'
                        : 'bg-gray-600/20 text-gray-500 hover:bg-gray-600/40'
                    }`}
                  >
                    {user.is_monitored ? 'Yes' : 'No'}
                  </button>
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="flex items-center justify-end space-x-2">
                    <button
                      onClick={() => handleToggleExempt(user)}
                      className={`text-xs px-2 py-1 rounded transition-colors ${
                        user.is_exempt
                          ? 'bg-blue-600/20 text-blue-400 hover:bg-blue-600/40'
                          : 'bg-gray-600/20 text-gray-500 hover:bg-gray-600/40'
                      }`}
                      title={user.is_exempt ? 'Remove exemption' : 'Mark as exempt'}
                    >
                      {user.is_exempt ? 'Exempt' : 'Enforce'}
                    </button>
                    <button
                      onClick={() => handleToggleDisable(user)}
                      className={`text-xs px-2 py-1 rounded transition-colors ${
                        user.disabled_at
                          ? 'bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/40'
                          : 'bg-red-600/20 text-red-400 hover:bg-red-600/40'
                      }`}
                    >
                      {user.disabled_at ? 'Enable' : 'Disable'}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between mt-4">
        <p className="text-sm text-gray-500">
          Showing {users.length > 0 ? (page - 1) * pageSize + 1 : 0}–{Math.min(page * pageSize, total)} of {total}
        </p>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setPage(1)}
            disabled={page === 1}
            className="text-gray-400 hover:text-white disabled:opacity-30 text-sm px-2 py-1 transition-colors"
          >
            First
          </button>
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="text-gray-400 hover:text-white disabled:opacity-30 text-sm px-2 py-1 transition-colors"
          >
            Prev
          </button>
          <span className="text-gray-300 text-sm font-medium px-3">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage(page + 1)}
            disabled={page >= totalPages}
            className="text-gray-400 hover:text-white disabled:opacity-30 text-sm px-2 py-1 transition-colors"
          >
            Next
          </button>
          <button
            onClick={() => setPage(totalPages)}
            disabled={page >= totalPages}
            className="text-gray-400 hover:text-white disabled:opacity-30 text-sm px-2 py-1 transition-colors"
          >
            Last
          </button>
        </div>
      </div>
    </div>
  )
}

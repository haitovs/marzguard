import { useEffect, useState } from 'react'
import { api } from '../api/client'

interface LogEntry {
  id: number
  timestamp: string
  event_type: string
  username: string | null
  details: string | null
  source: string
}

const EVENT_LABELS: Record<string, string> = {
  user_disabled: 'User Disabled',
  user_reenabled: 'User Re-enabled',
  user_enabled: 'User Enabled',
  user_updated: 'User Updated',
  webhook_event: 'Webhook',
}

export default function AuditLog() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [eventType, setEventType] = useState('')
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(true)
  const pageSize = 50

  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  useEffect(() => {
    setLoading(true)
    api.getLogs(page, eventType, username).then((data) => {
      setLogs(data.logs)
      setTotal(data.total)
    }).finally(() => setLoading(false))
  }, [page, eventType, username])

  const eventColor = (type: string) => {
    if (type.includes('disabled')) return 'bg-red-500/10 text-red-400'
    if (type.includes('reenabled') || type.includes('enabled')) return 'bg-emerald-500/10 text-emerald-400'
    if (type.includes('updated')) return 'bg-blue-500/10 text-blue-400'
    if (type.includes('webhook')) return 'bg-purple-500/10 text-purple-400'
    return 'bg-gray-500/10 text-gray-300'
  }

  const formatTime = (ts: string) => {
    const d = new Date(ts)
    const now = new Date()
    const diffMs = now.getTime() - d.getTime()
    const diffMin = Math.floor(diffMs / 60000)

    if (diffMin < 1) return 'Just now'
    if (diffMin < 60) return `${diffMin}m ago`
    if (diffMin < 1440) return `${Math.floor(diffMin / 60)}h ago`

    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) + ' ' +
      d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Audit Log</h1>
          <p className="text-sm text-gray-400 mt-1">{total} entries</p>
        </div>
      </div>

      <div className="flex space-x-3 mb-4">
        <select
          value={eventType}
          onChange={(e) => { setEventType(e.target.value); setPage(1) }}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-emerald-400 transition-colors"
        >
          <option value="">All Events</option>
          <option value="user_disabled">User Disabled</option>
          <option value="user_reenabled">User Re-enabled</option>
          <option value="user_updated">User Updated</option>
          <option value="webhook_event">Webhook</option>
        </select>
        <input
          type="text"
          placeholder="Filter by username..."
          value={username}
          onChange={(e) => { setUsername(e.target.value); setPage(1) }}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm w-56 focus:outline-none focus:border-emerald-400 transition-colors"
        />
        {(eventType || username) && (
          <button
            onClick={() => { setEventType(''); setUsername(''); setPage(1) }}
            className="text-gray-400 hover:text-white text-sm px-3 py-2 transition-colors"
          >
            Clear filters
          </button>
        )}
      </div>

      <div className="bg-gray-800 rounded-lg overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">Time</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">Event</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">User</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">Details</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase tracking-wider">Source</th>
            </tr>
          </thead>
          <tbody>
            {loading && logs.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-12 text-center text-gray-500">
                  Loading...
                </td>
              </tr>
            ) : logs.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-12 text-center text-gray-500">
                  {eventType || username ? 'No entries match your filters' : 'No log entries yet'}
                </td>
              </tr>
            ) : logs.map((log) => (
              <tr key={log.id} className="border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors">
                <td className="px-4 py-3 text-xs text-gray-400 whitespace-nowrap" title={new Date(log.timestamp).toLocaleString()}>
                  {formatTime(log.timestamp)}
                </td>
                <td className="px-4 py-3">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded ${eventColor(log.event_type)}`}>
                    {EVENT_LABELS[log.event_type] || log.event_type}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-white font-mono">{log.username || <span className="text-gray-600">—</span>}</td>
                <td className="px-4 py-3 text-xs text-gray-400 max-w-md truncate" title={log.details || ''}>
                  {log.details || <span className="text-gray-600">—</span>}
                </td>
                <td className="px-4 py-3">
                  <span className={`text-xs px-1.5 py-0.5 rounded ${
                    log.source === 'enforcer' ? 'bg-yellow-500/10 text-yellow-400' :
                    log.source === 'admin' ? 'bg-blue-500/10 text-blue-400' :
                    'bg-gray-500/10 text-gray-400'
                  }`}>
                    {log.source}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between mt-4">
        <p className="text-sm text-gray-500">
          Showing {logs.length > 0 ? (page - 1) * pageSize + 1 : 0}–{Math.min(page * pageSize, total)} of {total}
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

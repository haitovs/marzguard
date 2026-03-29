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

export default function AuditLog() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [eventType, setEventType] = useState('')
  const [username, setUsername] = useState('')

  useEffect(() => {
    api.getLogs(page, eventType, username).then((data) => {
      setLogs(data.logs)
      setTotal(data.total)
    })
  }, [page, eventType, username])

  const eventColor = (type: string) => {
    if (type.includes('disabled')) return 'text-red-400'
    if (type.includes('reenabled') || type.includes('enabled')) return 'text-emerald-400'
    if (type.includes('updated')) return 'text-blue-400'
    return 'text-gray-300'
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">Audit Log</h1>

      <div className="flex space-x-4 mb-4">
        <select
          value={eventType}
          onChange={(e) => { setEventType(e.target.value); setPage(1) }}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm"
        >
          <option value="">All Events</option>
          <option value="user_disabled">User Disabled</option>
          <option value="user_reenabled">User Re-enabled</option>
          <option value="user_updated">User Updated</option>
        </select>
        <input
          type="text"
          placeholder="Filter by username..."
          value={username}
          onChange={(e) => { setUsername(e.target.value); setPage(1) }}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm w-48"
        />
      </div>

      <div className="bg-gray-800 rounded-lg overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase">Time</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase">Event</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase">User</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase">Details</th>
              <th className="text-left px-4 py-3 text-xs text-gray-400 uppercase">Source</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} className="border-b border-gray-700/50">
                <td className="px-4 py-3 text-xs text-gray-400 whitespace-nowrap">
                  {new Date(log.timestamp).toLocaleString()}
                </td>
                <td className={`px-4 py-3 text-sm font-medium ${eventColor(log.event_type)}`}>
                  {log.event_type}
                </td>
                <td className="px-4 py-3 text-sm text-white font-mono">{log.username || '-'}</td>
                <td className="px-4 py-3 text-xs text-gray-400 max-w-md truncate">{log.details}</td>
                <td className="px-4 py-3 text-xs text-gray-500">{log.source}</td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                  No log entries
                </td>
              </tr>
            )}
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
          <span className="text-gray-400 text-sm">Page {page} of {Math.ceil(total / 50)}</span>
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

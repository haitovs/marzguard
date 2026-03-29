import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useWebSocket } from '../hooks/useWebSocket'
import StatusIndicator from '../components/StatusIndicator'
import IPBadge from '../components/IPBadge'

interface Summary {
  total_users: number
  monitored_users: number
  active_users: number
  disabled_users: number
  total_active_ips: number
  violations_today: number
}

export default function Dashboard() {
  const [summary, setSummary] = useState<Summary | null>(null)
  const { data: wsData, connected } = useWebSocket()
  const [searchLive, setSearchLive] = useState('')

  useEffect(() => {
    api.getSummary().then(setSummary).catch(console.error)
    const interval = setInterval(() => {
      api.getSummary().then(setSummary).catch(console.error)
    }, 30000)
    return () => clearInterval(interval)
  }, [])

  const stats = [
    { label: 'Total Users', value: summary?.total_users ?? '—', icon: '~' },
    { label: 'Monitored', value: summary?.monitored_users ?? '—', icon: '~' },
    { label: 'Active Now', value: wsData?.total_users ?? summary?.active_users ?? '—', color: 'text-emerald-400' },
    { label: 'Active IPs', value: wsData?.total_ips ?? summary?.total_active_ips ?? '—', color: 'text-emerald-400' },
    { label: 'Disabled', value: summary?.disabled_users ?? '—', color: summary?.disabled_users ? 'text-red-400' : undefined },
    { label: 'Violations Today', value: summary?.violations_today ?? '—', color: summary?.violations_today ? 'text-yellow-400' : undefined },
  ]

  const filteredUsers = wsData
    ? Object.entries(wsData.users)
        .filter(([username]) => !searchLive || username.toLowerCase().includes(searchLive.toLowerCase()))
        .sort(([, a], [, b]) => b.count - a.count)
    : []

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <StatusIndicator connected={connected} />
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-gray-800 rounded-lg p-4 border border-gray-700/50">
            <p className="text-gray-400 text-xs uppercase tracking-wide">{stat.label}</p>
            <p className={`text-2xl font-bold mt-1 tabular-nums ${stat.color || 'text-white'}`}>
              {stat.value}
            </p>
          </div>
        ))}
      </div>

      {/* Live connections */}
      <div className="bg-gray-800 rounded-lg border border-gray-700/50">
        <div className="flex items-center justify-between p-4 border-b border-gray-700/50">
          <div className="flex items-center space-x-3">
            <h2 className="text-lg font-semibold text-white">Live Connections</h2>
            {wsData && (
              <span className="text-xs text-gray-400 bg-gray-700 px-2 py-0.5 rounded-full">
                {Object.keys(wsData.users).length} users
              </span>
            )}
          </div>
          {wsData && Object.keys(wsData.users).length > 5 && (
            <input
              type="text"
              placeholder="Filter users..."
              value={searchLive}
              onChange={(e) => setSearchLive(e.target.value)}
              className="bg-gray-700 border border-gray-600 rounded px-3 py-1.5 text-white text-sm w-48 focus:outline-none focus:border-emerald-400 transition-colors"
            />
          )}
        </div>
        <div className="p-4">
          {filteredUsers.length > 0 ? (
            <div className="space-y-2 max-h-[500px] overflow-y-auto">
              {filteredUsers.map(([username, info]) => (
                <div
                  key={username}
                  className="flex items-center justify-between bg-gray-700/40 rounded-lg px-4 py-2.5 hover:bg-gray-700/60 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 rounded-full bg-emerald-400 shrink-0" />
                    <span className="text-white font-mono text-sm">{username}</span>
                    <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${
                      info.count > 2 ? 'bg-yellow-500/10 text-yellow-400' : 'bg-gray-600/50 text-gray-400'
                    }`}>
                      {info.count} IP{info.count !== 1 ? 's' : ''}
                    </span>
                  </div>
                  <div className="flex flex-wrap justify-end gap-1">
                    {info.ips.map((ip) => (
                      <IPBadge key={ip} ip={ip} />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm text-center py-8">
              {searchLive ? 'No users match your filter' : connected ? 'No active connections' : 'Connecting to live stream...'}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

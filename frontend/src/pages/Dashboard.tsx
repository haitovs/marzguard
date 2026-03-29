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

  useEffect(() => {
    api.getSummary().then(setSummary).catch(console.error)
    const interval = setInterval(() => {
      api.getSummary().then(setSummary).catch(console.error)
    }, 30000)
    return () => clearInterval(interval)
  }, [])

  const stats = [
    { label: 'Total Users', value: summary?.total_users ?? '-' },
    { label: 'Monitored', value: summary?.monitored_users ?? '-' },
    { label: 'Active Now', value: wsData?.total_users ?? summary?.active_users ?? '-' },
    { label: 'Active IPs', value: wsData?.total_ips ?? summary?.total_active_ips ?? '-' },
    { label: 'Disabled', value: summary?.disabled_users ?? '-', color: 'text-red-400' },
    { label: 'Violations Today', value: summary?.violations_today ?? '-', color: 'text-yellow-400' },
  ]

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <StatusIndicator connected={connected} />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-gray-800 rounded-lg p-4">
            <p className="text-gray-400 text-xs uppercase tracking-wide">{stat.label}</p>
            <p className={`text-2xl font-bold mt-1 ${(stat as any).color || 'text-white'}`}>
              {stat.value}
            </p>
          </div>
        ))}
      </div>

      <div className="bg-gray-800 rounded-lg p-4">
        <h2 className="text-lg font-semibold text-white mb-4">Live Connections</h2>
        {wsData && Object.keys(wsData.users).length > 0 ? (
          <div className="space-y-2">
            {Object.entries(wsData.users)
              .sort(([, a], [, b]) => b.count - a.count)
              .map(([username, info]) => (
                <div
                  key={username}
                  className="flex items-center justify-between bg-gray-700/50 rounded px-3 py-2"
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-white font-mono text-sm">{username}</span>
                    <span className="text-gray-400 text-xs">{info.count} IP(s)</span>
                  </div>
                  <div className="flex flex-wrap justify-end">
                    {info.ips.map((ip) => (
                      <IPBadge key={ip} ip={ip} />
                    ))}
                  </div>
                </div>
              ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No active connections</p>
        )}
      </div>
    </div>
  )
}

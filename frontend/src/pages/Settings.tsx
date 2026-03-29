import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function Settings() {
  const [settings, setSettings] = useState<Record<string, string>>({})
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    api.getSettings().then((data) => setSettings(data.settings))
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      await api.updateSettings({ settings })
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } finally {
      setSaving(false)
    }
  }

  const updateSetting = (key: string, value: string) => {
    setSettings((prev) => ({ ...prev, [key]: value }))
  }

  const settingFields = [
    {
      key: 'default_ip_limit',
      label: 'Default IP Limit',
      type: 'number',
      description: 'Global IP limit for users without a specific limit. Set to 0 to disable enforcement by default.',
    },
    {
      key: 'ip_ttl_seconds',
      label: 'IP TTL (seconds)',
      type: 'number',
      description: 'How long an IP is considered "active" after last connection.',
    },
    {
      key: 'enforcement_interval',
      label: 'Enforcement Interval (seconds)',
      type: 'number',
      description: 'How often the enforcer checks for violations.',
    },
    {
      key: 'reenable_check_interval',
      label: 'Re-enable Check Interval (seconds)',
      type: 'number',
      description: 'How often to check if disabled users can be re-enabled.',
    },
    {
      key: 'default_reenable_delay',
      label: 'Default Re-enable Delay (seconds)',
      type: 'number',
      description: 'How long to wait before auto re-enabling a disabled user.',
    },
  ]

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">Settings</h1>
      <div className="bg-gray-800 rounded-lg border border-gray-700/50 p-6 max-w-xl">
        <div className="space-y-5">
          {settingFields.map((field) => (
            <div key={field.key}>
              <label className="block text-sm font-medium text-gray-300 mb-1">{field.label}</label>
              <input
                type={field.type}
                value={settings[field.key] || ''}
                onChange={(e) => updateSetting(field.key, e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-emerald-400 transition-colors"
                min="0"
              />
              <p className="text-xs text-gray-500 mt-1">{field.description}</p>
            </div>
          ))}
        </div>
        <div className="mt-6 flex items-center space-x-3 pt-4 border-t border-gray-700/50">
          <button
            onClick={handleSave}
            disabled={saving}
            className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2 rounded text-sm font-medium disabled:opacity-50 transition-colors"
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
          {saved && <span className="text-emerald-400 text-sm">Settings saved successfully</span>}
        </div>
      </div>

      <div className="mt-8 bg-gray-800 rounded-lg border border-gray-700/50 p-6 max-w-xl">
        <h2 className="text-lg font-semibold text-white mb-3">How IP limits work</h2>
        <div className="space-y-2 text-sm text-gray-400">
          <p>IP limits are resolved in a 3-tier cascade:</p>
          <ol className="list-decimal list-inside space-y-1 ml-2">
            <li><span className="text-white">User-specific limit</span> — set per user in the Users page</li>
            <li><span className="text-white">Policy limit</span> — inherited from assigned policy</li>
            <li><span className="text-white">Global default</span> — the Default IP Limit above</li>
          </ol>
          <p className="mt-3">
            Setting the global default to <span className="text-white font-mono">0</span> disables enforcement for all users
            who don't have an explicit limit set (either directly or via policy).
          </p>
        </div>
      </div>
    </div>
  )
}

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
    { key: 'default_ip_limit', label: 'Default IP Limit', type: 'number' },
    { key: 'ip_ttl_seconds', label: 'IP TTL (seconds)', type: 'number' },
    { key: 'enforcement_interval', label: 'Enforcement Interval (seconds)', type: 'number' },
    { key: 'reenable_check_interval', label: 'Re-enable Check Interval (seconds)', type: 'number' },
    { key: 'default_reenable_delay', label: 'Default Re-enable Delay (seconds)', type: 'number' },
  ]

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">Settings</h1>
      <div className="bg-gray-800 rounded-lg p-6 max-w-lg">
        <div className="space-y-4">
          {settingFields.map((field) => (
            <div key={field.key}>
              <label className="block text-sm text-gray-400 mb-1">{field.label}</label>
              <input
                type={field.type}
                value={settings[field.key] || ''}
                onChange={(e) => updateSetting(field.key, e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-emerald-400"
              />
            </div>
          ))}
        </div>
        <div className="mt-6 flex items-center space-x-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded text-sm disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
          {saved && <span className="text-emerald-400 text-sm">Saved!</span>}
        </div>
      </div>
    </div>
  )
}

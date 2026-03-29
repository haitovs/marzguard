interface Props {
  connected: boolean
}

export default function StatusIndicator({ connected }: Props) {
  return (
    <div className="flex items-center space-x-2">
      <div
        className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-400' : 'bg-red-400'}`}
      />
      <span className="text-xs text-gray-400">
        {connected ? 'Live' : 'Disconnected'}
      </span>
    </div>
  )
}

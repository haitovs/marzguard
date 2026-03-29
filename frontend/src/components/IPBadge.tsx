interface Props {
  ip: string
}

export default function IPBadge({ ip }: Props) {
  return (
    <span className="inline-block bg-gray-700 text-gray-300 text-xs px-2 py-0.5 rounded-full mr-1 mb-1 font-mono">
      {ip}
    </span>
  )
}

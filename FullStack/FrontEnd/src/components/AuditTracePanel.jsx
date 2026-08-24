function AuditTracePanel() {
  return (
    <div className="bg-gray-900 text-white px-3 py-2 rounded-lg shrink-0">
      <h2 className="font-semibold text-sm mb-1">Auditable Execution Trace</h2>
      <div className="space-y-1 text-xs">
        <div className="flex justify-between">
          <span className="text-gray-400">Task:</span>
          <span>Bi-Temporal Change</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Tool:</span>
          <span>Change-Adapter-v2</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Execution Time:</span>
          <span>0.82s</span>
        </div>
      </div>
    </div>
  )
}

export default AuditTracePanel
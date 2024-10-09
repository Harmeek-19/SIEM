import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"

export default function DynamicDialog({ isOpen, onOpenChange, selectedAnomaly }) {
  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 shadow-lg">
        <DialogHeader>
          <DialogTitle className="text-lg font-semibold text-gray-900 dark:text-gray-100">Anomaly Details</DialogTitle>
        </DialogHeader>
        {selectedAnomaly && (
          <div className="text-sm text-gray-700 dark:text-gray-300">
            <p><strong>ID:</strong> {selectedAnomaly.id}</p>
            <p><strong>Event Type:</strong> {selectedAnomaly.event_type}</p>
            <p><strong>Timestamp:</strong> {new Date(selectedAnomaly.timestamp).toLocaleString()}</p>
            <p><strong>Risk Score:</strong> {selectedAnomaly.risk_score}</p>
            <p><strong>Source IP:</strong> {selectedAnomaly.source_ip}</p>
            <p><strong>Destination IP:</strong> {selectedAnomaly.destination_ip}</p>
            <p><strong>Description:</strong> {selectedAnomaly.description}</p>
            <p><strong>Raw Data:</strong> {JSON.stringify(selectedAnomaly.raw_data, null, 2)}</p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
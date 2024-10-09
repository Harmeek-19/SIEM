import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"

export default function DynamicTable({ anomaliesList, handleInvestigate }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>ID</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Timestamp</TableHead>
          <TableHead>Risk Score</TableHead>
          <TableHead>Action</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {anomaliesList.map((anomaly) => (
          <TableRow key={anomaly.id}>
            <TableCell>{anomaly.id}</TableCell>
            <TableCell>{anomaly.event_type}</TableCell>
            <TableCell>{new Date(anomaly.timestamp).toLocaleString()}</TableCell>
            <TableCell>{anomaly.risk_score}</TableCell>
            <TableCell>
              <Button onClick={() => handleInvestigate(anomaly.id)}>Investigate</Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
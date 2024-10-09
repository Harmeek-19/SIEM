'use client'

import { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { anomalies } from '@/services/api'

const DynamicTable = dynamic(() => import('@/components/ui/DynamicTable'), { ssr: false })
const DynamicDialog = dynamic(() => import('@/components/ui/DynamicDialog'), { ssr: false })

export default function AnomaliesPage() {
  const [isClient, setIsClient] = useState(false)
  const [anomaliesList, setAnomaliesList] = useState([])
  const [selectedAnomaly, setSelectedAnomaly] = useState(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  useEffect(() => {
    setIsClient(true)
    const fetchAnomalies = async () => {
      try {
        const data = await anomalies.getAll()
        setAnomaliesList(data)
      } catch (error) {
        console.error('Failed to fetch anomalies:', error)
      }
    }
    fetchAnomalies()
  }, [])

  const handleInvestigate = async (id) => {
    try {
      const details = await anomalies.getDetails(id)
      setSelectedAnomaly(details)
      setIsDialogOpen(true)
    } catch (error) {
      console.error('Failed to fetch anomaly details:', error)
    }
  }

  if (!isClient) {
    return null // or a loading spinner
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Detected Anomalies</CardTitle>
      </CardHeader>
      <CardContent>
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

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
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
      </CardContent>
    </Card>
  )
}
'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { alerts } from '@/services/api'

export default function Alerts() {
  const [alertsList, setAlertsList] = useState([])

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const data = await alerts.getAll()
        setAlertsList(data)
      } catch (error) {
        console.error('Failed to fetch alerts:', error)
      }
    }
    fetchAlerts()
  }, [])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Alerts</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Severity</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {alertsList.map((alert) => (
              <TableRow key={alert.id}>
                <TableCell>{alert.id}</TableCell>
                <TableCell>{alert.title}</TableCell>
                <TableCell>{alert.severity}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
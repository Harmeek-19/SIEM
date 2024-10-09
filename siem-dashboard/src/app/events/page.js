'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { securityEvents } from '@/services/api'

export default function EventsPage() {
  const [events, setEvents] = useState([])

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const data = await securityEvents.getAll()
        setEvents(data)
      } catch (error) {
        console.error('Failed to fetch security events:', error)
      }
    }
    fetchEvents()
  }, [])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Security Events</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Type</TableHead>
              <TableHead>Severity</TableHead>
              <TableHead>Timestamp</TableHead>
              <TableHead>Description</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {events.map((event) => (
              <TableRow key={event.id}>
                <TableCell>{event.event_type}</TableCell>
                <TableCell>{event.severity}</TableCell>
                <TableCell>{event.timestamp}</TableCell>
                <TableCell>{event.description}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
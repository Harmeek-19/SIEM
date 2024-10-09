'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { securityEvents } from '@/services/api'

export default function SecurityEvents() {
  const [events, setEvents] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const eventsPerPage = 10

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

  const filteredEvents = events.filter(event =>
    event.event_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    event.severity.toString().includes(searchTerm)
  )

  const indexOfLastEvent = currentPage * eventsPerPage
  const indexOfFirstEvent = indexOfLastEvent - eventsPerPage
  const currentEvents = filteredEvents.slice(indexOfFirstEvent, indexOfLastEvent)

  const paginate = (pageNumber) => setCurrentPage(pageNumber)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Security Events</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <Input
            type="text"
            placeholder="Search events..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Event Type</TableHead>
              <TableHead>Severity</TableHead>
              <TableHead>Timestamp</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {currentEvents.map((event, index) => (
              <TableRow key={index}>
                <TableCell>{event.event_type}</TableCell>
                <TableCell>{event.severity}</TableCell>
                <TableCell>{new Date(event.timestamp).toLocaleString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <div className="mt-4 flex justify-between">
          <Button
            onClick={() => paginate(currentPage - 1)}
            disabled={currentPage === 1}
          >
            Previous
          </Button>
          <Button
            onClick={() => paginate(currentPage + 1)}
            disabled={indexOfLastEvent >= filteredEvents.length}
          >
            Next
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
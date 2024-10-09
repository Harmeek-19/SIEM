'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { iocs } from '@/services/api'

export default function ThreatIntelligence() {
  const [iocList, setIocList] = useState([])

  useEffect(() => {
    const fetchIOCs = async () => {
      try {
        const data = await iocs.getAll()
        setIocList(data)
      } catch (error) {
        console.error('Failed to fetch IOCs:', error)
      }
    }
    fetchIOCs()
  }, [])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Threat Intelligence</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Type</TableHead>
              <TableHead>Value</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {iocList.map((ioc, index) => (
              <TableRow key={index}>
                <TableCell>{ioc.type}</TableCell>
                <TableCell>{ioc.value}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
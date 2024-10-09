'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { correlation } from '@/services/api'

export default function Correlation() {
  const [timeWindow, setTimeWindow] = useState(60)
  const [correlationResult, setCorrelationResult] = useState(null)

  const runCorrelation = async () => {
    try {
      const result = await correlation.run(timeWindow)
      setCorrelationResult(result)
    } catch (error) {
      console.error('Failed to run correlation:', error)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Event Correlation</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <label htmlFor="timeWindow" className="block mb-2">Time Window (minutes)</label>
          <Input
            id="timeWindow"
            type="number"
            value={timeWindow}
            onChange={(e) => setTimeWindow(e.target.value)}
            className="w-full"
          />
        </div>
        <Button onClick={runCorrelation}>Run Correlation</Button>
        {correlationResult && (
          <div className="mt-4">
            <h3 className="text-lg font-semibold">Correlation Results</h3>
            <p>Correlated groups: {correlationResult.correlated_groups}</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
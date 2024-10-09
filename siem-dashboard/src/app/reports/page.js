'use client'
import { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { reports } from '@/services/api'

const DynamicReportContent = dynamic(() => import('@/components/ui/DynamicReportContent'), { ssr: false })

export default function Reports() {
  const [isClient, setIsClient] = useState(false)
  const [reportType, setReportType] = useState('daily')
  const [generatedReport, setGeneratedReport] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [emailNotification, setEmailNotification] = useState(false)

  useEffect(() => {
    setIsClient(true)
  }, [])

  const generateReport = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const report = await reports.generate(reportType, emailNotification)
      setGeneratedReport(report)
    } catch (error) {
      console.error('Failed to generate report:', error)
      setError('Failed to generate report. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  if (!isClient) {
    return null
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Reports</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <label htmlFor="reportType" className="block mb-2 text-sm font-medium text-gray-700">Report Type</label>
          <Select value={reportType} onValueChange={setReportType}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select report type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="daily">Daily</SelectItem>
              <SelectItem value="weekly">Weekly</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-center space-x-2 mb-4">
          <Switch
            id="email-notification"
            checked={emailNotification}
            onCheckedChange={setEmailNotification}
          />
          <label htmlFor="email-notification" className="text-sm font-medium text-gray-700">
            Send Email Notification
          </label>
        </div>
        <Button onClick={generateReport} disabled={isLoading} className="bg-blue-500 text-white hover:bg-blue-600">
        {isLoading ? 'Generating...' : 'Generate Report'}
        </Button>
        {error && <p className="text-red-500 mt-2">{error}</p>}
        {generatedReport && <DynamicReportContent report={generatedReport} />}
      </CardContent>
    </Card>
  )
}
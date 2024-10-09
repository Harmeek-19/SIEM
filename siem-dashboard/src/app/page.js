'use client'

import { threatIntelligence } from '@/services/api'
import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/Alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Activity, AlertTriangle, CheckCircle, Clock } from 'lucide-react'
import { securityEvents, alerts, iocs, anomalies } from '@/services/api'
import { useRouter } from 'next/navigation'

export default function SIEMDashboard() {
  const [eventCount, setEventCount] = useState(0)
  const [alertCount, setAlertCount] = useState(0)
  const [iocCount, setIocCount] = useState(0)
  const [anomalyCount, setAnomalyCount] = useState(0)
  const [recentEvents, setRecentEvents] = useState([])
  const [eventsTrend, setEventsTrend] = useState([])
  const [taskStatus, setTaskStatus] = useState(null)
  const [alert, setAlert] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    fetchMetrics()
    fetchRecentEvents()
    fetchEventsTrend()
  }, [])

  useEffect(() => {
    if (taskStatus && taskStatus.status === 'in progress') {
      const timer = setInterval(() => {
        setProgress((oldProgress) => {
          const newProgress = Math.min(oldProgress + 10, 100)
          if (newProgress === 100) {
            clearInterval(timer)
            setTaskStatus({ ...taskStatus, status: 'completed' })
          }
          return newProgress
        })
      }, 1000)
      return () => clearInterval(timer)
    }
  }, [taskStatus])

  const router = useRouter()

  const handleCardClick = (type) => {
    switch(type) {
      case 'events':
        router.push('/events')
        break
      case 'alerts':
        router.push('/alerts')
        break
      case 'iocs':
        router.push('/intel')
        break
      case 'anomalies':
        router.push('/anomalies')
        break
    }
  }

  const fetchMetrics = async () => {
    try {
      const summary = await securityEvents.getSummary()
      setEventCount(summary.total_events)

      const alertsData = await alerts.getAll()
      setAlertCount(alertsData.length)

      const iocsData = await iocs.getAll()
      setIocCount(iocsData.length)

      const anomaliesData = await anomalies.getAll()
      setAnomalyCount(anomaliesData.length)
    } catch (error) {
      console.error('Error fetching metrics:', error)
      setAlert({ type: 'destructive', title: 'Error', description: 'Failed to fetch metrics. Please try again.' })
    }
  }

  const fetchRecentEvents = async () => {
    try {
      const data = await securityEvents.getRecent()
      setRecentEvents(data.results || [])
    } catch (error) {
      console.error('Error fetching recent events:', error)
      setAlert({ type: 'destructive', title: 'Error', description: 'Failed to fetch recent events. Please try again.' })
    }
  }

  const fetchEventsTrend = async () => {
    try {
      const summary = await securityEvents.getSummary()
      const trend = summary.by_type.map(item => ({
        name: item.event_type,
        count: item.count
      }))
      setEventsTrend(trend)
    } catch (error) {
      console.error('Error fetching events trend:', error)
      setAlert({ type: 'destructive', title: 'Error', description: 'Failed to fetch events trend. Please try again.' })
    }
  }

  const runMLAnomalyDetection = async () => {
    try {
      const response = await securityEvents.runMLAnomalyDetection()
      setTaskStatus({ type: 'ML Detection', id: response.task_id, status: 'in progress' })
      setProgress(0)
      setAlert({ type: 'default', title: 'ML Anomaly Detection', description: 'Task started successfully.' })
    } catch (error) {
      console.error('Failed to start ML anomaly detection:', error)
      setAlert({ type: 'destructive', title: 'Error', description: 'Failed to start ML anomaly detection. Please try again.' })
    }
  }

  const initiateLogCollection = async () => {
    try {
      const response = await securityEvents.initiateLogCollection()
      setTaskStatus({ type: 'Log Collection', id: response.task_id, status: 'in progress' })
      setProgress(0)
      setAlert({ type: 'default', title: 'Log Collection', description: 'Task started successfully.' })
    } catch (error) {
      console.error('Failed to start log collection:', error)
      setAlert({ type: 'destructive', title: 'Error', description: 'Failed to start log collection. Please try again.' })
    }
  }

  const stopTask = async () => {
    if (!taskStatus) {
      setAlert({ type: 'destructive', title: 'Error', description: 'No active task to stop.' })
      return
    }
    try {
      if (taskStatus.type === 'Log Collection') {
        await securityEvents.stopLogCollection(taskStatus.id)
      }
      setTaskStatus(null)
      setProgress(0)
      setAlert({ type: 'default', title: 'Task Stopped', description: 'Task stopped successfully.' })
    } catch (error) {
      console.error('Failed to stop task:', error)
      setAlert({ type: 'destructive', title: 'Error', description: 'Failed to stop task. Please try again.' })
    }
  }

  const checkTaskStatus = async () => {
    if (!taskStatus) {
      setAlert({ type: 'destructive', title: 'Error', description: 'No active task to check status.' })
      return
    }
    try {
      const status = await securityEvents.checkTaskStatus(taskStatus.id)
      setTaskStatus({ ...taskStatus, status: status.status, result: status.result })
      setAlert({ type: 'default', title: 'Task Status', description: `Current status: ${status.status}` })
    } catch (error) {
      console.error('Failed to check task status:', error)
      setAlert({ type: 'destructive', title: 'Error', description: 'Failed to check task status. Please try again.' })
    }
  }

  const updateThreatFeed = async () => {
    try {
      const response = await threatIntelligence.updateFeed()
      setAlert({ type: 'default', title: 'Threat Feed Update', description: 'Threat feed update task started successfully.' })
    } catch (error) {
      console.error('Failed to update threat feed:', error)
      setAlert({ type: 'destructive', title: 'Error', description: 'Failed to update threat feed. Please try again.' })
    }
  }

  return (
    <div className="space-y-8">
      <Card className="card">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Welcome to SIEM Dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-lg mb-4">
            Our Security Information and Event Management (SIEM) tool provides comprehensive security monitoring, 
            threat detection, and incident response capabilities for your organization.
          </p>
        </CardContent>
      </Card>

      
      <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid  w-full grid-cols-3">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="operations">Operations</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>
        <TabsContent value="overview">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="card" interactive onClick={() => handleCardClick('events')}>
              <CardHeader>
                <CardTitle>Total Events</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-2">
                  <Activity className="h-6 w-6 text-green-500" />
                  <p className="text-2xl font-bold">{eventCount}</p>
                </div>
              </CardContent>
            </Card>
            <Card className="card" interactive onClick={() => handleCardClick('alerts')}>
              <CardHeader>
                <CardTitle>Active Alerts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-6 w-6 text-yellow-500" />
                  <p className="text-2xl font-bold">{alertCount}</p>
                </div>
              </CardContent>
            </Card>
            <Card className="card" interactive onClick={() => handleCardClick('iocs')}>
              <CardHeader>
                <CardTitle>IOC Count</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-2">
                  <Clock className="h-6 w-6 text-blue-500" />
                  <p className="text-2xl font-bold">{iocCount}</p>
                </div>
              </CardContent>
            </Card>
            <Card className="card" interactive onClick={() => handleCardClick('anomalies')}>
              <CardHeader>
                <CardTitle>Anomaly Count</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-6 w-6 text-red-500" />
                  <p className="text-2xl font-bold">{anomalyCount}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        <TabsContent value="operations">
          <Card className="card">
            <CardHeader>
              <CardTitle>System Operations</CardTitle>
            </CardHeader>
            <CardContent>
              {alert && (
                <Alert variant={alert.type} className={`alert alert-${alert.type} mb-4`}>
                  <AlertTitle>{alert.title}</AlertTitle>
                  <AlertDescription>{alert.description}</AlertDescription>
                </Alert>
              )}

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <h3 className="text-lg font-semibold mb-2">Log Collection</h3>
                  <p className="mb-2">Collect and analyze logs from various sources in real-time.</p>
                  <Button className="btn btn-primary" onClick={initiateLogCollection} disabled={taskStatus !== null}>Start Log Collection</Button>
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-2">ML Anomaly Detection</h3>
                  <p className="mb-2">Run machine learning algorithms to detect anomalies in your data.</p>
                  <Button className="btn btn-primary" onClick={runMLAnomalyDetection} disabled={taskStatus !== null}>Run ML Anomaly Detection</Button>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-2">Update Threat Feed</h3>
                <p className="mb-2">Update the threat intelligence feed with the latest data.</p>
                <Button className="btn btn-primary" onClick={updateThreatFeed}>Update Threat Feed</Button>
              </div>

              {taskStatus && (
                <div className="mb-6 p-4 bg-gray-100 rounded-lg">
                  <h3 className="text-lg font-semibold mb-2">Current Task</h3>
                  <div className="flex items-center justify-between mb-2">
                    <p><strong>Type:</strong> {taskStatus.type}</p>
                    <Badge variant={taskStatus.status === 'completed' ? 'success' : 'default'}>
                      {taskStatus.status === 'completed' ? <CheckCircle className="mr-1 h-4 w-4" /> : null}
                      {taskStatus.status}
                    </Badge>
                  </div>
                  <Progress value={progress} className="mb-2" />
                  <div className="flex space-x-2">
                    <Button className="btn btn-danger" onClick={stopTask} variant="destructive" disabled={taskStatus.status === 'completed'}>
                      {taskStatus.status === 'completed' ? 'Clear Task' : 'Stop Task'}
                    </Button>
                    <Button className="btn btn-secondary" onClick={checkTaskStatus} variant="outline">Check Status</Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="analytics">
          <Card className="card">
            <CardHeader>
              <CardTitle>Security Events Trend</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={eventsTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e9ecef" />
                    <XAxis dataKey="name" stroke="#495057" />
                    <YAxis stroke="#495057" />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="count" stroke="#0d6efd" activeDot={{ r: 8 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
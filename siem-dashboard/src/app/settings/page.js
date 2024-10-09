'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Switch } from "@/components/ui/switch"
import { settings } from '@/services/api'

export default function Settings() {
  const [emailNotifications, setEmailNotifications] = useState(true)
  const [dataRetentionDays, setDataRetentionDays] = useState(90)

  const saveSettings = async () => {
    try {
      await settings.update({
        email_notifications: emailNotifications,
        data_retention_days: dataRetentionDays,
      })
      alert('Settings saved successfully')
    } catch (error) {
      console.error('Failed to save settings:', error)
      alert('Failed to save settings')
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Settings</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <label htmlFor="emailNotifications" className="block mb-2">Email Notifications</label>
          <Switch
            id="emailNotifications"
            checked={emailNotifications}
            onCheckedChange={setEmailNotifications}
          />
        </div>
        <div className="mb-4">
          <label htmlFor="dataRetention" className="block mb-2">Data Retention (days)</label>
          <Input
            id="dataRetention"
            type="number"
            value={dataRetentionDays}
            onChange={(e) => setDataRetentionDays(e.target.value)}
            className="w-full"
          />
        </div>
        <Button onClick={saveSettings} className="bg-blue-500 text-white hover:bg-blue-600">Save Settings</Button>
      </CardContent>
    </Card>
  )
}
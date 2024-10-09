'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { isAuthenticated } from '@/services/auth'

export default function AuthCheck({ children }) {
  const router = useRouter()

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login')
    }
  }, [router])

  if (!isAuthenticated()) {
    return null // Or you could return a loading spinner here
  }

  return children
}
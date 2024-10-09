'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { isAuthenticated } from '@/services/auth'

export default function ProtectedRoute({ children }) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login')
    } else {
      setIsLoading(false)
    }
  }, [router])

  if (typeof window === 'undefined' || isLoading) {
    return <div>Loading...</div> // Or any loading indicator
  }

  return isAuthenticated() ? children : null
}
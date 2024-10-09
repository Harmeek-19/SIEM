'use client'
import { useRouter } from 'next/navigation'
import { logout } from '@/services/auth'
import { Button } from "@/components/ui/button"

export default function LogoutButton() {
  const router = useRouter()

  const handleLogout = async () => {
    try {
      await logout()
      router.push('/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return (
    <Button onClick={handleLogout}>Logout</Button>
  )
}
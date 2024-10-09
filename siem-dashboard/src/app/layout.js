'use client'

import { usePathname } from 'next/navigation'
import AuthCheck from '@/components/ui/AuthCheck'
import './globals.css'
import { Inter } from 'next/font/google'
import Link from 'next/link'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({ children }) {
  const pathname = usePathname()
  const isAuthPage = pathname === '/login' || pathname === '/signup'

  return (
    <html lang="en">
      <body className={inter.className}>
        {isAuthPage ? (
          children
        ) : (
          <AuthCheck>
            <div className="flex h-screen bg-gray-100">
              <Sidebar />
              <div className="flex-1 flex flex-col overflow-hidden">
                <Header />
                <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-200 p-6">
                  {children}
                </main>
              </div>
            </div>
          </AuthCheck>
        )}
      </body>
    </html>
  )
}


function Sidebar() {
  return (
    <aside className="bg-gray-800 text-white w-64 space-y-6 py-7 px-2 absolute inset-y-0 left-0 transform -translate-x-full md:relative md:translate-x-0 transition duration-200 ease-in-out">
      <nav>
        <Link href="/" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-gray-700">Dashboard</Link>
        <Link href="/events" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-gray-700">Security Events</Link>
        <Link href="/alerts" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-gray-700">Alerts</Link>
        <Link href="/intel" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-gray-700">Threat Intelligence</Link>
        <Link href="/anomalies" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-gray-700">Anomalies</Link>
        <Link href="/reports" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-gray-700">Reports</Link>
        <Link href="/settings" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-gray-700">Settings</Link>
      </nav>
    </aside>
  )
}

import { manualLogout } from '@/services/auth'

function Header() {
  return (
    <header className="bg-white shadow-md py-4 px-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-800">SOC Dashboard</h1>
        <button 
          onClick={manualLogout} 
          className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
        >
          Logout
        </button>
      </div>
    </header>
  )
}
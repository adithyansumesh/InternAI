"use client"

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export default function ProfilePage() {
  const router = useRouter()

  useEffect(() => {
    const userId = localStorage.getItem("user_id")
    if (!userId) {
      router.replace('/login')
    }
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem("user_id")
    router.replace('/login')
  }

  return (
    <div className="flex min-h-screen bg-slate-50 font-sans">
      {/* Fixed Sidebar */}
      <aside className="w-64 bg-slate-900 text-white flex-shrink-0 hidden md:flex flex-col shadow-xl z-10 sticky top-0 h-screen">
        <div className="p-4 border-b border-slate-800 flex items-center gap-3">
           <img src="/logo.png" alt="InternAI Logo" className="w-[50px] h-[50px] object-contain" />
           <span className="font-extrabold text-2xl tracking-tight text-white">InternAI</span>
        </div>
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
           <Link href="/dashboard" className="block px-4 py-3 rounded-md text-slate-300 hover:bg-slate-800 hover:text-white transition-colors">
             Application Hub
           </Link>
           <Link href="/internships" className="block px-4 py-3 rounded-md text-slate-300 hover:bg-slate-800 hover:text-white transition-colors">
             Internship Matches
           </Link>
           <Link href="/discovery" className="block px-4 py-3 rounded-md text-slate-300 hover:bg-slate-800 hover:text-white transition-colors">
             Internship Discovery
           </Link>
           <Link href="/profile" className="block px-4 py-3 rounded-md bg-primary text-primary-foreground font-semibold shadow-sm transition-all hover:brightness-110">
             Profile Settings
           </Link>
           <button onClick={handleLogout} className="w-full text-left block px-4 py-3 rounded-md text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-colors font-medium">
             Log Out
           </button>
        </nav>
      </aside>

      <main className="flex-1 p-4 md:p-8 lg:p-12 h-screen overflow-y-auto w-full relative">
        <header className="bg-slate-900 text-white p-4 md:hidden rounded-lg mb-6 flex items-center gap-3 shadow-lg">
          <img src="/logo.png" alt="InternAI Logo" className="w-[40px] h-[40px] object-contain" />
          <h1 className="font-extrabold text-xl tracking-tight">InternAI</h1>
        </header>

        <div className="max-w-7xl mx-auto space-y-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-200 pb-6">
            <div>
              <h2 className="text-3xl md:text-4xl font-extrabold tracking-tight text-slate-900">Profile View Placeholder</h2>
              <p className="text-slate-500 mt-2 text-lg">Manage your student details and preferences here.</p>
            </div>
            
            <Card>
              <CardHeader>
                <CardTitle>Personal Information</CardTitle>
                <CardDescription>Update your contact details and basic info.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name</Label>
                  <Input id="name" placeholder="John Doe" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input id="email" type="email" placeholder="john@example.com" />
                </div>
              </CardContent>
              <CardFooter className="flex justify-between items-center">
                <Button variant="destructive" onClick={handleLogout}>Log out</Button>
                <Button>Save Changes</Button>
              </CardFooter>
            </Card>

          </div>
        </div>
      </main>
    </div>
  )
}

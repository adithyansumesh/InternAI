"use client"

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'

export default function LandingPage() {
  const [isClient, setIsClient] = useState(false)
  
  useEffect(() => {
    setIsClient(true)
  }, [])

  return (
    <div className="flex flex-col min-h-screen font-sans bg-white selection:bg-primary/20">
      {/* Header */}
      <header className="px-6 py-4 flex items-center justify-between border-b border-slate-200 bg-white/80 backdrop-blur-md sticky top-0 z-50 transition-all">
        <div className="flex items-center gap-3 p-4">
          <img src="/logo.png" alt="InternAI Logo" className="w-[50px] h-[50px] object-contain" />
          <span className="font-extrabold text-2xl tracking-tight text-slate-900">InternAI</span>
        </div>
        <nav className="flex items-center gap-4">
          <Link href="/login?type=login">
            <Button variant="ghost" className="font-bold tracking-wide">Login</Button>
          </Link>
          <Link href="/login?type=register">
            <Button className="font-bold tracking-wide shadow-sm hover:shadow-md transition-shadow">Register</Button>
          </Link>
        </nav>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative w-full py-24 md:py-32 lg:py-40 bg-slate-900 text-center overflow-hidden">
          {/* Subtle background glow */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full max-w-5xl opacity-30 pointer-events-none bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/40 via-slate-900 to-slate-900"></div>
          
          <div className="container relative z-10 px-4 md:px-6 mx-auto space-y-8 max-w-4xl">
             <div className="inline-flex items-center justify-center px-4 py-1.5 rounded-full bg-white/10 border border-white/20 text-slate-200 text-sm font-medium tracking-wide shadow-sm backdrop-blur-md mb-6 hover:bg-white/20 transition-colors mx-auto">
               <svg className="w-3.5 h-3.5 mr-2 text-emerald-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
               Automation Enabled
             </div>
            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white leading-[1.1]">
              Automate Your <br className="hidden md:block"/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">Internship Hunt</span>
            </h1>
            <p className="text-xl md:text-2xl text-slate-300 max-w-2xl mx-auto font-medium leading-relaxed">
              Upload your resume and let our intelligent Multi-Agent AI discover roles, instantly generate tailored resumes, craft perfect cover letters, and securely draft outreach emails.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
              <Link href="/login">
                <Button size="lg" className="h-14 px-10 text-lg font-extrabold shadow-xl hover:scale-105 transition-all bg-white text-slate-900 hover:bg-slate-100 border-2 border-transparent hover:border-slate-200">
                  Get Started For Free
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-24 bg-slate-50 border-t border-slate-200">
          <div className="container px-4 md:px-6 mx-auto max-w-7xl">
            <div className="text-center mb-16 space-y-4">
              <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900">How InternAI Works</h2>
              <p className="text-xl text-slate-500 font-medium max-w-2xl mx-auto">Your complete end-to-end application orchestrator.</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12">
              {/* Feature 1 */}
              <div className="flex flex-col items-center text-center space-y-6 p-8 bg-white rounded-3xl shadow-sm border border-slate-100 hover:shadow-lg transition-shadow">
                <div className="p-5 bg-blue-50 rounded-2xl text-blue-600 shadow-inner border border-blue-100">
                  <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                </div>
                <h3 className="text-2xl font-bold text-slate-900 tracking-tight">1. Smart Analysis</h3>
                <p className="text-slate-600 font-medium leading-relaxed">Our NLP engine deeply parses your existing resume document to extract and precisely categorize your core technical competencies and experiences.</p>
              </div>

              {/* Feature 2 */}
              <div className="flex flex-col items-center text-center space-y-6 p-8 bg-white rounded-3xl shadow-sm border border-slate-100 hover:shadow-lg transition-shadow">
                <div className="p-5 bg-purple-50 rounded-2xl text-purple-600 shadow-inner border border-purple-100">
                  <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><path d="m11 8 3-3"/><path d="m11 14-3 3"/></svg>
                </div>
                <h3 className="text-2xl font-bold text-slate-900 tracking-tight">2. Precision Matching</h3>
                <p className="text-slate-600 font-medium leading-relaxed">The AI Discovery Agent scours available internships locally and scores your exact match percentage based on the job's strict requirements.</p>
              </div>

              {/* Feature 3 */}
              <div className="flex flex-col items-center text-center space-y-6 p-8 bg-white rounded-3xl shadow-sm border border-slate-100 hover:shadow-lg transition-shadow">
                <div className="p-5 bg-emerald-50 rounded-2xl text-emerald-600 shadow-inner border border-emerald-100">
                  <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
                </div>
                <h3 className="text-2xl font-bold text-slate-900 tracking-tight">3. Drafting & Outreach</h3>
                <p className="text-slate-600 font-medium leading-relaxed">We dynamically rewrite your resume, compose a pristine cover letter, and draft a personalized outreach email for each high-match role instantly.</p>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-12 text-center text-slate-500">
        <div className="flex items-center justify-center gap-3 p-4 mb-4">
           <img src="/logo.png" alt="InternAI Logo" className="w-[40px] h-[40px] object-contain" />
           <span className="font-bold text-xl text-slate-700 tracking-tight">InternAI</span>
        </div>
        {isClient && <p className="font-medium">&copy; {new Date().getFullYear()} InternAI Platform. All rights reserved.</p>}
      </footer>
    </div>
  )
}

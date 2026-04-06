"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { runWorkflow, ApplicationPackage, getAppliedInternships } from '../../lib/api'
import { getBestApplicationUrl } from '../../lib/internship-links'

export default function InternshipsPage() {
  const [preferredField, setPreferredField] = useState('')
  const [location, setLocation] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [result, setResult] = useState<ApplicationPackage | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [history, setHistory] = useState<any[]>([])
  const [isLoadingHistory, setIsLoadingHistory] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem("user_id")
    if (!token) {
      router.replace('/login')
    } else {
      getAppliedInternships()
        .then(data => setHistory(data))
        .catch(err => console.error("History fetch error:", err))
        .finally(() => setIsLoadingHistory(false))
    }
  }, [router])

  const handleSearch = async () => {
    // 1. Get the stored resume_id
    const resumeId = localStorage.getItem('internai_resume_id')
    
    if (!resumeId) {
      setError("No Resume Found. Please upload a resume in the Resume Generator tool first.")
      return
    }

    if (!preferredField) {
      setError("Please enter a preferred field (e.g., Software Engineering).")
      return
    }

    setIsSearching(true)
    setError(null)
    setResult(null)

    try {
      // 2. Trigger the multi-agent backend workflow
      const workflowData = await runWorkflow(resumeId, preferredField, location || "Remote")
      setResult(workflowData)
    } catch (err: any) {
      setError(err.message || "An error occurred while running the AI agents.")
    } finally {
      setIsSearching(false)
    }
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
           <Link href="/internships" className="block px-4 py-3 rounded-md bg-primary text-primary-foreground font-semibold shadow-sm transition-all hover:brightness-110">
             Internship Matches
           </Link>
           <Link href="/discovery" className="block px-4 py-3 rounded-md text-slate-300 hover:bg-slate-800 hover:text-white transition-colors">
             Internship Discovery
           </Link>
           <Link href="/profile" className="block px-4 py-3 rounded-md text-slate-300 hover:bg-slate-800 hover:text-white transition-colors">
             Profile Settings
           </Link>
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
              <h2 className="text-3xl md:text-4xl font-extrabold tracking-tight text-slate-900">AI Internship Discovery</h2>
              <p className="text-slate-500 mt-2 text-lg">Agents will find matching roles using your parsed resume.</p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-2 w-full md:w-auto">
                <Input 
                  placeholder="Preferred Role/Field..." 
                  value={preferredField}
                  onChange={(e) => setPreferredField(e.target.value)}
                  className="w-full sm:w-[200px]" 
                />
                <Input 
                  placeholder="Location (Optional)..." 
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full sm:w-[150px]" 
                />
                <Button onClick={handleSearch} disabled={isSearching}>
                   {isSearching ? "Agents Searching..." : "Run Discovery"}
                </Button>
            </div>
          </div>

          {error && <p className="text-sm text-destructive font-medium">{error}</p>}

          {/* Render the resulting Internship Matches */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
             {result ? (
               result.applications.filter(app => app.match_evaluation.match_score >= 6).length > 0 ? (
                 result.applications.filter(app => app.match_evaluation.match_score >= 6).map((app, i) => (
                  <Card key={i} className="flex flex-col h-full">
                    <CardHeader>
                      <div className="flex justify-between items-start gap-4">
                          <div>
                              <CardTitle className="text-lg">{app.internship.role}</CardTitle>
                              <CardDescription>{app.internship.company} • {app.internship.location}</CardDescription>
                          </div>
                          <div className="flex flex-col items-end">
                              <span className="text-2xl font-bold text-primary">{app.match_evaluation.match_score}/10</span>
                              <span className="text-xs text-muted-foreground uppercase tracking-wider">Match Score</span>
                          </div>
                      </div>
                    </CardHeader>
                    <CardContent className="flex-1 space-y-4">
                       <div className="space-y-1">
                         <h4 className="text-sm font-semibold">About the role</h4>
                         <p className="text-sm text-muted-foreground line-clamp-3">
                             {app.internship.description}
                         </p>
                       </div>
                       
                       <div className="space-y-1 border-t pt-4">
                         <h4 className="text-sm font-semibold">AI Match Recommendation</h4>
                         <p className="text-sm text-muted-foreground leading-relaxed">
                            {app.match_evaluation.recommendation}
                         </p>
                       </div>

                       {app.cover_letter && (
                         <div className="space-y-1 border-t pt-4">
                            <h4 className="text-sm font-semibold text-green-600">Generated Cover Letter</h4>
                            <p className="text-xs text-muted-foreground whitespace-pre-wrap leading-relaxed max-h-[150px] overflow-y-auto">
                               {app.cover_letter}
                            </p>
                         </div>
                       )}

                    </CardContent>
                    <CardFooter className="pt-4 border-t">
                       <Button 
                         variant="default" 
                         className="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold"
                         onClick={() => {
                            const resumeId = localStorage.getItem('internai_resume_id');
                            if (!resumeId) {
                                setError("Please upload your resume first!");
                                return;
                            }
                            window.open(getBestApplicationUrl(app.internship), '_blank', 'noopener,noreferrer');
                            localStorage.setItem("selected_internship", JSON.stringify({
                                resume_id: resumeId,
                                internship: app.internship,
                                match_score: app.match_evaluation.match_score,
                                reasoning: app.match_evaluation.reasoning
                            }));
                            router.push('/application/generate');
                         }}
                       >
                           Generate Application & Apply
                       </Button>
                    </CardFooter>
                  </Card>
                 ))
               ) : (
                 <div className="col-span-1 xl:col-span-2 flex flex-col items-center justify-center p-12 mt-12 text-center bg-muted/20 border-2 border-dashed rounded-xl">
                      <h3 className="text-lg font-semibold">No Strong Matches Found</h3>
                      <p className="text-sm text-muted-foreground mt-2 max-w-sm">
                         We couldn't find any internships with a match score of 6 or higher. Try adjusting your preferences or updating your resume.
                      </p>
                 </div>
               )
             ) : (
                /* Empty state / Generic placehoder when no active search */
                !isSearching && (
                  <div className="col-span-1 xl:col-span-2 flex flex-col items-center justify-center p-12 mt-12 text-center bg-muted/20 border-2 border-dashed rounded-xl">
                      <h3 className="text-lg font-semibold">Ready to discover internships</h3>
                      <p className="text-sm text-muted-foreground mt-2 max-w-sm">
                         Enter your preferred field above and our AI agents will scour the web, evaluate matches against your resume, and auto-generate tailored cover letters.
                      </p>
                  </div>
                )
             )}
          </div>

              <div className="mt-8 mb-6 border-b border-slate-200 pb-2 flex justify-between items-center">
                 <h2 className="text-2xl font-bold tracking-tight text-slate-900">Application History</h2>
                 <span className="bg-primary/10 text-primary px-3 py-1 rounded-full text-sm font-bold">{history.length} Total</span>
              </div>
              
              {isLoadingHistory ? (
                 <div className="flex justify-center p-8"><div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div></div>
              ) : history.length > 0 ? (
                 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {history.map((app, idx) => (
                       <Card key={idx} className="border-0 ring-1 ring-slate-200 shadow-sm hover:shadow-md transition-shadow">
                          <CardHeader className="bg-slate-50 border-b pb-4">
                             <CardTitle className="text-lg">{app.role}</CardTitle>
                             <CardDescription className="text-sm font-medium">{app.company}</CardDescription>
                          </CardHeader>
                          <CardContent className="pt-4 space-y-3">
                             <div className="flex justify-between items-center bg-slate-100 p-2 rounded">
                               <span className="text-xs text-slate-500 font-semibold uppercase">Match Score</span>
                               <span className="font-bold text-primary">{app.match_score}/10</span>
                             </div>
                             <div>
                               <p className="text-xs text-slate-500 font-semibold uppercase mb-1">AI Reasoning</p>
                               <p className="text-sm text-slate-700 line-clamp-3 leading-relaxed">{app.reasoning}</p>
                             </div>
                             <div className="text-xs text-slate-400 mt-2">
                                Applied: {new Date(app.created_at).toLocaleDateString()}
                             </div>
                          </CardContent>
                       </Card>
                    ))}
                 </div>
              ) : (
                 <div className="text-center p-8 bg-slate-50 rounded-lg border border-dashed border-slate-200">
                    <p className="text-slate-500">You haven't generated any applications yet. Run a discovery above!</p>
                 </div>
              )}

        </div>
      </main>
    </div>
  )
}

"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { CORE_API_BASE_URL, runWorkflow } from '../../lib/api'
import { getOriginalApplicationUrl, getSearchFirstApplicationUrl } from '../../lib/internship-links'

const STORAGE_KEYS = {
  resumeId: "internai_resume_id",
  results: "internai_dashboard_results",
  field: "internai_preferred_field",
  location: "internai_location",
  fileName: "internai_resume_file_name",
}

export default function DashboardPage() {
  const [file, setFile] = useState<File | null>(null)
  const [preferredField, setPreferredField] = useState("Software Engineering")
  const [location, setLocation] = useState("Remote")
  const [results, setResults] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sendingId, setSendingId] = useState<number | null>(null)
  const [savedResumeId, setSavedResumeId] = useState<string | null>(null)
  const [savedResumeName, setSavedResumeName] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    const userId = localStorage.getItem("user_id")
    if (!userId) {
      router.replace('/login')
      return
    }

    const storedResumeId = localStorage.getItem(STORAGE_KEYS.resumeId)
    const storedResults = localStorage.getItem(STORAGE_KEYS.results)
    const storedField = localStorage.getItem(STORAGE_KEYS.field)
    const storedLocation = localStorage.getItem(STORAGE_KEYS.location)
    const storedFileName = localStorage.getItem(STORAGE_KEYS.fileName)

    if (storedResumeId) setSavedResumeId(storedResumeId)
    if (storedFileName) setSavedResumeName(storedFileName)
    if (storedField) setPreferredField(storedField)
    if (storedLocation) setLocation(storedLocation)

    if (storedResults) {
      try {
        setResults(JSON.parse(storedResults))
      } catch {
        localStorage.removeItem(STORAGE_KEYS.results)
      }
    }
  }, [router])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0])
      setSavedResumeName(e.target.files[0].name)
    }
  }

  const persistDashboardState = (data: any, resumeId?: string, fileName?: string | null) => {
    localStorage.setItem(STORAGE_KEYS.results, JSON.stringify(data))
    localStorage.setItem(STORAGE_KEYS.field, preferredField)
    localStorage.setItem(STORAGE_KEYS.location, location)

    if (resumeId) {
      localStorage.setItem(STORAGE_KEYS.resumeId, resumeId)
      setSavedResumeId(resumeId)
    }

    if (fileName) {
      localStorage.setItem(STORAGE_KEYS.fileName, fileName)
      setSavedResumeName(fileName)
    }
  }

  const clearSavedResume = () => {
    setFile(null)
    setResults(null)
    setSavedResumeId(null)
    setSavedResumeName(null)
    setError(null)
    localStorage.removeItem(STORAGE_KEYS.resumeId)
    localStorage.removeItem(STORAGE_KEYS.results)
    localStorage.removeItem(STORAGE_KEYS.fileName)
  }

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    setResults(null)

    const userId = typeof window !== 'undefined' ? localStorage.getItem("user_id") : null

    if (!userId) {
      setError("Please login first to use the AI Application Engine.")
      setIsLoading(false)
      return
    }

    try {
      if (file) {
        const formData = new FormData()
        formData.append("file", file)
        formData.append("preferred_field", preferredField)
        formData.append("location", location)

        const response = await fetch(`${CORE_API_BASE_URL}/analyze`, {
          method: "POST",
          headers: {
            ...(userId ? { "Authorization": `Bearer ${userId}` } : {})
          },
          body: formData,
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || "Analysis failed.")
        }

        const data = await response.json()
        setResults(data)
        persistDashboardState(data, data.resume_id, file.name)
        return
      }

      if (!savedResumeId) {
        throw new Error("Please upload a resume PDF once. After that, you can reuse it without uploading again.")
      }

      const data = await runWorkflow(savedResumeId, preferredField, location)
      setResults(data)
      persistDashboardState(data, savedResumeId, savedResumeName)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleApply = (app: any, resumeId: string) => {
    if (typeof window !== 'undefined') {
      window.open(getSearchFirstApplicationUrl(app.internship), '_blank', 'noopener,noreferrer');
      localStorage.setItem("selected_internship", JSON.stringify({
        internship: app.internship,
        match_score: app.match_evaluation.match_score,
        reasoning: app.match_evaluation.reasoning,
        resume_id: resumeId
      }))
      router.push('/application/generate')
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
           <Link href="/dashboard" className="block px-4 py-3 rounded-md bg-primary text-primary-foreground font-semibold shadow-sm transition-all hover:brightness-110">
             Application Hub
           </Link>
           <Link href="/internships" className="block px-4 py-3 rounded-md text-slate-300 hover:bg-slate-800 hover:text-white transition-colors">
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

      {/* Main Content - Takes remaining space */}
      <main className="flex-1 p-4 md:p-8 lg:p-12 h-screen overflow-y-auto w-full relative">
        {/* Mobile Header */}
        <header className="bg-slate-900 text-white p-4 md:hidden rounded-lg mb-6 flex items-center gap-3 shadow-lg">
          <img src="/logo.png" alt="InternAI Logo" className="w-[40px] h-[40px] object-contain" />
          <h1 className="font-extrabold text-xl tracking-tight">InternAI</h1>
        </header>

        <div className="max-w-7xl mx-auto space-y-8">
          <div className="border-b border-slate-200 pb-6">
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-slate-900">Application Hub</h1>
            <p className="text-slate-500 mt-2 text-lg">Upload your resume to discover internships and auto-generate beautifully tailored application materials.</p>
          </div>
          
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
            
            {/* Left Column: Upload Form */}
            <div className="xl:col-span-1 space-y-6">
              <Card className="shadow-lg border-0 ring-1 ring-slate-200 sticky top-12">
                <CardHeader className="bg-slate-100/50 border-b pb-4">
                  <CardTitle className="text-xl">AI Application Engine</CardTitle>
                </CardHeader>
                <CardContent className="pt-6">
                  <form onSubmit={handleAnalyze} className="space-y-5">
                    <div className="space-y-2">
                      <Label htmlFor="resume" className="font-semibold text-slate-700">Resume Document (PDF)</Label>
                      <Input id="resume" type="file" accept=".pdf" onChange={handleFileChange} className="cursor-pointer file:text-primary file:font-semibold bg-white" />
                      {savedResumeId && (
                        <div className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
                          Using saved resume session{savedResumeName ? `: ${savedResumeName}` : ""}. You only need to upload again if you want to replace it.
                        </div>
                      )}
                    </div>
                    
                    <div className="space-y-2 pt-2">
                      <Label htmlFor="field" className="font-semibold text-slate-700">Preferred Field</Label>
                      <Input 
                        id="field" 
                        type="text" 
                        value={preferredField}
                        onChange={(e) => setPreferredField(e.target.value)}
                        placeholder="e.g. Machine Learning"
                        className="bg-white"
                      />
                    </div>

                    <div className="space-y-2 pt-2">
                      <Label htmlFor="location" className="font-semibold text-slate-700">Location Match</Label>
                      <Input 
                        id="location" 
                        type="text" 
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                        placeholder="e.g. Remote, New York, CA"
                        className="bg-white"
                      />
                    </div>

                    {error && <div className="text-sm text-red-600 bg-red-50 border border-red-200 p-3 rounded-md font-medium mt-4">{error}</div>}

                    <div className="pt-4 space-y-3">
                      <Button type="submit" className="w-full py-6 text-md font-bold transition-all shadow-md hover:shadow-xl" disabled={isLoading || (!file && !savedResumeId)}>
                        {isLoading ? "Running Pipeline..." : file ? "Analyze & Draft Apps" : "Reuse Saved Resume"}
                      </Button>
                      {savedResumeId && (
                        <Button type="button" variant="outline" className="w-full" onClick={clearSavedResume}>
                          Replace Saved Resume
                        </Button>
                      )}
                    </div>
                  </form>
                </CardContent>
              </Card>
            </div>

            {/* Right Column: Results Display */}
            <div className="xl:col-span-2 space-y-6">
              {!results && !isLoading && (
                <div className="h-full min-h-[500px] flex flex-col items-center justify-center border-2 border-dashed border-slate-300 rounded-2xl bg-white shadow-sm p-8 text-center transition-all hover:bg-slate-50">
                  <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" className="text-slate-300 mb-6"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/></svg>
                  <h3 className="text-xl font-bold text-slate-700 mb-2">Ready for Discovery</h3>
                  <p className="text-slate-500 max-w-sm">Upload your resume and click Analyze to let our AI automation orchestrator craft your next application.</p>
                </div>
              )}

              {isLoading && (
                <div className="h-full min-h-[500px] flex flex-col items-center justify-center border rounded-2xl bg-white shadow-sm p-8 text-center">
                   <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mb-6"></div>
                   <h3 className="text-xl font-bold text-slate-800 mb-2">Running Stage 1: Intelligence Discovery</h3>
                   <p className="text-primary font-medium animate-pulse">Parsing ➔ Identifying Skills ➔ Finding Internships...</p>
                </div>
              )}

              {results && (
                <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                  {/* Skills Section */}
                  <Card className="shadow-md border-0 ring-1 ring-slate-200">
                    <CardHeader className="bg-slate-50 border-b pb-4 rounded-t-lg">
                      <CardTitle>Profile Extraction</CardTitle>
                      <CardDescription>AI Categorized Core Competencies</CardDescription>
                    </CardHeader>
                    <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
                      <div className="space-y-3">
                        <Label className="font-bold text-slate-800 flex items-center gap-2">
                           <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                           Programming
                        </Label>
                        <div className="flex flex-wrap gap-2">
                          {results.categorized_skills?.programming_languages?.map((skill: string, i: number) => (
                            <span key={i} className="px-3 py-1 bg-blue-50 text-blue-700 border border-blue-200 text-xs font-semibold rounded-md shadow-sm">{skill}</span>
                          ))}
                        </div>
                      </div>
                      <div className="space-y-3">
                        <Label className="font-bold text-slate-800 flex items-center gap-2">
                           <span className="w-2 h-2 rounded-full bg-purple-500"></span>
                           AI / ML
                        </Label>
                        <div className="flex flex-wrap gap-2">
                          {results.categorized_skills?.ai_ml_skills?.map((skill: string, i: number) => (
                            <span key={i} className="px-3 py-1 bg-purple-50 text-purple-700 border border-purple-200 text-xs font-semibold rounded-md shadow-sm">{skill}</span>
                          ))}
                        </div>
                      </div>
                      <div className="space-y-3">
                        <Label className="font-bold text-slate-800 flex items-center gap-2">
                           <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                           Tools & Frameworks
                        </Label>
                        <div className="flex flex-wrap gap-2">
                          {results.categorized_skills?.tools_frameworks?.map((skill: string, i: number) => (
                            <span key={i} className="px-3 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold rounded-md shadow-sm">{skill}</span>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Internship Applications Section */}
                  <div className="flex items-center justify-between mt-10 mb-6">
                     <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">Crafted Applications</h2>
                     <span className="px-3 py-1 bg-primary/10 font-bold text-primary rounded-full text-sm">{results.applications?.length || 0} Matches</span>
                  </div>
                  
                  <div className="space-y-8">
                    {results.applications?.map((app: any, idx: number) => (
                      <Card key={idx} className="border-0 ring-1 ring-slate-200 shadow-xl overflow-hidden rounded-xl">
                        <div className="bg-slate-900 p-6 flex flex-col md:flex-row justify-between items-start md:items-center text-white">
                          <div className="mb-4 md:mb-0">
                            <h3 className="text-2xl font-bold tracking-tight mb-1">{app.internship.role}</h3>
                            <p className="text-slate-300 font-medium flex items-center gap-2">
                               <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
                               {app.internship.company} <span className="opacity-50 mx-1">•</span>
                               <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                               {app.internship.location}
                            </p>
                          </div>
                          <div className="flex flex-col items-end bg-black/30 px-4 py-2 rounded-lg border border-white/10">
                            <span className="text-3xl font-extrabold text-white">{app.match_evaluation.match_score}<span className="text-lg opacity-70">/10</span></span>
                            <span className="text-xs font-bold uppercase tracking-wider text-slate-300 mt-1">Match Score</span>
                          </div>
                        </div>
                        
                        <CardContent className="p-0">
                          <div className="p-6 border-b border-slate-100 bg-slate-50/50">
                            <p className="text-sm font-bold tracking-tight text-slate-800 mb-2 uppercase">AI Selection Reasoning</p>
                            <p className="text-base text-slate-600 leading-relaxed border-l-4 border-slate-300 pl-4 py-1">{app.match_evaluation.reasoning}</p>
                          </div>
                          
                          <div className="p-6 bg-slate-50 border-t border-slate-100 flex justify-between items-center rounded-b-xl mt-4">
                                <div className="text-sm text-slate-500 font-medium">
                                    Ready to generate tailored application documents?
                                </div>
                                <Button 
                                    onClick={() => handleApply(app, results.resume_id)}
                                    className="px-8 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold shadow-md rounded-md"
                                >
                                    Apply Now 👉
                                </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>

                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { searchInternships } from '../../lib/api'

export default function DiscoveryPage() {
  const [preferredField, setPreferredField] = useState('')
  const [location, setLocation] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [results, setResults] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem("user_id")
    if (!token) {
      router.replace('/login')
    }
  }, [router])

  const handleSearch = async (e?: React.FormEvent, directField?: string, directLoc?: string) => {
    if (e) e.preventDefault()

    const searchField = directField !== undefined ? directField : preferredField;
    const searchLoc = directLoc !== undefined ? directLoc : location;

    if (!searchField) {
      setError("Please enter a preferred field (e.g., Software Engineering).")
      return
    }

    setIsSearching(true)
    setError(null)
    setResults([])

    // Update state to match clicked quick links
    if (directField !== undefined) setPreferredField(directField);
    if (directLoc !== undefined) setLocation(directLoc);

    try {
      // Trigger the manual search backend workflow
      const data = await searchInternships(searchField, searchLoc || "Remote")
      setResults(data)
    } catch (err: any) {
      setError(err.message || "An error occurred while running the search.")
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
           <Link href="/internships" className="block px-4 py-3 rounded-md text-slate-300 hover:bg-slate-800 hover:text-white transition-colors">
             Internship Matches
           </Link>
           <Link href="/discovery" className="block px-4 py-3 rounded-md bg-primary text-primary-foreground font-semibold shadow-sm transition-all hover:brightness-110">
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
          <div className="border-b border-slate-200 pb-6">
              <h2 className="text-3xl md:text-4xl font-extrabold tracking-tight text-slate-900">Manual Internship Discovery</h2>
              <p className="text-slate-500 mt-2 text-lg">Search and scrape up-to-date internship listings instantly from Google.</p>
          </div>

          {/* Quick Links Mega Menu section */}
          <Card className="shadow-sm border-0 ring-1 ring-slate-200 bg-white">
            <CardContent className="p-6 md:p-8">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Popular Categories */}
                <div className="space-y-4">
                  <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2 border-b border-slate-100 pb-2">
                    Popular categories
                  </h3>
                  <ul className="space-y-3">
                    {["IT jobs", "Sales jobs", "Marketing jobs", "Data Science jobs", "HR jobs", "Engineering jobs"].map((job) => (
                      <li key={job}>
                        <button onClick={() => handleSearch(undefined, job, "Remote")} className="text-slate-600 hover:text-primary hover:translate-x-1 transition-all text-sm font-medium text-left">
                          {job}
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Jobs in Demand */}
                <div className="space-y-4 md:border-l md:border-slate-100 md:pl-8">
                  <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2 border-b border-slate-100 pb-2">
                    Jobs in demand
                  </h3>
                  <ul className="space-y-3">
                    {["Fresher jobs", "MNC jobs", "Remote jobs", "Work from home jobs", "Walk-in jobs", "Part-time jobs"].map((job) => (
                      <li key={job}>
                        <button onClick={() => handleSearch(undefined, job, "Remote")} className="text-slate-600 hover:text-primary hover:translate-x-1 transition-all text-sm font-medium text-left">
                          {job}
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Jobs by Location */}
                <div className="space-y-4 md:border-l md:border-slate-100 md:pl-8">
                  <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2 border-b border-slate-100 pb-2">
                    Jobs by location
                  </h3>
                  <ul className="space-y-3">
                    {["Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai", "Pune"].map((loc) => (
                      <li key={loc}>
                        <button onClick={() => handleSearch(undefined, "Any Field", loc)} className="text-slate-600 hover:text-primary hover:translate-x-1 transition-all text-sm font-medium text-left">
                          Jobs in {loc}
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-lg border-0 ring-1 ring-slate-200">
             <CardHeader className="bg-slate-100/50 border-b pb-4">
               <CardTitle className="text-xl">Search Parameters</CardTitle>
             </CardHeader>
             <CardContent className="pt-6">
               <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
                 <div className="space-y-2 flex-1">
                   <Label htmlFor="field" className="font-semibold text-slate-700">Role / Keyword</Label>
                   <Input 
                     id="field" 
                     type="text" 
                     value={preferredField}
                     onChange={(e) => setPreferredField(e.target.value)}
                     placeholder="e.g. Data Analyst"
                     className="bg-white"
                   />
                 </div>

                 <div className="space-y-2 flex-1">
                   <Label htmlFor="location" className="font-semibold text-slate-700">Location</Label>
                   <Input 
                     id="location" 
                     type="text" 
                     value={location}
                     onChange={(e) => setLocation(e.target.value)}
                     placeholder="e.g. Remote, San Francisco"
                     className="bg-white"
                   />
                 </div>
                 
                 <div className="flex items-end">
                    <Button type="submit" disabled={isSearching} className="w-full md:w-auto py-5 px-8 font-bold shadow-md">
                        {isSearching ? "Scraping Jobs..." : "Search"}
                    </Button>
                 </div>
               </form>
               {error && <p className="text-sm text-destructive font-medium mt-4">{error}</p>}
             </CardContent>
          </Card>

          {/* Render the resulting Internship Matches */}
          {results.length > 0 && (
             <div className="mt-8 mb-4">
                <h3 className="text-2xl font-bold tracking-tight text-slate-900 mb-6">Discovery Results</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                 {results.map((internship, i) => (
                    <Card key={i} className="flex flex-col h-full shadow-md border-0 ring-1 ring-slate-200">
                      <CardHeader className="bg-slate-50 border-b">
                        <CardTitle className="text-lg">{internship.role}</CardTitle>
                        <CardDescription className="text-sm font-medium text-slate-600">{internship.company} • {internship.location}</CardDescription>
                      </CardHeader>
                      <CardContent className="flex-1 pt-4">
                         <div className="space-y-1">
                           <h4 className="text-sm font-semibold text-slate-800">Job Description Snippet</h4>
                           <p className="text-sm text-muted-foreground line-clamp-4 leading-relaxed">
                               {internship.description}
                           </p>
                         </div>
                      </CardContent>
                      <CardFooter className="pt-4 border-t bg-slate-50/50">
                         {internship.application_link ? (
                             <Button 
                               asChild
                               variant="default" 
                               className="w-full font-bold"
                             >
                                 <a href={internship.application_link} target="_blank" rel="noopener noreferrer">View Original Post</a>
                             </Button>
                         ) : (
                             <Button disabled variant="outline" className="w-full">
                               Link Unavailable
                             </Button>
                         )}
                      </CardFooter>
                    </Card>
                 ))}
                </div>
             </div>
          )}
          
          {!isSearching && results.length === 0 && (
              <div className="col-span-1 xl:col-span-2 flex flex-col items-center justify-center p-12 mt-12 text-center bg-muted/20 border-2 border-dashed rounded-xl">
                  <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" className="text-slate-300 mb-6"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                  <h3 className="text-lg font-semibold text-slate-700">Search for New Internships</h3>
                  <p className="text-sm text-muted-foreground mt-2 max-w-sm">
                     Use the search form above to directly scrape Google for the latest internship listings matching your criteria.
                  </p>
              </div>
          )}

          {isSearching && (
             <div className="flex justify-center p-16">
                 <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
             </div>
          )}

        </div>
      </main>
    </div>
  )
}

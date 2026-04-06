"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { API_BASE_URL } from "../../lib/api"

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLogin, setIsLogin] = useState(false) // Default to Sign Up when clicking "Get Started"
  const [name, setName] = useState("") // Only for signup
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      if (params.get("type") === "login") {
        setIsLogin(true);
      }
    }
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      const endpoint = isLogin ? "/auth/login" : "/auth/signup"
      const payload = isLogin 
        ? { email, password } 
        : { name, email, password }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || "Authentication failed")
      }

      if (isLogin) {
        // Save simple session data
        localStorage.setItem("user_id", data.user_id)
        
        // Redirect to dashboard
        router.push("/dashboard")
      } else {
        // Successful signup, switch to login view
        setIsLogin(true)
        setError("Account created successfully! Please log in.")
      }

    } catch (err: any) {
        setError(err.message)
    } finally {
        setIsLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-muted/40 p-4">
      <Card className="w-full max-w-md shadow-xl border-t-4 border-t-primary">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center p-4 mb-2">
            <img src="/logo.png" alt="InternAI Logo" className="w-[150px] h-auto object-contain" />
          </div>
          <CardTitle className="text-2xl font-extrabold tracking-tight text-slate-900">InternAI Platform</CardTitle>
          <CardDescription className="text-base text-slate-500 mt-2">
            {isLogin ? "Welcome back! Sign in to continue." : "Create your account to automate your internship applications."}
          </CardDescription>

          <div className="flex bg-slate-100 p-1 rounded-lg mt-6 mb-2 mx-auto w-full max-w-sm">
             <button type="button" onClick={() => {setIsLogin(false); setError(null)}} className={`flex-1 py-2 text-sm font-semibold rounded-md transition-all ${!isLogin ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}>Sign Up</button>
             <button type="button" onClick={() => {setIsLogin(true); setError(null)}} className={`flex-1 py-2 text-sm font-semibold rounded-md transition-all ${isLogin ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}>Sign In</button>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            
            {!isLogin && (
               <div className="space-y-2">
                 <Label htmlFor="name">Full Name</Label>
                 <Input 
                   id="name" 
                   placeholder="Jane Doe" 
                   required={!isLogin} 
                   value={name}
                   onChange={(e) => setName(e.target.value)}
                 />
               </div>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="email">Email address</Label>
              <Input 
                id="email" 
                type="email" 
                placeholder="student@example.com" 
                required 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                 <Label htmlFor="password">Password</Label>
                 {isLogin && <a href="#" className="text-xs text-primary hover:underline">Forgot password?</a>}
              </div>
              <Input 
                id="password" 
                type="password" 
                required 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            {error && (
               <div className={`p-3 text-sm rounded-md ${error.includes('successfully') ? 'bg-green-100 text-green-800' : 'bg-destructive/15 text-destructive font-medium'}`}>
                  {error}
               </div>
            )}

            <Button type="submit" className="w-full h-11 text-md font-bold" disabled={isLoading}>
               {isLoading ? "Please wait..." : (isLogin ? "Sign In Securely" : "Create Account")}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

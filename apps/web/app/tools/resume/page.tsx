"use client"

import { useState } from 'react'
import { AppSidebar } from '@/components/app-sidebar'
import { SiteHeader } from '@/components/site-header'
import {
  SidebarInset,
  SidebarProvider,
} from '@/components/ui/sidebar'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { uploadResume, ParsedResumeResponse } from '../../../lib/api'

export default function ResumeGeneratorPage() {
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [result, setResult] = useState<ParsedResumeResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0])
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first.")
      return
    }

    setIsUploading(true)
    setError(null)
    setResult(null)

    try {
      const parsedData = await uploadResume(file)
      setResult(parsedData)
      // Store the resume_id in localStorage so other pages can use it for workflows
      localStorage.setItem('intelai_resume_id', parsedData.resume_id)
    } catch (err: any) {
      setError(err.message || "An error occurred during upload.")
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <SidebarProvider>
      <AppSidebar variant="inset" />
      <SidebarInset>
        <SiteHeader />
        <div className="flex flex-1 flex-col p-4 lg:p-6">
          <div className="max-w-4xl w-full mx-auto space-y-6">
            <div>
              <h2 className="text-2xl font-bold tracking-tight">Resume Upload & Parsing</h2>
              <p className="text-muted-foreground">Upload your resume PDF to extract skills and prepare for AI matching.</p>
            </div>
            
            <Card>
              <CardHeader>
                <CardTitle>Resume Upload</CardTitle>
                <CardDescription>Select a PDF file to begin the parsing process.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="resume_file">Resume File (PDF)</Label>
                  <Input 
                    id="resume_file" 
                    type="file" 
                    accept=".pdf"
                    onChange={handleFileChange}
                    disabled={isUploading}
                  />
                </div>
                {error && <p className="text-sm text-destructive font-medium">{error}</p>}
                {result && (
                  <p className="text-sm text-green-600 font-medium">
                    Upload successful! Resume ID: {result.resume_id}
                  </p>
                )}
              </CardContent>
              <CardFooter className="flex justify-end">
                <Button onClick={handleUpload} disabled={isUploading || !file}>
                  {isUploading ? "Uploading & Parsing..." : "Upload Resume"}
                </Button>
              </CardFooter>
            </Card>

            {/* Generated output visualization */}
            {result && (
              <Card className="border-dashed bg-muted/20">
                <CardHeader>
                   <CardTitle>Extracted Data Pipeline</CardTitle>
                   <CardDescription>This is the raw data captured by the resume OCR service.</CardDescription>
                </CardHeader>
                 <CardContent>
                     <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-xs">
                        {JSON.stringify(result.parsed_data, null, 2)}
                     </pre>
                 </CardContent>
              </Card>
            )}

            {!result && (
               <Card className="border-dashed bg-muted/20">
                 <CardContent className="flex items-center justify-center min-h-[150px]">
                     <p className="text-muted-foreground text-sm">Waiting for resume upload...</p>
                 </CardContent>
               </Card>
            )}

          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

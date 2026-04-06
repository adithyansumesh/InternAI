import { AppSidebar } from '@/components/app-sidebar'
import { SiteHeader } from '@/components/site-header'
import {
  SidebarInset,
  SidebarProvider,
} from '@/components/ui/sidebar'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'

export default function EmailGeneratorPage() {
  return (
    <SidebarProvider>
      <AppSidebar variant="inset" />
      <SidebarInset>
        <SiteHeader />
        <div className="flex flex-1 flex-col p-4 lg:p-6">
          <div className="max-w-4xl w-full mx-auto space-y-6">
            <div>
              <h2 className="text-2xl font-bold tracking-tight">AI Cover Letter / Email Generator</h2>
              <p className="text-muted-foreground">Draft cold emails or cover letters tailored to a specific internship.</p>
            </div>
            
            <Card>
              <CardHeader>
                <CardTitle>Job Description Context</CardTitle>
                <CardDescription>Provide details about the role you are applying to.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="company">Target Company</Label>
                  <Input id="company" placeholder="e.g. Acme Corp" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="jd">Job Description</Label>
                  <Textarea id="jd" placeholder="Paste the job description here..." className="min-h-[150px]" />
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button variant="outline">Clear</Button>
                <Button>Generate Draft</Button>
              </CardFooter>
            </Card>

            {/* Placeholder for generated output */}
            <Card className="border-dashed bg-muted/20">
               <CardContent className="flex items-center justify-center min-h-[300px]">
                   <p className="text-muted-foreground">Generated Email/Letter will appear here...</p>
               </CardContent>
            </Card>

          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

"use client"

import GanttChart from "@/components/GanttChart"

export default function GanttPage() {
  return (
    <main className="min-h-screen bg-white py-20 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
          <GanttChart />
        </div>
      </div>
    </main>
  )
}

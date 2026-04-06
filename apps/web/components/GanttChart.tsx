"use client"

import React from "react"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList,
  ReferenceArea,
} from "recharts"

const data = [
  {
    name: "Project Proposal Approval",
    start: new Date(2025, 10, 30).getTime(),
    end: new Date(2025, 11, 14).getTime(),
    color: "#5b69f6",
  },
  {
    name: "Methodology & Research",
    start: new Date(2025, 11, 14).getTime(),
    end: new Date(2026, 0, 15).getTime(),
    color: "#ef5350",
  },
  {
    name: "System Design & Architecture",
    start: new Date(2026, 0, 1).getTime(),
    end: new Date(2026, 0, 25).getTime(),
    color: "#26c6da",
  },
  {
    name: "Implementation (Input & Idea Modules)",
    start: new Date(2026, 0, 20).getTime(),
    end: new Date(2026, 1, 10).getTime(),
    color: "#ab47bc",
  },
  {
    name: "Implementation (Analysis & UI Modules)",
    start: new Date(2026, 1, 10).getTime(),
    end: new Date(2026, 1, 25).getTime(),
    color: "#ffa726",
  },
  {
    name: "Testing & Debugging",
    start: new Date(2026, 1, 26).getTime(),
    end: new Date(2026, 2, 5).getTime(),
    color: "#29b6f6",
  },
  {
    name: "Report Writing & Diagrams",
    start: new Date(2026, 0, 15).getTime(),
    end: new Date(2026, 2, 10).getTime(),
    color: "#f06292",
  },
  {
    name: "Final Review & Submission",
    start: new Date(2026, 2, 11).getTime(),
    end: new Date(2026, 2, 22).getTime(),
    color: "#9ccc65",
  },
]

// Formatting the data for Recharts stacked bar chart to simulate Gantt
// We use a transparent bar for the "pre-start" duration
const chartData = data.map((item) => ({
  name: item.name,
  startOffset: item.start,
  duration: item.end - item.start,
  color: item.color,
  fullName: item.name,
}))

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload
    return (
      <div className="bg-white p-3 border border-gray-200 shadow-lg rounded-md text-sm">
        <p className="font-bold text-gray-800">{data.fullName}</p>
        <p className="text-gray-600">
          Start: {new Date(data.startOffset).toLocaleDateString()}
        </p>
        <p className="text-gray-600">
          End: {new Date(data.startOffset + data.duration).toLocaleDateString()}
        </p>
      </div>
    )
  }
  return null
}

const GanttChart = () => {
  const minDate = new Date(2025, 10, 30).getTime()
  const maxDate = new Date(2026, 2, 30).getTime()

  const formatXAxis = (tickItem: number) => {
    const date = new Date(tickItem)
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    const day = date.getDate()
    const month = months[date.getMonth()]
    const year = date.getFullYear()

    // Show year for the first tick and the first tick of the new year
    if (day === 30 && date.getMonth() === 10) return `${month} ${day} ${year}`
    if (day === 11 && date.getMonth() === 0) return `${month} ${day} ${year}`
    
    return `${month} ${day}`
  }

  return (
    <div className="w-full bg-white flex flex-col items-center py-12 px-4">
      <div className="w-full max-w-6xl">
        <div className="mb-16 text-center">
          <h1 className="text-4xl font-serif font-bold tracking-[0.2em] text-black mb-16 uppercase">
            GANTT CHART
          </h1>
          
          <div className="relative inline-block w-full">
            <p className="text-gray-500 text-sm font-medium mb-4">
              LaunchCraft Project Timeline (Dec 2025 - Mar 2026)
            </p>
            
            <div className="flex gap-1 justify-center mb-10">
              {["1w", "1m", "6m", "YTD", "1y", "all"].map((range) => (
                <button
                  key={range}
                  className={`px-3 py-1 text-xs font-semibold rounded ${
                    range === "all" ? "bg-gray-300 text-gray-700" : "bg-gray-100 text-gray-500"
                  } hover:bg-gray-200 transition-colors cursor-pointer`}
                >
                  {range}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="relative w-full h-[550px]" style={{ paddingLeft: '40px', paddingRight: '40px' }}>
          {/* Y Axis Label "Tasks" rotated */}
          <div className="absolute -left-12 top-1/2 -translate-y-1/2 -rotate-90 text-gray-400 font-medium text-sm tracking-widest hidden md:block">
            Tasks
          </div>

          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              layout="vertical"
              data={chartData}
              margin={{ top: 10, right: 30, left: 220, bottom: 40 }}
              barGap={0}
            >
              <CartesianGrid strokeDasharray="0" horizontal={false} vertical stroke="#f1f1f1" strokeWidth={1} />
              <XAxis
                type="number"
                domain={[minDate, maxDate]}
                ticks={[
                  new Date(2025, 10, 30).getTime(),
                  new Date(2025, 11, 14).getTime(),
                  new Date(2025, 11, 28).getTime(),
                  new Date(2026, 0, 11).getTime(),
                  new Date(2026, 0, 25).getTime(),
                  new Date(2026, 1, 8).getTime(),
                  new Date(2026, 1, 22).getTime(),
                  new Date(2026, 2, 8).getTime(),
                  new Date(2026, 2, 22).getTime(),
                ]}
                axisLine={false}
                tickLine={false}
                tickFormatter={formatXAxis}
                orientation="bottom"
                style={{ fontSize: "12px", fill: "#a1a1aa", fontWeight: 400 }}
                dy={20}
              />
              <YAxis
                type="category"
                dataKey="name"
                axisLine={false}
                tickLine={false}
                style={{ fontSize: "14px", fill: "#71717a", fontWeight: 400 }}
                width={220}
                dx={-10}
              />
              <Tooltip 
                content={<CustomTooltip />} 
                cursor={{ fill: "transparent" }}
                animationDuration={200}
              />
              
              <Bar dataKey="startOffset" stackId="a" fill="transparent" />
              <Bar dataKey="duration" stackId="a" barSize={14} radius={[2, 2, 2, 2]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          
          {/* X Axis Label "Timeline (Months)" */}
          <div className="absolute left-1/2 -translate-x-1/2 bottom-0 text-gray-500 text-sm font-medium mt-12 pt-10">
            Timeline (Months)
          </div>
        </div>
      </div>
    </div>
  )
}

export default GanttChart

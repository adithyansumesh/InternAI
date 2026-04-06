"use client"

import * as React from "react"
import { Area, AreaChart, CartesianGrid, XAxis } from "recharts"

import { useIsMobile } from '@/hooks/use-mobile'
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from '@/components/ui/chart'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  ToggleGroup,
  ToggleGroupItem,
} from '@/components/ui/toggle-group'

export interface ChartAreaProps {
  title?: string
  description?: string
  data?: any[]
  xAxisKey?: string
  series?: {
    key: string
    color: string
    label: string
  }[]
}

const defaultData = [
  { date: "2024-06-01", value1: 178, value2: 200 },
  { date: "2024-06-02", value1: 470, value2: 410 },
  { date: "2024-06-03", value1: 103, value2: 160 },
  { date: "2024-06-04", value1: 439, value2: 380 },
  { date: "2024-06-05", value1: 88, value2: 140 },
  { date: "2024-06-06", value1: 294, value2: 250 },
  { date: "2024-06-07", value1: 323, value2: 370 },
  { date: "2024-06-08", value1: 385, value2: 320 },
  { date: "2024-06-09", value1: 438, value2: 480 },
  { date: "2024-06-10", value1: 155, value2: 200 },
]

export function ChartAreaInteractive({
  title = "Interactive Chart",
  description = "Displaying data trends over time",
  data = defaultData,
  xAxisKey = "date",
  series = [
    { key: "value1", color: "var(--primary)", label: "Metric 1" },
    { key: "value2", color: "hsl(var(--muted-foreground))", label: "Metric 2" }
  ]
}: ChartAreaProps) {
  const isMobile = useIsMobile()
  const [timeRange, setTimeRange] = React.useState("90d")

  React.useEffect(() => {
    if (isMobile) {
      setTimeRange("7d")
    }
  }, [isMobile])

  // Optional: Add filtering logic here based on timeRange if using real dates.
  // For the generic component, we'll just display the provided data.
  const filteredData = data; 

  // Dynamically build chart config based on series prop
  const dynamicConfig = series.reduce((acc, s) => {
    acc[s.key] = { label: s.label, color: s.color }
    return acc
  }, {} as ChartConfig)

  return (
    <Card className="@container/card">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>
          <span className="hidden @[540px]/card:block">
            {description}
          </span>
          <span className="@[540px]/card:hidden">Trend</span>
        </CardDescription>
        <CardAction>
          <ToggleGroup
            type="single"
            value={timeRange}
            onValueChange={setTimeRange}
            variant="outline"
            className="hidden *:data-[slot=toggle-group-item]:!px-4 @[767px]/card:flex"
          >
            <ToggleGroupItem value="90d">90 Days</ToggleGroupItem>
            <ToggleGroupItem value="30d">30 Days</ToggleGroupItem>
            <ToggleGroupItem value="7d">7 Days</ToggleGroupItem>
          </ToggleGroup>
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger
              className="flex w-40 **:data-[slot=select-value]:block **:data-[slot=select-value]:truncate @[767px]/card:hidden"
              aria-label="Select a value"
            >
              <SelectValue placeholder="Timeframe" />
            </SelectTrigger>
            <SelectContent className="rounded-xl">
              <SelectItem value="90d" className="rounded-lg">90 Days</SelectItem>
              <SelectItem value="30d" className="rounded-lg">30 Days</SelectItem>
              <SelectItem value="7d" className="rounded-lg">7 Days</SelectItem>
            </SelectContent>
          </Select>
        </CardAction>
      </CardHeader>
      <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
        <ChartContainer
          config={dynamicConfig}
          className="aspect-auto h-[250px] w-full"
        >
          <AreaChart data={filteredData}>
            <defs>
              {series.map((s, idx) => (
                <linearGradient key={`grad-${s.key}`} id={`fill${s.key}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={s.color} stopOpacity={0.8} />
                  <stop offset="95%" stopColor={s.color} stopOpacity={0.1} />
                </linearGradient>
              ))}
            </defs>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey={xAxisKey}
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              minTickGap={32}
              tickFormatter={(value) => {
                // Formatting assuming date strings for now, can be updated based on generic needs
                 try {
                     const date = new Date(value)
                     if (!isNaN(date.getTime())) {
                        return date.toLocaleDateString("en-US", { month: "short", day: "numeric" })
                     }
                     return value
                 } catch {
                     return value
                 }
              }}
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="dot" />}
            />
            {series.map((s) => (
               <Area
                 key={s.key}
                 dataKey={s.key}
                 type="natural"
                 fill={`url(#fill${s.key})`}
                 stroke={s.color}
                 stackId="a"
               />
            ))}
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}

import * as React from "react"
import { type LucideIcon } from "lucide-react"

import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardAction,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

export interface SectionCardProps {
  title: string
  value: string | number
  trendValue?: string
  trendIcon?: LucideIcon | any
  footerTitle?: string
  footerDesc?: string
}

export function SectionCards({ cards }: { cards?: SectionCardProps[] }) {
  // Default placeholder cards if none provided
  const displayCards = cards || [
    { title: "Metric 1", value: "--" },
    { title: "Metric 2", value: "--" },
    { title: "Metric 3", value: "--" },
    { title: "Metric 4", value: "--" },
  ]

  return (
    <div className="*:data-[slot=card]:from-primary/5 *:data-[slot=card]:to-card dark:*:data-[slot=card]:bg-card grid grid-cols-1 gap-4 px-4 *:data-[slot=card]:bg-gradient-to-t *:data-[slot=card]:shadow-xs lg:px-6 @xl/main:grid-cols-2 @5xl/main:grid-cols-4">
      {displayCards.map((card, i) => (
        <Card key={i} className="@container/card">
          <CardHeader>
            <CardDescription>{card.title}</CardDescription>
            <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
              {card.value}
            </CardTitle>
            {card.trendValue && (
              <CardAction>
                <Badge variant="outline">
                  {card.trendIcon && <card.trendIcon className="mr-1 size-4" />}
                  {card.trendValue}
                </Badge>
              </CardAction>
            )}
          </CardHeader>
          <CardFooter className="flex-col items-start gap-1.5 text-sm">
            {card.footerTitle && (
               <div className="line-clamp-1 flex gap-2 font-medium">
                 {card.footerTitle}
               </div>
            )}
            {card.footerDesc && (
               <div className="text-muted-foreground">
                 {card.footerDesc}
               </div>
            )}
          </CardFooter>
        </Card>
      ))}
    </div>
  )
}

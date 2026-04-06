"use client"

import * as React from "react"
import {
  IconBriefcase,
  IconDashboard,
  IconFileAi,
  IconMailFast,
  IconSettings,
  IconUser,
} from "@tabler/icons-react"

import { NavMain } from '@/components/nav-main'
import { NavSecondary } from '@/components/nav-secondary'
import { NavUser } from '@/components/nav-user'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar'

const INITIAL_DATA = {
  user: {
    name: "Student Profile",
    email: "student@example.com",
    avatar: "",
  },
  navMain: [
    { title: "Dashboard", url: "/dashboard", icon: IconDashboard },
    { title: "Internships", url: "/internships", icon: IconBriefcase },
    { title: "Job Matches", url: "/matches", icon: IconBriefcase },
    { title: "Resume Upload", url: "/tools/resume", icon: IconFileAi },
    { title: "Cover Letter", url: "/tools/email", icon: IconMailFast },
    { title: "Profile", url: "/profile", icon: IconUser },
  ],
  navSecondary: [
    { title: "Settings", url: "#", icon: IconSettings },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const [userData, setUserData] = React.useState(INITIAL_DATA.user)

  React.useEffect(() => {
    // Load active user from auth session login
    const storedUser = localStorage.getItem("internai_user")
    if (storedUser) {
        try {
            const parsed = JSON.parse(storedUser)
            setUserData({ name: parsed.name, email: parsed.email, avatar: "" })
        } catch (e) {}
    }
  }, [])
  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              asChild
              className="data-[slot=sidebar-menu-button]:!p-0 hover:bg-transparent"
            >
              <div className="flex items-center gap-3 px-1 py-4">
                <img 
                  src="/logo.jpg" 
                  alt="InternAI Logo" 
                  className="h-10 w-10 object-contain rounded-md border border-gray-100/50" 
                />
                <span className="text-xl font-bold tracking-tight text-white drop-shadow-sm">
                  InternAI
                </span>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={INITIAL_DATA.navMain} />
        <NavSecondary items={INITIAL_DATA.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={userData} />
      </SidebarFooter>
    </Sidebar>
  )
}

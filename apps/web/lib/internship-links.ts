export function createCompanySearchUrl(company: string, role?: string, location?: string) {
  const queryParts = [company, role, "internship", "careers", location]
    .filter((part) => part && part.trim().length > 0)
    .join(" ")

  return `https://www.google.com/search?q=${encodeURIComponent(queryParts)}`
}

function createCompanyDomainSearchUrl(domain: string, company?: string, role?: string, location?: string) {
  const queryParts = [`site:${domain}`, company, role, "internship", location]
    .filter((part) => part && part.trim().length > 0)
    .join(" ")

  return `https://www.google.com/search?q=${encodeURIComponent(queryParts)}`
}

function getPreferredSearchDomain(hostname: string) {
  if (hostname.includes("google.com") || hostname.includes("linkedin.com")) {
    return ""
  }

  if (hostname.includes("microsoft.com")) {
    return "jobs.careers.microsoft.com"
  }

  if (hostname.includes("nvidia.com")) {
    return "nvidia.com"
  }

  return hostname.replace(/^www\./, "")
}

function shouldUseDomainSearch(url: URL) {
  const hostname = url.hostname.toLowerCase()
  const path = url.pathname.toLowerCase()

  if (hostname.includes("microsoft.com") && path.includes("/careers/jobs/")) {
    return true
  }

  if (hostname.includes("linkedin.com") || hostname.includes("google.com")) {
    return true
  }

  return false
}

type InternshipLinkInput = {
  application_link?: string
  company?: string
  role?: string
  location?: string
}

export function getSearchFirstApplicationUrl(internship: InternshipLinkInput) {
  const rawLink = internship.application_link?.trim()

  if (rawLink) {
    try {
      const url = new URL(rawLink)
      const hostname = url.hostname.toLowerCase()
      const isPlaceholder = hostname === "example.com" || hostname.endsWith(".example.com")

      if (!isPlaceholder) {
        const preferredDomain = getPreferredSearchDomain(hostname)

        if (preferredDomain) {
          return createCompanyDomainSearchUrl(
            preferredDomain,
            internship.company || "",
            internship.role,
            internship.location
          )
        }

        if (shouldUseDomainSearch(url)) {
          return createCompanySearchUrl(internship.company || "", internship.role, internship.location)
        }
      }
    } catch {
      // Ignore malformed URLs and fall back to a normal search.
    }
  }

  return createCompanySearchUrl(internship.company || "", internship.role, internship.location)
}

export function getOriginalApplicationUrl(internship: InternshipLinkInput) {
  const rawLink = internship.application_link?.trim()

  if (rawLink) {
    try {
      const url = new URL(rawLink)
      const hostname = url.hostname.toLowerCase()
      const isPlaceholder = hostname === "example.com" || hostname.endsWith(".example.com")

      if (!isPlaceholder) {
        return rawLink
      }
    } catch {
      return null
    }
  }

  return null
}

export function getBestApplicationUrl(internship: InternshipLinkInput) {
  return getSearchFirstApplicationUrl(internship)
}

/**
 * Frontend API Client
 * Connects the React application to the FastAPI endpoints.
 */

const BACKEND_URL = (process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");
export const CORE_API_BASE_URL = BACKEND_URL;
export const API_BASE_URL = `${BACKEND_URL}/api/v1`;

export interface ParsedResumeResponse {
    resume_id: string;
    message: string;
    parsed_data: any;
}

export interface ApplicationPackage {
    resume_id: string;
    categorized_skills: {
        programming_languages: string[];
        ai_ml_skills: string[];
        tools_frameworks: string[];
    };
    applications: Array<{
        internship: {
            role: string;
            company: string;
            location: string;
            description: string;
            application_link: string;
        };
        match_evaluation: {
            match_score: number;
            reasoning: string;
            recommendation: string;
        };
        cover_letter: string | null;
    }>;
}

export interface GeneratedMaterials {
    application_id?: string | null;
    cover_letter: string | null;
    tailored_resume: string | null;
    email_subject: string | null;
    email_body: string | null;
}

/**
 * Helper to get the auth token from local storage
 * Using simple session handling with user_id rather than JWT.
 */
const getAuthToken = () => {
    if (typeof window !== 'undefined') {
        const userId = localStorage.getItem('user_id');
        return userId ? `Bearer ${userId}` : '';
    }
    return '';
}

/**
 * Uploads a physical PDF resume to the parsing service.
 */
export async function uploadResume(file: File): Promise<ParsedResumeResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/resume/upload`, {
        method: "POST",
        headers: {
            "Authorization": getAuthToken(),
        },
        body: formData,
    });

    if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Upload failed with status: ${response.status}`);
    }

    return response.json();
}

/**
 * Triggers the 7-agent workflow to find matches and generate applications.
 */
export async function runWorkflow(resumeId: string, preferredField: string, location: string): Promise<ApplicationPackage> {
    const response = await fetch(`${API_BASE_URL}/workflow/run`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": getAuthToken(),
        },
        body: JSON.stringify({
            resume_id: resumeId,
            preferred_field: preferredField,
            location: location,
        }),
    });

    if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Workflow run failed with status: ${response.status}`);
    }

    return response.json();
}

/**
 * Fetches the user's previously applied internships
 */
export async function getAppliedInternships() {
    try {
        const response = await fetch(`${API_BASE_URL}/internships/history`, {
            method: "GET",
            headers: {
                "Authorization": getAuthToken(),
            },
        });

        if (!response.ok) {
            console.warn(`Failed to fetch history. Server returned ${response.status}`);
            return [];
        }

        return await response.json();
    } catch (error) {
        console.warn("Browser completely blocked fetch to /internships/history:", error);
        return [];
    }
}

/**
 * Stage 2: Triggers Application Generation (RAG, Tailored Resume, Email)
 */
export async function generateApplication(resumeId: string, internship: any, matchScore: number, reasoning: string): Promise<GeneratedMaterials> {
    const response = await fetch(`${CORE_API_BASE_URL}/generate-application`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": getAuthToken(),
        },
        body: JSON.stringify({
            resume_id: resumeId,
            internship: internship,
            match_score: matchScore,
            reasoning: reasoning
        }),
    });

    if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to generate application materials");
    }

    return response.json();
}

export async function updateGeneratedMaterials(
    applicationId: string,
    materials: {
        tailored_resume: string;
        cover_letter: string;
        email_subject: string;
        email_body: string;
    }
) {
    const response = await fetch(`${CORE_API_BASE_URL}/application-materials`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "Authorization": getAuthToken(),
        },
        body: JSON.stringify({
            application_id: applicationId,
            ...materials,
        }),
    });

    if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to save edited materials");
    }

    return response.json();
}

/**
 * Manually scrape Google for internships
 */
export async function searchInternships(query: string, location: string) {
    const params = new URLSearchParams({
        query: query,
        location: location
    });
    
    const response = await fetch(`${API_BASE_URL}/internships/search?${params.toString()}`, {
        method: "GET",
        headers: {
            "Authorization": getAuthToken(),
        },
    });

    if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to search internships");
    }

    return response.json();
}

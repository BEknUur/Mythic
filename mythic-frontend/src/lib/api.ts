import { z } from 'zod'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';


/* ──────────── VALIDATIO SCHEMAS─────────── */
const StartScrapeResponseSchema = z.object({
  runId: z.string(),
  message: z.string(),
})

const ProfileSchema = z.object({
  username: z.string(),
  fullName: z.string(),
  followers: z.number(),
  posts: z.number(),
  stories: z.number().optional(),
})

const StagesSchema = z.object({
  data_collected: z.boolean(),
  images_downloaded: z.boolean(),
  book_generated: z.boolean(),
})

const StatusResponseSchema = z.object({
  runId: z.string(),
  message: z.string(),
  style: z.string().optional(),
  format: z.string().optional(),
  stages: StagesSchema,
  profile: ProfileSchema.optional(),
  files: z.record(z.string()).default({}),
})

const HealthResponseSchema = z.object({
  status: z.string(),
  message: z.string(),
})

const UserBookSchema = z.object({
  id: z.string(),
  run_id: z.string(),
  title: z.string(),
  created_at: z.string(),
  profile_username: z.string().optional(),
  profile_full_name: z.string().optional(),
  has_pdf: z.boolean(),
  has_html: z.boolean(),
})

const UserBooksResponseSchema = z.object({
  books: z.array(UserBookSchema),
  total: z.number(),
})

const SaveBookResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  book_id: z.string().optional(),
})

const AISuggestionResponseSchema = z.object({
  suggestion: z.string(),
  confidence: z.number().optional(),
})

/* ──────────── TYPES ──────────── */
export type StartScrapeResponse = z.infer<typeof StartScrapeResponseSchema>
export type StatusResponse = z.infer<typeof StatusResponseSchema>
export type HealthResponse = z.infer<typeof HealthResponseSchema>
export type UserBook = z.infer<typeof UserBookSchema>
export type UserBooksResponse = z.infer<typeof UserBooksResponseSchema>
export type SaveBookResponse = z.infer<typeof SaveBookResponseSchema>
export type AISuggestionResponse = z.infer<typeof AISuggestionResponseSchema>

/* ──────────── ERROR CLASS ──────────── */
class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message)
    this.name = 'ApiError'
  }
}

/* ──────────── HELPERS ──────────── */
const headersWithAuth = (token?: string) => ({
  'Content-Type': 'application/json',
  ...(token ? { Authorization: `Bearer ${token}` } : {}),
})

const asBlobDownload = async (
  response: Response,
  filename: string,
): Promise<void> => {
  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

/* ──────────── PUBLIC API ──────────── */
export const api = {
  /* ---------- health ---------- */
  async healthCheck(): Promise<HealthResponse> {
    const res = await fetch(`${BASE_URL}/health`)
    if (!res.ok) throw new ApiError(`HTTP ${res.status}`, res.status)
    return HealthResponseSchema.parse(await res.json())
  },

  /* ---------- instagram → apify ---------- */
  async startScrape(
    instagramUrl: string,
    style: string = 'romantic',
    token?: string,
  ): Promise<StartScrapeResponse> {
    const url = new URL(`${BASE_URL}/start-scrape`);
    url.searchParams.set('url', instagramUrl);
    url.searchParams.set('style', style);
    const res = await fetch(url.toString(), {
      headers: headersWithAuth(token),
    })
    if (!res.ok)
      throw new ApiError(await res.text(), res.status)
    return StartScrapeResponseSchema.parse(await res.json())
  },

  async getStatus(runId: string, token?: string): Promise<StatusResponse> {
    const res = await fetch(`${BASE_URL}/status/${runId}`, {
      headers: headersWithAuth(token),
    })
    if (!res.ok)
      throw new ApiError(await res.text(), res.status)
    return StatusResponseSchema.parse(await res.json())
  },

  /* ---------- runtime URLs (view / download) ---------- */
  getViewUrl(runId: string, token?: string) {
    const url = new URL(`${BASE_URL}/view/${runId}/book.html`)
    if (token) url.searchParams.set('token', token)
    return url.toString()
  },

  getDownloadUrl(runId: string, file: string, token?: string) {
    const url = new URL(`${BASE_URL}/download/${runId}/${file}`)
    if (token) url.searchParams.set('token', token)
    return url.toString()
  },

  /* ---------- HTML книги ---------- */
  async getBookContent(runId: string, token?: string): Promise<string> {
    const res = await fetch(`${BASE_URL}/view/${runId}/book.html`, {
      headers: headersWithAuth(token),
    })
    if (!res.ok) throw new Error(res.statusText)
    return res.text()
  },

  /* ---------- PDF ---------- */
  async generatePdf(runId: string, token?: string) {
    const res = await fetch(`${BASE_URL}/generate-pdf/${runId}`, {
      method: 'POST',
      headers: headersWithAuth(token),
    })
    if (!res.ok)
      throw new ApiError(await res.text(), res.status)
    return res.json() as Promise<{
      status: string
      message: string
      download_url?: string
    }>
  },

  async downloadFile(runId: string, filename: string, token?: string) {
    if (filename === 'book.pdf') await this.generatePdf(runId, token)
    const res = await fetch(`${BASE_URL}/download/${runId}/${filename}`, {
      headers: headersWithAuth(token),
    })
    if (!res.ok) throw new Error(res.statusText)
    await asBlobDownload(res, filename)
  },

  /* ---------- library ---------- */
  async saveBookToLibrary(
    runId: string,
    customTitle?: string,
    token?: string,
  ): Promise<SaveBookResponse> {
    const res = await fetch(`${BASE_URL}/books/save`, {
      method: 'POST',
      headers: headersWithAuth(token),
      body: JSON.stringify({ run_id: runId, custom_title: customTitle }),
    })
    if (!res.ok)
      throw new ApiError(await res.text(), res.status)
    return SaveBookResponseSchema.parse(await res.json())
  },

  async getMyBooks(token?: string): Promise<UserBooksResponse> {
    const res = await fetch(`${BASE_URL}/books/my`, {
      headers: headersWithAuth(token),
    })
    if (!res.ok)
      throw new ApiError(await res.text(), res.status)
    return UserBooksResponseSchema.parse(await res.json())
  },

  async deleteBook(bookId: string, token?: string): Promise<void> {
    const res = await fetch(`${BASE_URL}/books/${bookId}`, {
      method: 'DELETE',
      headers: headersWithAuth(token),
    })
    if (!res.ok) throw new ApiError(await res.text(), res.status)
  },

  /* ---------- saved book URLs ---------- */
  getSavedBookViewUrl(id: string, token?: string) {
    const url = new URL(`${BASE_URL}/books/${id}/view`)
    if (token) url.searchParams.set('token', token)
    return url.toString()
  },

  getSavedBookDownloadUrl(id: string, file: string, token?: string) {
    const url = new URL(`${BASE_URL}/books/${id}/download/${file}`)
    if (token) url.searchParams.set('token', token)
    return url.toString()
  },

  async downloadSavedBook(
    id: string,
    file: string,
    token?: string,
  ): Promise<void> {
    const res = await fetch(
      `${BASE_URL}/books/${id}/download/${file}`,
      { headers: headersWithAuth(token) },
    )
    if (!res.ok) throw new Error(res.statusText)
    await asBlobDownload(res, file)
  },

  /* ---------- AI suggestions ---------- */
  async getAISuggestion(
    selectedText: string,
    bookContext: string,
    token?: string,
  ): Promise<AISuggestionResponse> {
    const res = await fetch(`${BASE_URL}/ai/suggest`, {
      method: 'POST',
      headers: headersWithAuth(token),
      body: JSON.stringify({
        selected_text: selectedText,
        book_context: bookContext,
      }),
    })
    if (!res.ok)
      throw new ApiError(await res.text(), res.status)
    return AISuggestionResponseSchema.parse(await res.json())
  },

  async updateBookContent(
    bookOrRunId: string,
    updatedContent: string,
    token?: string,
  ): Promise<{ success: boolean; message: string }> {
    const res = await fetch(`${BASE_URL}/books/update-content`, {
      method: 'POST',
      headers: headersWithAuth(token),
      body: JSON.stringify({
        book_or_run_id: bookOrRunId,
        updated_content: updatedContent,
      }),
    })
    if (!res.ok)
      throw new ApiError(await res.text(), res.status)
    return res.json()
  },

  getEditChatUrl: () => {
    return `${BASE_URL}/api/edit-chat`;
  },

  async moderateText(text: string, token?: string): Promise<{ flagged: boolean; error?: string }> {
    const response = await fetch(`${BASE_URL}/api/moderate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ input: text })
    });
    if (!response.ok) {
        throw new Error('Moderation request failed');
    }
    return response.json();
  },

  /* ---------- book creation ---------- */
  async createBook(
    runId: string,
    format: string = 'classic',
    token?: string,
  ): Promise<{ success: boolean; message: string }> {
    const endpoint = format === 'flipbook' ? '/create-flipbook' : '/create-book';
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: headersWithAuth(token),
      body: JSON.stringify({ runId: runId, format: format }),
    })
    if (!res.ok)
      throw new ApiError(await res.text(), res.status)
    return res.json()
  },
}

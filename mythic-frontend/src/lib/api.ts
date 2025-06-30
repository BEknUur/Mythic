import { z } from 'zod';

const BASE_URL = 'http://164.90.172.68:8000';

// Zod schemas for API validation
const StartScrapeResponseSchema = z.object({
  runId: z.string(),
  message: z.string(),
});

const ProfileSchema = z.object({
  username: z.string(),
  fullName: z.string(),
  followers: z.number(),
  posts: z.number(),
});

const StagesSchema = z.object({
  data_collected: z.boolean(),
  images_downloaded: z.boolean(),
  book_generated: z.boolean(),
});

const StatusResponseSchema = z.object({
  runId: z.string(),
  message: z.string(),
  stages: StagesSchema,
  profile: ProfileSchema.optional(),
  files: z.record(z.string()).default({}),
});

const HealthResponseSchema = z.object({
  status: z.string(),
  message: z.string(),
});

// Новые схемы для пользовательских книг
const UserBookSchema = z.object({
  id: z.string(),
  run_id: z.string(),
  title: z.string(),
  created_at: z.string(),
  profile_username: z.string().optional(),
  profile_full_name: z.string().optional(),
  has_pdf: z.boolean(),
  has_html: z.boolean(),
});

const UserBooksResponseSchema = z.object({
  books: z.array(UserBookSchema),
  total: z.number(),
});

const SaveBookResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  book_id: z.string().optional(),
});

// Types
export type StartScrapeResponse = z.infer<typeof StartScrapeResponseSchema>;
export type StatusResponse = z.infer<typeof StatusResponseSchema>;
export type HealthResponse = z.infer<typeof HealthResponseSchema>;
export type UserBook = z.infer<typeof UserBookSchema>;
export type UserBooksResponse = z.infer<typeof UserBooksResponseSchema>;
export type SaveBookResponse = z.infer<typeof SaveBookResponseSchema>;

class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

// Функция для получения заголовков с токеном
const getAuthHeaders = (token?: string) => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
};

// API functions
export const api = {
  async healthCheck(): Promise<HealthResponse> {
    try {
      const response = await fetch(`${BASE_URL}/health`);
      if (!response.ok) {
        throw new ApiError(`HTTP ${response.status}`, response.status);
      }
      const data = await response.json();
      return HealthResponseSchema.parse(data);
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError('Ошибка соединения с сервером');
    }
  },

  async startScrape(instagramUrl: string, token?: string): Promise<StartScrapeResponse> {
    try {
      console.log('Starting scrape for URL:', instagramUrl);
      const response = await fetch(`${BASE_URL}/start-scrape?url=${encodeURIComponent(instagramUrl)}`, {
        method: 'GET',
        headers: getAuthHeaders(token),
      });
      if (!response.ok) {
        const errorText = await response.text();
        console.error('StartScrape API error:', response.status, errorText);
        throw new ApiError(`HTTP ${response.status}: ${errorText}`, response.status);
      }
      const data = await response.json();
      console.log('StartScrape response:', data);
      const parsedData = StartScrapeResponseSchema.parse(data);
      console.log('Parsed runId:', parsedData.runId);
      return parsedData;
    } catch (error) {
      console.error('startScrape error details:', error);
      if (error instanceof ApiError) throw error;
      throw new ApiError('Ошибка запуска обработки');
    }
  },

  async getStatus(runId: string, token?: string): Promise<StatusResponse> {
    try {
      const response = await fetch(`${BASE_URL}/status/${runId}`, {
        headers: getAuthHeaders(token),
      });
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Status API error:', response.status, errorText);
        throw new ApiError(`HTTP ${response.status}: ${errorText}`, response.status);
      }
      const data = await response.json();
      console.log('Status response:', data);
      return StatusResponseSchema.parse(data);
    } catch (error) {
      console.error('getStatus error details:', error);
      if (error instanceof ApiError) throw error;
      throw new ApiError('Ошибка получения статуса');
    }
  },

  getViewUrl(runId: string, token?: string): string {
    const url = new URL(`${BASE_URL}/view/${runId}/book.html`);
    if (token) {
      url.searchParams.set('token', token);
    }
    return url.toString();
  },

  getDownloadUrl(runId: string, filename: string, token?: string): string {
    const url = new URL(`${BASE_URL}/download/${runId}/${filename}`);
    if (token) {
      url.searchParams.set('token', token);
    }
    return url.toString();
  },

  async getBookContent(runId: string, token?: string): Promise<string> {
    const response = await fetch(`${BASE_URL}/view/${runId}/book.html`, {
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get book content: ${response.statusText}`);
    }

    return response.text();
  },

  async downloadFile(runId: string, filename: string, token?: string): Promise<void> {
    // If trying to download PDF, generate it first
    if (filename === 'book.pdf') {
      try {
        await this.generatePdf(runId, token);
      } catch (error) {
        console.error('Error generating PDF:', error);
        // Continue with download attempt even if generation fails
      }
    }

    const response = await fetch(`${BASE_URL}/download/${runId}/${filename}`, {
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to download file: ${response.statusText}`);
    }

    // Создаем blob и скачиваем файл
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },

  async generatePdf(runId: string, token?: string): Promise<{ status: string; message: string; download_url?: string }> {
    try {
      const response = await fetch(`${BASE_URL}/generate-pdf/${runId}`, {
        method: 'POST',
        headers: getAuthHeaders(token),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new ApiError(`HTTP ${response.status}: ${errorText}`, response.status);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError('Ошибка генерации PDF');
    }
  },

  // Методы для работы с пользовательскими книгами
  async saveBookToLibrary(runId: string, customTitle?: string, token?: string): Promise<SaveBookResponse> {
    try {
      const response = await fetch(`${BASE_URL}/books/save`, {
        method: 'POST',
        headers: getAuthHeaders(token),
        body: JSON.stringify({
          run_id: runId,
          custom_title: customTitle,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new ApiError(`HTTP ${response.status}: ${errorText}`, response.status);
      }

      const data = await response.json();
      return SaveBookResponseSchema.parse(data);
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError('Ошибка сохранения книги');
    }
  },

  async getMyBooks(token?: string): Promise<UserBooksResponse> {
    try {
      const response = await fetch(`${BASE_URL}/books/my`, {
        headers: getAuthHeaders(token),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new ApiError(`HTTP ${response.status}: ${errorText}`, response.status);
      }

      const data = await response.json();
      return UserBooksResponseSchema.parse(data);
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError('Ошибка получения списка книг');
    }
  },

  async deleteBook(bookId: string, token?: string): Promise<void> {
    try {
      const response = await fetch(`${BASE_URL}/books/${bookId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(token),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new ApiError(`HTTP ${response.status}: ${errorText}`, response.status);
      }
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError('Ошибка удаления книги');
    }
  },

  getSavedBookViewUrl(bookId: string, token?: string): string {
    const url = new URL(`${BASE_URL}/books/${bookId}/view`);
    if (token) {
      url.searchParams.set('token', token);
    }
    return url.toString();
  },

  getSavedBookDownloadUrl(bookId: string, filename: string, token?: string): string {
    const url = new URL(`${BASE_URL}/books/${bookId}/download/${filename}`);
    if (token) {
      url.searchParams.set('token', token);
    }
    return url.toString();
  },

  async downloadSavedBook(bookId: string, filename: string, token?: string): Promise<void> {
    const response = await fetch(`${BASE_URL}/books/${bookId}/download/${filename}`, {
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to download saved book: ${response.statusText}`);
    }

    // Создаем blob и скачиваем файл
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }
}; 
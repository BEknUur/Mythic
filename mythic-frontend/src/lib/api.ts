import { z } from 'zod';

const BASE_URL = 'http://localhost:8000';

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
  stages: StagesSchema,
  profile: ProfileSchema.optional(),
  files: z.record(z.string()).default({}),
});

const HealthResponseSchema = z.object({
  status: z.string(),
  message: z.string(),
});

// Types
export type StartScrapeResponse = z.infer<typeof StartScrapeResponseSchema>;
export type StatusResponse = z.infer<typeof StatusResponseSchema>;
export type HealthResponse = z.infer<typeof HealthResponseSchema>;

class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

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

  async startScrape(instagramUrl: string): Promise<StartScrapeResponse> {
    try {
      console.log('Starting scrape for URL:', instagramUrl);
      const response = await fetch(`${BASE_URL}/start-scrape?url=${encodeURIComponent(instagramUrl)}`, {
        method: 'GET',
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

  async getStatus(runId: string): Promise<StatusResponse> {
    try {
      const response = await fetch(`${BASE_URL}/status/${runId}`);
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

  getViewUrl(runId: string): string {
    return `${BASE_URL}/view/${runId}/book.html`;
  },

  getDownloadUrl(runId: string, filename: string): string {
    return `${BASE_URL}/download/${runId}/${filename}`;
  },
}; 
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { Instagram, CheckCircle, AlertCircle, Loader2, Lock, User, Server, Book } from 'lucide-react';
import { useUser, SignInButton, useAuth } from '@clerk/clerk-react';
import { api } from '@/lib/api';
import { StylePicker } from './StylePicker';
import { AnimatePresence, motion } from 'framer-motion';
import { TOUR_STEP_IDS } from './ui/tour';

interface FormProps {
  onStartScrape: (runId: string) => void;
}

const StepMainForm = ({ onStartScrape }: FormProps) => {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [style, setStyle] = useState('romantic');
  const { toast } = useToast();
  const { getToken } = useAuth();
  const { isSignedIn } = useUser();

  // Функция для нормализации входа пользователя
  const normalizeInstagramInput = (input: string): string => {
    const trimmed = input.trim();
    
    // Если это уже полный URL, возвращаем как есть
    if (trimmed.match(/^https?:\/\/(www\.)?instagram\.com\/[a-zA-Z0-9_.]+\/?$/)) {
      return trimmed;
    }
    
    // Убираем @ если есть в начале
    const cleanUsername = trimmed.replace(/^@/, '');
    
    // Проверяем, что username состоит только из допустимых символов
    if (cleanUsername.match(/^[a-zA-Z0-9_.]+$/)) {
      return `https://instagram.com/${cleanUsername}`;
    }
    
    return trimmed; // Возвращаем как есть для показа ошибки валидации
  };

  // Функция для извлечения username из URL или input
  const extractUsername = (input: string): string => {
    const trimmed = input.trim();
    
    // Если это URL, извлекаем username
    const urlMatch = trimmed.match(/^https?:\/\/(www\.)?instagram\.com\/([a-zA-Z0-9_.]+)\/?$/);
    if (urlMatch) {
      return urlMatch[2];
    }
    
    // Убираем @ если есть в начале
    return trimmed.replace(/^@/, '');
  };

  const validateInstagramInput = (input: string): boolean => {
    const trimmed = input.trim();
    
    // Проверяем полный URL
    const urlPattern = /^https?:\/\/(www\.)?instagram\.com\/[a-zA-Z0-9_.]+\/?$/;
    if (urlPattern.test(trimmed)) {
      return true;
    }
    
    // Проверяем username (с или без @)
    const cleanUsername = trimmed.replace(/^@/, '');
    const usernamePattern = /^[a-zA-Z0-9_.]+$/;
    return usernamePattern.test(cleanUsername) && cleanUsername.length > 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateInstagramInput(url)) {
      setError('Пожалуйста, введите корректный Instagram профиль (например: ualikhaanuly или @ualikhaanuly).');
      return;
    }
    
    setError('');
    setIsLoading(true);

    try {
      const token = await getToken();
      const normalizedUrl = normalizeInstagramInput(url);
      const extractedUsername = extractUsername(url);
      
      const result = await api.startScrape(normalizedUrl, extractedUsername, style, token || undefined);
      toast({ 
        title: "Отлично!", 
        description: isSignedIn 
          ? `Книга в стиле "${style}" отправлена в обработку.`
          : `Книга создается! Вы сможете просмотреть первые 10 страниц. Для полного доступа потребуется авторизация.`
      });
      onStartScrape(result.runId);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Неизвестная ошибка';
      setError(errorMessage);
      toast({ title: "Ошибка", description: errorMessage, variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
    >
      <div className="text-center mb-8">
        <div className="mx-auto w-12 h-12 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-4">
          <Book className="h-6 w-6 text-gray-500 dark:text-gray-400" />
        </div>
        <h3 className="text-xl font-bold text-gray-900 dark:text-gray-50">Создайте вашу книгу</h3>
        <p className="text-gray-500 dark:text-gray-400">
          {isSignedIn 
            ? "Создайте книгу с полным доступом"
            : "Создайте книгу и просмотрите первые 10 страниц бесплатно"}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="instagram-url" className="text-gray-600 dark:text-gray-400">Instagram профиль</Label>
          <div className="relative">
            <Instagram className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <Input
              id={TOUR_STEP_IDS.INSTAGRAM_INPUT}
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="ualikhaanuly"
              className="pl-10"
              required
              disabled={isLoading}
            />
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Просто введите username (например: ualikhaanuly) или полную ссылку
          </p>
        </div>

        <div className="space-y-2">
          <Label>Выберите стиль книги</Label>
          <StylePicker value={style} onChange={setStyle} />
        </div>

        {!isSignedIn && (
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <Lock className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="flex-1">
                <h4 className="text-sm font-medium text-blue-900 dark:text-blue-100">Режим предварительного просмотра</h4>
                <p className="text-xs text-blue-700 dark:text-blue-300 mt-1">
                  Вы сможете просмотреть первые 10 страниц. Для полного доступа и сохранения книги войдите в систему.
                </p>
                <div className="mt-2">
                  <SignInButton mode="modal">
                    <Button variant="outline" size="sm" className="text-blue-600 border-blue-300 hover:bg-blue-50">
                      Войти для полного доступа
                    </Button>
                  </SignInButton>
                </div>
              </div>
            </div>
          </div>
        )}

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Button type="submit" disabled={isLoading || !url.trim()} className="w-full h-12 text-base bg-gray-900 text-white hover:bg-gray-800 dark:bg-gray-50 dark:text-gray-900 dark:hover:bg-gray-200">
          {isLoading ? (
            <>
              <Loader2 className="h-5 w-5 mr-2 animate-spin" />
              Создаем...
            </>
          ) : (
            isSignedIn ? 'Создать книгу' : 'Создать книгу (предпросмотр)'
          )}
        </Button>
      </form>
    </motion.div>
  );
};

export function Form({ onStartScrape }: FormProps) {
  // Убираем проверку авторизации и всегда показываем форму
  return (
    <section className="py-20 px-4">
      <div className="max-w-md mx-auto">
        <div className="bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-2xl p-8 shadow-lg shadow-gray-100/50 dark:shadow-black/50">
          <StepMainForm onStartScrape={onStartScrape} />
        </div>
        <div className="mt-6 text-center text-sm text-gray-400 dark:text-gray-500">
          <p>Ваши данные в безопасности.</p>
        </div>
      </div>
    </section>
  );
} 
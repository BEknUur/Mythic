import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@clerk/clerk-react';
import { api } from '@/lib/api';
import { ArrowLeft, Loader2 } from 'lucide-react';

interface BookReaderProps {
  bookId?: string;
  runId?: string;
  onBack: () => void;
}

export function BookReader({ bookId, runId, onBack }: BookReaderProps) {
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [cssContent, setCssContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const { getToken } = useAuth();
  const { toast } = useToast();
  const styleRef = useRef<HTMLStyleElement | null>(null);

  useEffect(() => {
    loadBookContent();
    // Очищаем стили при размонтировании
    return () => {
      if (styleRef.current && document.head.contains(styleRef.current)) {
        document.head.removeChild(styleRef.current);
      }
    };
    // eslint-disable-next-line
  }, [bookId, runId]);

  const loadBookContent = async () => {
    try {
      setLoading(true);
      const token = await getToken();
      let rawHtml: string;
      if (runId) {
        rawHtml = await api.getBookContent(runId, token || undefined);
      } else if (bookId) {
        const response = await fetch(api.getSavedBookViewUrl(bookId, token || undefined));
        rawHtml = await response.text();
      } else {
        throw new Error('Нужен bookId или runId');
      }
      // Извлекаем <style> и <body> из HTML
      const styleMatch = rawHtml.match(/<style[^>]*>([\s\S]*?)<\/style>/i);
      const css = styleMatch ? styleMatch[1] : '';
      setCssContent(css);
      const bodyMatch = rawHtml.match(/<body[^>]*>([\s\S]*)<\/body>/i);
      let bodyContent = bodyMatch ? bodyMatch[1] : rawHtml;
      setHtmlContent(bodyContent);
      // Вставляем стили в <head>
      if (css) {
        const styleEl = document.createElement('style');
        styleEl.textContent = css;
        document.head.appendChild(styleEl);
        styleRef.current = styleEl;
      }
    } catch (error) {
      console.error('Ошибка загрузки книги:', error);
      toast({
        title: 'Ошибка',
        description: 'Не удалось загрузить книгу',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-600" />
          <p className="text-gray-600">Загружаем вашу книгу...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <div className="sticky top-0 z-10 bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            onClick={onBack}
            className="text-gray-700 hover:text-black"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Назад
          </Button>
        </div>
      </div>
      <div className="flex-1 flex justify-center items-center bg-[#f5f2e8]">
        <div
          className="book-html max-w-4xl w-full shadow-2xl rounded-lg overflow-hidden bg-white"
          style={{ minHeight: 600, minWidth: 350, padding: 0 }}
          dangerouslySetInnerHTML={{ __html: htmlContent }}
        />
      </div>
    </div>
  );
}
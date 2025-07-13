import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@clerk/clerk-react';
import { api, type StatusResponse } from '@/lib/api';
import { BookReader } from './BookReader';
import { FlipBookReader } from './FlipBookReader';
import { ArrowLeft, ExternalLink, Download } from 'lucide-react';

interface BookViewerProps {
  bookId?: string;
  runId?: string;
}

export function BookViewer({ bookId, runId }: BookViewerProps) {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { getToken } = useAuth();
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [isFlipView, setIsFlipView] = useState(false);

  // Если передан bookId, используем его как runId (для совместимости с URL)
  const actualRunId = runId || bookId;

  useEffect(() => {
    loadBookStatus();
  }, [actualRunId]);

  const loadBookStatus = async () => {
    if (!actualRunId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const token = await getToken();
      const statusData = await api.getStatus(actualRunId, token || undefined);
      setStatus(statusData);
      
      // Автоматически переключаемся на flipbook если это flipbook формат
      if (statusData.format === 'flipbook') {
        setIsFlipView(true);
      }
    } catch (error) {
      console.error('Ошибка загрузки статуса книги:', error);
      toast({
        title: 'Ошибка',
        description: 'Не удалось загрузить информацию о книге',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/library');
  };

  const handleDownload = async () => {
    if (!actualRunId) return;
    
    try {
      const token = await getToken();
      await api.downloadFile(actualRunId, 'book.pdf', token || undefined);
      toast({
        title: 'Готово',
        description: 'Книга скачана',
      });
    } catch (error) {
      console.error('Ошибка скачивания:', error);
      toast({
        title: 'Ошибка',
        description: 'Не удалось скачать книгу',
        variant: 'destructive',
      });
    }
  };

  const openInNewTab = () => {
    if (actualRunId) {
      window.open(`/view/${actualRunId}/book.html`, '_blank');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-violet-600 mx-auto"></div>
          <p className="text-lg text-gray-600">Загружаем вашу книгу...</p>
        </div>
      </div>
    );
  }

  // Если это flipbook формат, показываем FlipBookReader
  if (isFlipView) {
    return (
      <FlipBookReader
        runId={actualRunId}
        onBack={handleBack}
      />
    );
  }

  // Иначе показываем обычный BookReader
  return (
    <BookReader
      runId={actualRunId}
      onBack={handleBack}
    />
  );
} 
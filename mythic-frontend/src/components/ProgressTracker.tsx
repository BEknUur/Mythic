import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress as ProgressBar } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { CheckCircle, Eye, Download, RotateCcw, Loader2, RefreshCw, ExternalLink, AlertTriangle } from 'lucide-react';
import { api, type StatusResponse } from '@/lib/api';
import { BookReadyDialog } from './BookReadyDialog';

interface ProgressTrackerProps {
  runId: string;
  onComplete: () => void;
  onReset: () => void;
}

export function ProgressTracker({ runId, onComplete, onReset }: ProgressTrackerProps) {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [error, setError] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const [isManualChecking, setIsManualChecking] = useState(false);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [showInlineViewer, setShowInlineViewer] = useState(false);
  const [bookContent, setBookContent] = useState<string>('');
  const [isLoadingBook, setIsLoadingBook] = useState(false);
  const [showIframeViewer, setShowIframeViewer] = useState(false);
  const [isBookReadyDialogOpen, setIsBookReadyDialogOpen] = useState(false);
  const { toast } = useToast();

  const isBookReady = status?.stages.book_generated || false;

  const handleStatusUpdate = (currentStatus: StatusResponse) => {
    setStatus(currentStatus);
    if (currentStatus.stages.book_generated) {
      if (!isBookReadyDialogOpen) {
        toast({
          title: "🎉 История любви готова!",
          description: "Ваша персональная романтическая книга создана.",
        });
        setIsBookReadyDialogOpen(true);
        onComplete();
      }
    }
  };

  const checkStatusManually = async () => {
    setIsManualChecking(true);
    try {
      const currentStatus = await api.getStatus(runId);
      handleStatusUpdate(currentStatus);
      setLastChecked(new Date());
    } catch (error) {
      setError('Ошибка при проверке статуса');
      toast({
        title: "❌ Ошибка",
        description: "Не удалось проверить статус книги",
        variant: "destructive",
      });
    } finally {
      setIsManualChecking(false);
    }
  };

  useEffect(() => {
    let retryCount = 0;
    const maxRetries = 5;
    let isCancelled = false;

    const pollStatus = async () => {
      if (isBookReady || isCancelled) return;
      try {
        const currentStatus = await api.getStatus(runId);
        if (!isCancelled) {
          handleStatusUpdate(currentStatus);
        }
      } catch (err) {
        retryCount++;
        if (retryCount >= maxRetries) {
          setError('Автоматическая проверка остановлена. Проверьте статус вручную.');
        }
      }
    };

    // Initial check
    pollStatus();

    const interval = setInterval(pollStatus, 5000);

    return () => {
      isCancelled = true;
      clearInterval(interval);
    };
  }, [runId, onComplete, isBookReady]);

  const getProgress = () => {
    if (!status) return 0;
    
    if (status.stages.book_generated) return 100;
    if (status.stages.images_downloaded) return 66;
    if (status.stages.data_collected) return 33;
    return 0;
  };

  const getCurrentStep = () => {
    if (!status) return 'Подключаемся к Instagram... 🔗';
    
    if (status.stages.book_generated) return 'Ваша романтическая книга готова! ✨';
    if (status.stages.images_downloaded) return 'Создаем вашу уникальную историю любви... 💕';
    if (status.stages.data_collected) return 'Анализируем ваши фотографии и моменты... 📸';
    return 'Изучаем ваш профиль и стиль жизни... 👀';
  };

  // Проверяем готовность книги - улучшенная логика
  const hasHTMLFile = status?.files?.html || isBookReady;
  const hasPDFFile = status?.files?.pdf;
  
  console.log('Current state check:', {
    isBookReady,
    hasHTMLFile,
    isComplete,
    bookGenerated: status?.stages.book_generated,
    htmlFile: status?.files?.html,
    statusExists: !!status
  });

  const loadBookContent = async () => {
    if (!hasHTMLFile) return;
    
    setIsLoadingBook(true);
    try {
      const response = await fetch(api.getViewUrl(runId));
      if (response.ok) {
        const html = await response.text();
        setBookContent(html);
        setShowInlineViewer(true);
        toast({
          title: "📖 Книга загружена",
          description: "Теперь вы можете читать книгу прямо здесь",
        });
      } else {
        throw new Error('Не удалось загрузить книгу');
      }
    } catch (error) {
      console.error('Error loading book:', error);
      toast({
        title: "❌ Ошибка загрузки содержимого",
        description: "Попробуйте 'Встроенный просмотр' или откройте в новой вкладке",
        variant: "destructive",
      });
    } finally {
      setIsLoadingBook(false);
    }
  };

  const handleViewBook = () => {
    if (hasHTMLFile) {
      window.open(api.getViewUrl(runId), '_blank');
      toast({
        title: "📖 Открываем книгу",
        description: "Книга открывается в новой вкладке",
      });
    }
  };

  const handleViewInline = () => {
    loadBookContent();
  };

  const handleViewIframe = () => {
    setShowIframeViewer(true);
    toast({
      title: "📖 Открываем книгу",
      description: "Книга загружается в встроенном просмотрщике",
    });
  };

  const handleDownloadPDF = () => {
    if (hasPDFFile) {
      const link = document.createElement('a');
      link.href = api.getDownloadUrl(runId, 'book.pdf');
      link.download = 'romantic_book.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <>
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <div className="w-full max-w-2xl">
          <Card className="bg-white border border-gray-200">
            <CardHeader className="text-center">
              <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Loader2 className="h-8 w-8 text-gray-600 animate-spin" />
              </div>
              <CardTitle className="text-2xl text-black">✨ Создаем вашу историю любви</CardTitle>
              <CardDescription className="text-gray-600">
                Наш ИИ анализирует ваш Instagram и создает персональную романтическую книгу
              </CardDescription>
              <div className="text-xs text-gray-500 mt-2">
                ID: {runId}
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {error && (
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              <div className="text-center">
                <Button
                  onClick={checkStatusManually}
                  disabled={isManualChecking}
                  variant="outline"
                  className="h-12 px-6 border-2"
                >
                  {isManualChecking ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <RefreshCw className="h-4 w-4 mr-2" />}
                  {isManualChecking ? 'Проверяем...' : 'Проверить статус'}
                </Button>
                {lastChecked && (
                  <p className="text-xs text-muted-foreground mt-1">
                    Последняя проверка: {lastChecked.toLocaleTimeString()}
                  </p>
                )}
              </div>

              {/* Status Info */}
              {status && (
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <h4 className="font-medium mb-3 text-blue-900">✨ Что происходит сейчас:</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-blue-700">📊 Анализ профиля:</span>
                      <span className={`font-medium ${status.stages.data_collected ? 'text-green-600' : 'text-orange-600'}`}>
                        {status.stages.data_collected ? '✅ Завершен' : '⏳ В процессе'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-blue-700">📸 Сбор фотографий:</span>
                      <span className={`font-medium ${status.stages.images_downloaded ? 'text-green-600' : 'text-gray-500'}`}>
                        {status.stages.images_downloaded ? '✅ Готово' : '⏸️ Ожидание'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-blue-700">💕 Создание книги:</span>
                      <span className={`font-medium ${status.stages.book_generated ? 'text-green-600' : 'text-gray-500'}`}>
                        {status.stages.book_generated ? '✅ Готова к чтению!' : '⏸️ Ожидание'}
                      </span>
                    </div>
                    {status.files && Object.keys(status.files).length > 0 && (
                      <div className="mt-3 pt-2 border-t border-blue-200">
                        <span className="text-blue-700 text-xs">📁 Файлы: </span>
                        <span className="text-xs text-gray-600">
                          {status.files.html && '📖 HTML'} {status.files.pdf && '📄 PDF'}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Progress */}
              <div className="space-y-4">
                <ProgressBar value={status ? (Object.values(status.stages).filter(Boolean).length / 3) * 100 : 0} className="h-2" />
                <p className="text-center text-sm text-muted-foreground">
                  {status?.stages.book_generated ? 'Готово!' : status?.stages.images_downloaded ? 'Пишем вашу историю...' : status?.stages.data_collected ? 'Анализируем фото...' : 'Начинаем...'}
                </p>
              </div>

              {/* Steps indicator */}
              <div className="space-y-3">
                <div className={`flex items-center gap-3 p-3 rounded-lg ${status?.stages.data_collected ? 'bg-green-50 border border-green-200' : 'bg-gray-50'}`}>
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center ${status?.stages.data_collected ? 'bg-green-500' : 'bg-gray-300'}`}>
                    {status?.stages.data_collected ? <CheckCircle className="w-4 h-4 text-white" /> : <span className="text-xs text-white">1</span>}
                  </div>
                  <div className="flex-1">
                    <span className={`block font-medium ${status?.stages.data_collected ? 'text-green-800' : 'text-gray-600'}`}>
                      Изучаем ваш профиль 👀
                    </span>
                    <span className="text-xs text-gray-500">
                      Анализируем ваши интересы, стиль жизни и предпочтения
                    </span>
                  </div>
                </div>
                
                <div className={`flex items-center gap-3 p-3 rounded-lg ${status?.stages.images_downloaded ? 'bg-green-50 border border-green-200' : 'bg-gray-50'}`}>
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center ${status?.stages.images_downloaded ? 'bg-green-500' : 'bg-gray-300'}`}>
                    {status?.stages.images_downloaded ? <CheckCircle className="w-4 h-4 text-white" /> : <span className="text-xs text-white">2</span>}
                  </div>
                  <div className="flex-1">
                    <span className={`block font-medium ${status?.stages.images_downloaded ? 'text-green-800' : 'text-gray-600'}`}>
                      Собираем ваши моменты 📸
                    </span>
                    <span className="text-xs text-gray-500">
                      Загружаем фотографии и создаем галерею для вашей истории
                    </span>
                  </div>
                </div>
                
                <div className={`flex items-center gap-3 p-3 rounded-lg ${status?.stages.book_generated ? 'bg-green-50 border border-green-200' : 'bg-gray-50'}`}>
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center ${status?.stages.book_generated ? 'bg-green-500' : 'bg-gray-300'}`}>
                    {status?.stages.book_generated ? <CheckCircle className="w-4 h-4 text-white" /> : <span className="text-xs text-white">3</span>}
                  </div>
                  <div className="flex-1">
                    <span className={`block font-medium ${status?.stages.book_generated ? 'text-green-800' : 'text-gray-600'}`}>
                      Создаем вашу книгу любви 💕
                    </span>
                    <span className="text-xs text-gray-500">
                      Пишем романтическую историю специально для вас
                    </span>
                  </div>
                </div>
              </div>

              {/* Profile preview if available */}
              {status?.profile && (
                <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                  <h3 className="font-medium text-black mb-2">✅ Профиль найден</h3>
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">{status.profile.fullName}</span> (@{status.profile.username})
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {status.profile.followers.toLocaleString()} подписчиков • {status.profile.posts} постов
                  </p>
                </div>
              )}

              {/* Reset button */}
              <div className="text-center pt-4 border-t">
                <Button
                  onClick={onReset}
                  variant="ghost"
                  className="text-gray-500 hover:text-gray-700"
                >
                  ← Вернуться к форме
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      
      <BookReadyDialog
        isOpen={isBookReadyDialogOpen}
        onOpenChange={(isOpen) => {
          if (!isOpen) {
            setIsBookReadyDialogOpen(false);
            // Возможно, здесь вы захотите сбросить состояние
            // onReset(); 
          }
        }}
        runId={runId}
        status={status}
      />
    </>
  );
} 
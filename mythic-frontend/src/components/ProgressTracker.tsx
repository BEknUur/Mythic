import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress as ProgressBar } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { CheckCircle, Eye, Download, RotateCcw, Loader2, RefreshCw, ExternalLink, AlertTriangle } from 'lucide-react';
import { api, type StatusResponse } from '@/lib/api';

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
  const { toast } = useToast();

  const checkStatusManually = async () => {
    setIsManualChecking(true);
    try {
      console.log(`Manual status check for runId: ${runId}`);
      const currentStatus = await api.getStatus(runId);
      console.log('Received status:', currentStatus);
      console.log('Book generated stage:', currentStatus.stages.book_generated);
      console.log('Files object:', currentStatus.files);
      
      setStatus(currentStatus);
      setError('');
      setLastChecked(new Date());
      
      if (currentStatus.stages.book_generated) {
        setIsComplete(true);
        onComplete();
        toast({
          title: "💕 Ваша книга готова!",
          description: "Романтическая история создана специально для вас",
        });
      } else {
        toast({
          title: "⏳ Работаем над вашей историей",
          description: "Анализируем ваши фото и создаем уникальный сюжет",
        });
      }
    } catch (error) {
      console.error('Manual status check error:', error);
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
    const maxRetries = 3; // Уменьшил количество попыток
    
    const pollStatus = async () => {
      try {
        console.log(`Polling status for runId: ${runId}`);
        const currentStatus = await api.getStatus(runId);
        setStatus(currentStatus);
        setError('');
        retryCount = 0;
        
        if (currentStatus.stages.book_generated && !isComplete) {
          setIsComplete(true);
          onComplete();
          toast({
            title: "🎉 История любви готова!",
            description: "Ваша персональная романтическая книга создана",
          });
        }
      } catch (error) {
        retryCount++;
        console.error(`Error polling status (attempt ${retryCount}):`, error);
        
        if (retryCount >= maxRetries) {
          setError('Создание книги занимает больше времени. Используйте кнопку "Проверить статус" для обновления или попробуйте позже.');
        }
      }
    };

    pollStatus();
    
    const interval = setInterval(() => {
      if (!isComplete && retryCount < maxRetries) {
        pollStatus();
      }
    }, 5000); // Увеличил интервал до 5 секунд

    return () => clearInterval(interval);
  }, [runId, isComplete, onComplete, toast]);

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

  // Проверяем готовность книги
  const isBookReady = status?.stages.book_generated || false;
  const hasHTMLFile = status?.files?.html || isBookReady;
  const hasPDFFile = status?.files?.pdf;

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

  // Если книга готова
  if (isBookReady && status) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <div className="w-full max-w-6xl space-y-6">
          {/* Success Card */}
          <Card className="bg-white border-2 border-green-200">
            <CardHeader className="text-center">
              <div className="mx-auto w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mb-4 animate-pulse">
                <CheckCircle className="h-10 w-10 text-green-600" />
              </div>
              <CardTitle className="text-4xl text-black">🎉 Книга готова!</CardTitle>
              <CardDescription className="text-xl text-gray-600">
                Ваша романтическая книга создана и готова для просмотра
              </CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-6">
              {/* Inline Book Viewer */}
              {showInlineViewer && bookContent && (
                <div className="border-2 border-gray-200 rounded-lg overflow-hidden">
                  <div className="bg-gray-100 p-3 flex items-center justify-between border-b">
                    <h3 className="font-medium text-black">📖 Ваша романтическая книга</h3>
                    <div className="flex gap-2">
                      <Button
                        onClick={handleViewBook}
                        size="sm"
                        variant="outline"
                        className="text-xs"
                      >
                        <ExternalLink className="h-3 w-3 mr-1" />
                        Открыть в новой вкладке
                      </Button>
                      <Button
                        onClick={() => setShowInlineViewer(false)}
                        size="sm"
                        variant="ghost"
                        className="text-xs"
                      >
                        ✕ Закрыть
                      </Button>
                    </div>
                  </div>
                  <div 
                    className="book-content overflow-auto bg-white p-6"
                    dangerouslySetInnerHTML={{ __html: bookContent }}
                    style={{
                      maxHeight: '70vh',
                      minHeight: '500px',
                      scrollbarWidth: 'thin',
                      scrollbarColor: '#cbd5e1 #f1f5f9'
                    }}
                  />
                  {/* Footer controls */}
                  <div className="bg-gray-50 p-3 border-t flex justify-between items-center">
                    <span className="text-sm text-gray-600">
                      💝 Создано специально для вас
                    </span>
                    <div className="flex gap-2">
                      <Button
                        onClick={handleViewBook}
                        size="sm"
                        variant="outline"
                        className="text-xs"
                      >
                        <ExternalLink className="h-3 w-3 mr-1" />
                        Полноэкранный режим
                      </Button>
                      {hasPDFFile && (
                        <Button
                          onClick={handleDownloadPDF}
                          size="sm"
                          variant="outline"
                          className="text-xs"
                        >
                          <Download className="h-3 w-3 mr-1" />
                          PDF
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Iframe Book Viewer */}
              {showIframeViewer && (
                <div className="border-2 border-gray-200 rounded-lg overflow-hidden">
                  <div className="bg-blue-100 p-3 flex items-center justify-between border-b">
                    <h3 className="font-medium text-black">📚 Просмотр книги (встроенный)</h3>
                    <div className="flex gap-2">
                      <Button
                        onClick={handleViewBook}
                        size="sm"
                        variant="outline"
                        className="text-xs"
                      >
                        <ExternalLink className="h-3 w-3 mr-1" />
                        Открыть в новой вкладке
                      </Button>
                      <Button
                        onClick={() => setShowIframeViewer(false)}
                        size="sm"
                        variant="ghost"
                        className="text-xs"
                      >
                        ✕ Закрыть
                      </Button>
                    </div>
                  </div>
                  <iframe
                    src={api.getViewUrl(runId)}
                    className="w-full bg-white"
                    style={{
                      height: '70vh',
                      minHeight: '500px',
                      border: 'none'
                    }}
                    title="Романтическая книга"
                    sandbox="allow-same-origin allow-scripts"
                  />
                  <div className="bg-blue-50 p-3 border-t flex justify-between items-center">
                    <span className="text-sm text-blue-700">
                      💝 Если содержимое не отображается, попробуйте открыть в новой вкладке
                    </span>
                    <div className="flex gap-2">
                      <Button
                        onClick={handleViewBook}
                        size="sm"
                        className="text-xs bg-blue-600 text-white hover:bg-blue-700"
                      >
                        <ExternalLink className="h-3 w-3 mr-1" />
                        Полный экран
                      </Button>
                    </div>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {!showInlineViewer && !showIframeViewer && (
                  <>
                    <Button
                      onClick={handleViewInline}
                      size="lg"
                      disabled={!hasHTMLFile || isLoadingBook}
                      className="h-14 px-6 bg-blue-600 text-white hover:bg-blue-700 shadow-lg disabled:opacity-50"
                    >
                      {isLoadingBook ? (
                        <Loader2 className="h-5 w-5 mr-3 animate-spin" />
                      ) : (
                        <Eye className="h-5 w-5 mr-3" />
                      )}
                      {isLoadingBook ? 'Загружаем...' : 'Читать здесь'}
                    </Button>

                    <Button
                      onClick={handleViewIframe}
                      size="lg"
                      disabled={!hasHTMLFile}
                      className="h-14 px-6 bg-purple-600 text-white hover:bg-purple-700 shadow-lg disabled:opacity-50"
                    >
                      <Eye className="h-5 w-5 mr-3" />
                      Встроенный просмотр
                    </Button>
                  </>
                )}

                <Button
                  onClick={handleViewBook}
                  size="lg"
                  disabled={!hasHTMLFile}
                  variant="outline"
                  className="h-14 px-6 border-2 border-gray-300 hover:border-gray-900 hover:bg-gray-50 disabled:opacity-50"
                >
                  <ExternalLink className="h-5 w-5 mr-3" />
                  Открыть в новой вкладке
                </Button>

                {hasPDFFile && (
                  <Button
                    onClick={handleDownloadPDF}
                    variant="outline"
                    size="lg"
                    className="h-14 px-6 border-2 border-gray-300 hover:bg-gray-50 hover:border-gray-900"
                  >
                    <Download className="h-5 w-5 mr-2" />
                    Скачать PDF
                  </Button>
                )}
              </div>

              {!hasHTMLFile && (
                <Alert className="border-yellow-200 bg-yellow-50">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription className="text-yellow-700">
                    Файл книги еще не готов для просмотра
                  </AlertDescription>
                </Alert>
              )}

              {/* Viewing Options Info */}
              {hasHTMLFile && !showInlineViewer && !showIframeViewer && (
                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                  <h4 className="font-medium text-green-800 mb-2">📖 Способы просмотра книги:</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-green-700">
                    <div className="flex items-start gap-2">
                      <span className="text-blue-600">💙</span>
                      <div>
                        <span className="font-medium">Читать здесь</span> - Загружает содержимое прямо на страницу
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-purple-600">💜</span>
                      <div>
                        <span className="font-medium">Встроенный просмотр</span> - Отображает книгу во фрейме
                      </div>
                    </div>
                  </div>
                  <p className="text-xs text-green-600 mt-2">
                    💡 Если один способ не работает, попробуйте другой или откройте в новой вкладке
                  </p>
                </div>
              )}

              {/* Profile Info */}
              {status.profile && (
                <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
                  <h3 className="font-semibold text-black mb-3 text-lg">📋 Информация о профиле</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div className="bg-white p-3 rounded border">
                      <span className="text-gray-600">Пользователь:</span>
                      <div className="font-medium text-lg">@{status.profile.username}</div>
                    </div>
                    <div className="bg-white p-3 rounded border">
                      <span className="text-gray-600">Имя:</span>
                      <div className="font-medium text-lg">{status.profile.fullName}</div>
                    </div>
                    <div className="bg-white p-3 rounded border">
                      <span className="text-gray-600">Подписчики:</span>
                      <div className="font-medium text-lg">{status.profile.followers.toLocaleString()}</div>
                    </div>
                    <div className="bg-white p-3 rounded border">
                      <span className="text-gray-600">Постов:</span>
                      <div className="font-medium text-lg">{status.profile.posts}</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Additional Actions */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button
                  onClick={onReset}
                  variant="ghost"
                  className="h-12 hover:bg-gray-50"
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Создать новую книгу
                </Button>
              </div>

              {/* Book URL for sharing */}
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h4 className="font-medium text-black mb-2">Ссылка на книгу:</h4>
                <div className="flex items-center gap-2">
                  <code className="flex-1 bg-white p-2 rounded border text-sm font-mono break-all">
                    {api.getViewUrl(runId)}
                  </code>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      navigator.clipboard.writeText(api.getViewUrl(runId));
                      toast({ title: "Скопировано!", description: "Ссылка скопирована в буфер обмена" });
                    }}
                  >
                    Копировать
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // В процессе создания
  return (
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
              <Alert className="border-yellow-200 bg-yellow-50">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription className="text-yellow-700">
                  {error}
                </AlertDescription>
              </Alert>
            )}

            {/* Manual Check Button */}
            <div className="text-center">
              <Button
                onClick={checkStatusManually}
                disabled={isManualChecking}
                variant="outline"
                className="h-12 px-6 border-2 border-blue-200 hover:border-blue-400 hover:bg-blue-50"
              >
                {isManualChecking ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4 mr-2" />
                )}
                {isManualChecking ? 'Проверяем готовность...' : 'Проверить статус книги'}
              </Button>
              {lastChecked && (
                <p className="text-xs text-gray-500 mt-1">
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
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-black">Прогресс</span>
                <span className="text-sm text-gray-600">{getProgress()}%</span>
              </div>
              <ProgressBar value={getProgress()} className="h-3" />
              <p className="text-center text-base text-gray-700 font-medium">
                {getCurrentStep()}
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
  );
} 
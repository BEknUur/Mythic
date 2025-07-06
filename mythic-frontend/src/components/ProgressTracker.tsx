import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { CheckCircle, Loader2, RefreshCw, AlertTriangle, Heart, Book, Camera, User, Lock, BookOpen, Newspaper } from 'lucide-react';
import { useUser, SignInButton, UserButton, useAuth } from '@clerk/clerk-react';
import { api, type StatusResponse } from '@/lib/api';
import { BookReadyDialog } from './BookReadyDialog';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';

interface ProgressTrackerProps {
  runId: string;
  onComplete: () => void;
  onReset: () => void;
}

const ProgressBar: React.FC<{ value: number; className?: string }> = ({ value, className }) => (
  <Progress value={value} className={className} />
);

// Компонент анимации печатающейся машинки
const TypewriterText: React.FC<{ text: string; speed?: number; className?: string }> = ({ 
  text, 
  speed = 50, 
  className = "" 
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, speed);

      return () => clearTimeout(timeout);
    }
  }, [currentIndex, text, speed]);

  // Сброс анимации при изменении текста
  useEffect(() => {
    setDisplayedText('');
    setCurrentIndex(0);
  }, [text]);

  return (
    <span className={className}>
      {displayedText}
      {currentIndex < text.length && (
        <span className="animate-pulse">|</span>
      )}
    </span>
  );
};

export function ProgressTracker({ runId, onComplete, onReset }: ProgressTrackerProps) {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isManualChecking, setIsManualChecking] = useState(false);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [isBookReadyDialogOpen, setIsBookReadyDialogOpen] = useState(false);
  const [visibleSteps, setVisibleSteps] = useState<number>(0);
  const [showFormatDialog, setShowFormatDialog] = useState(false);
  const [isCreatingBook, setIsCreatingBook] = useState(false);
  const { toast } = useToast();
  const { isSignedIn, user } = useUser();
  const { getToken } = useAuth();

  const isBookReady = status?.stages.book_generated || false;

  // Если пользователь не авторизован, показываем предупреждение
  if (!isSignedIn) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <div className="w-full max-w-2xl">
          <Card className="bg-white border border-red-200">
            <CardContent className="text-center py-12">
              <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
                <Lock className="h-8 w-8 text-red-600" />
              </div>
              <h2 className="text-2xl font-semibold text-black mb-4">Доступ ограничен</h2>
              <p className="text-gray-600 mb-6">
                Для просмотра процесса создания и результата книги необходимо войти в систему
              </p>
              <div className="flex gap-3 justify-center">
                <SignInButton mode="modal">
                  <Button>
                    Войти в систему
                  </Button>
                </SignInButton>
                <Button variant="outline" onClick={onReset}>
                  Вернуться назад
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Анимация появления шагов
  useEffect(() => {
    if (status) {
      const completedSteps = Object.values(status.stages).filter(Boolean).length;
      let stepIndex = 0;
      const interval = setInterval(() => {
        if (stepIndex <= completedSteps) {
          setVisibleSteps(stepIndex);
          stepIndex++;
        } else {
          clearInterval(interval);
        }
      }, 800);
      
      return () => clearInterval(interval);
    }
  }, [status]);

  const handleStatusUpdate = (currentStatus: StatusResponse) => {
    const newStatus = { ...currentStatus };
    setStatus(newStatus);
    setLastChecked(new Date());

    // Показываем диалог выбора формата, когда фотографии загружены, но книга еще не создана
    if (newStatus.stages.images_downloaded && !newStatus.stages.book_generated && !showFormatDialog && !isCreatingBook) {
      setShowFormatDialog(true);
      return;
    }

    if (newStatus.stages.book_generated && !isBookReadyDialogOpen) {
        setIsBookReadyDialogOpen(true);
        onComplete();
    }
  };

  const checkStatusManually = async () => {
    setIsManualChecking(true);
    try {
      const token = await getToken();
      const currentStatus = await api.getStatus(runId, token || undefined);
      handleStatusUpdate(currentStatus);
    } catch (error) {
      setError('Ошибка при проверке статуса');
      toast({
        title: "Ошибка",
        description: "Не удалось проверить статус книги",
        variant: "destructive",
      });
    } finally {
      setIsManualChecking(false);
    }
  };

  const createBookWithFormat = async (format: string) => {
    setShowFormatDialog(false);
    setIsCreatingBook(true);
    
    try {
      const token = await getToken();
      await api.createBook(runId, format, token || undefined);
      
      toast({
        title: "Создание книги началось",
        description: `Создаем книгу в формате: ${format === 'classic' ? 'классическом' : format === 'magazine' ? 'журнальном' : 'зин'}`,
      });
    } catch (error) {
      console.error('Error creating book:', error);
      toast({
        title: "Ошибка",
        description: "Не удалось начать создание книги",
        variant: "destructive",
      });
      setIsCreatingBook(false);
    }
  };

  useEffect(() => {
    let retryCount = 0;
    const maxRetries = 5;
    let isCancelled = false;

    const pollStatus = async () => {
      if (isBookReady || isCancelled) return;
      try {
        const token = await getToken();
        const currentStatus = await api.getStatus(runId, token || undefined);
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

    pollStatus();
    const interval = setInterval(pollStatus, 5000);

    return () => {
      isCancelled = true;
      clearInterval(interval);
    };
  }, [runId, onComplete, isBookReady, getToken]);

  const getHumanStatus = (stageKey: string, isCompleted: boolean) => {
    const stages: Record<string, { inProgress: string; completed: string }> = {
      data_collected: {
        inProgress: 'изучаем ваш профиль',
        completed: 'профиль изучен'
      },
      images_downloaded: {
        inProgress: 'собираем ваши фотографии',
        completed: 'фотографии собраны'
      },
      book_generated: {
        inProgress: status?.style === 'fantasy' ? 'создаем эпическую сагу' :
                    status?.style === 'humor' ? 'создаем веселую книгу' :
                    'создаем вашу историю',
        completed: status?.style === 'fantasy' ? 'сага готова' :
                   status?.style === 'humor' ? 'книга готова' :
                   'книга готова'
      }
    };
    
    return isCompleted ? stages[stageKey]?.completed : stages[stageKey]?.inProgress;
  };

  const getCurrentPhrase = () => {
    if (!status) return 'начинаем работу...';
    
    // Показываем только романтические сообщения от API
    if (status.message) {
      return status.message;
    }
    
    // Простые статусы без лишних деталей
    if (status.stages.book_generated) return 'книга готова';
    if (status.stages.images_downloaded) return 'создаем книгу';
    if (status.stages.data_collected) return 'загружаем фотографии';
    return 'анализируем профиль';
  };

  return (
    <>
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <div className="w-full max-w-2xl">
          <Card className="bg-white border border-border shadow-lg">
            <CardHeader className="text-center relative">
              {/* Информация о пользователе в правом верхнем углу */}
              <div className="absolute top-4 right-4">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground font-medium">
                    {user?.firstName || 'Пользователь'}
                  </span>
                  <UserButton />
                </div>
              </div>

              {/* Минималистичная иконка */}
              <div className="mx-auto w-16 h-16 bg-gray-100 border-2 border-gray-200 rounded-full flex items-center justify-center mb-6 relative">
                {status?.stages.book_generated ? (
                  <Book className="h-8 w-8 text-gray-600" />
                ) : status?.style === 'fantasy' ? (
                  <span className="text-2xl animate-pulse">⚔️</span>
                ) : status?.style === 'humor' ? (
                  <span className="text-2xl animate-pulse">😄</span>
                ) : (
                  <Heart className="h-8 w-8 text-gray-600 animate-pulse" />
                )}
              </div>

              <CardTitle className="text-3xl font-bold text-gray-900 mb-2">
                {status?.style === 'fantasy' ? 'Создаем эпическую фэнтези-книгу' :
                 status?.style === 'humor' ? 'Создаем веселую юмористическую книгу' :
                 'Создаем вашу историю любви'}
              </CardTitle>
              <CardDescription className="text-gray-600 text-lg leading-relaxed">
                {status?.style === 'fantasy' ? 'Наш искусственный интеллект анализирует ваш Instagram и создает эпическую фэнтези-хронику о великом герое' :
                 status?.style === 'humor' ? 'Наш искусственный интеллект анализирует ваш Instagram и создает веселую юмористическую биографию' :
                 'Наш искусственный интеллект анализирует ваш Instagram и создает персональную романтическую книгу'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-8">
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
                  className="h-14 px-8 border-gray-200 hover:bg-gray-50"
                >
                  {isManualChecking ? (
                    <Loader2 className="h-5 w-5 mr-3 animate-spin text-gray-500" />
                  ) : (
                    <RefreshCw className="h-5 w-5 mr-3 text-gray-500" />
                  )}
                  {isManualChecking ? 'проверяем статус' : 'обновить статус'}
                </Button>
                {lastChecked && (
                  <p className="text-sm text-gray-400 mt-2">
                    последняя проверка: {lastChecked.toLocaleTimeString()}
                  </p>
                )}
              </div>

              {/* Живой статус */}
              {status && (
                <div className="bg-gray-50 p-8 rounded-lg border border-gray-100">
                  <h4 className="font-semibold mb-6 text-gray-800 text-lg flex items-center gap-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                    Сейчас происходит:
                  </h4>
                  
                  {/* Романтическое сообщение от API */}
                  {status.message && !status.stages.book_generated && (
                    <div className="mb-6 p-5 bg-white rounded-lg border border-gray-100 shadow-sm">
                      <p className="text-gray-700 italic text-base leading-relaxed font-medium">
                        <TypewriterText 
                          text={status.message} 
                          speed={60}
                          className="inline"
                        />
                      </p>
                    </div>
                  )}
                  
                  <div className="space-y-4 text-base">
                    <div className={`flex items-center justify-between transition-all duration-700 ${visibleSteps >= 1 ? 'opacity-100 transform translate-y-0' : 'opacity-0 transform translate-y-4'}`}>
                      <span className="text-gray-700 flex items-center gap-3 font-medium">
                        <div className="w-8 h-8 bg-gray-100 border border-gray-200 rounded-full flex items-center justify-center">
                          <User className="w-4 h-4 text-gray-500" />
                        </div>
                        анализ профиля
                      </span>
                      <span className={`font-semibold transition-colors duration-300 ${status.stages.data_collected ? 'text-gray-800' : 'text-gray-400'}`}>
                        {getHumanStatus('data_collected', status.stages.data_collected)}
                      </span>
                    </div>
                    <div className={`flex items-center justify-between transition-all duration-700 delay-300 ${visibleSteps >= 2 ? 'opacity-100 transform translate-y-0' : 'opacity-0 transform translate-y-4'}`}>
                      <span className="text-gray-700 flex items-center gap-3 font-medium">
                        <div className="w-8 h-8 bg-gray-100 border border-gray-200 rounded-full flex items-center justify-center">
                          <Camera className="w-4 h-4 text-gray-500" />
                        </div>
                        сбор фотографий
                      </span>
                      <span className={`font-semibold transition-colors duration-300 ${status.stages.images_downloaded ? 'text-gray-800' : 'text-gray-400'}`}>
                        {getHumanStatus('images_downloaded', status.stages.images_downloaded) || 'ожидание'}
                      </span>
                    </div>
                    <div className={`flex items-center justify-between transition-all duration-700 delay-600 ${visibleSteps >= 3 ? 'opacity-100 transform translate-y-0' : 'opacity-0 transform translate-y-4'}`}>
                      <span className="text-gray-700 flex items-center gap-3 font-medium">
                        <div className="w-8 h-8 bg-gray-100 border border-gray-200 rounded-full flex items-center justify-center">
                          <Book className="w-4 h-4 text-gray-500" />
                        </div>
                        создание книги
                      </span>
                      <span className={`font-semibold transition-colors duration-300 ${status.stages.book_generated ? 'text-gray-800' : 'text-gray-400'}`}>
                        {status.stages.book_generated ? 
                          getHumanStatus('book_generated', status.stages.book_generated) : 
                          isCreatingBook ? 'создаем книгу...' : 'ожидание выбора формата'}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Прогресс */}
              <div className="space-y-6">
                <ProgressBar 
                  value={status ? (Object.values(status.stages).filter(Boolean).length / 3) * 100 : 0} 
                  className="h-2"
                />
                <p className="text-center text-lg text-gray-600 italic transition-all duration-500">
                  {getCurrentPhrase()}
                </p>
              </div>

              {/* Детальные шаги - светлые */}
              <div className="grid grid-cols-3 gap-4">
                <div className={`text-center p-4 rounded-lg border transition-all duration-500 ${
                  status?.stages.data_collected 
                    ? 'bg-gray-800 text-white border-gray-800' 
                    : 'bg-gray-50 border-gray-200'
                }`}>
                  <div className={`w-10 h-10 mx-auto rounded-full flex items-center justify-center mb-2 transition-all duration-300 ${
                    status?.stages.data_collected ? 'bg-white text-gray-800' : 'bg-gray-200 text-gray-500'
                  }`}>
                    {status?.stages.data_collected ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <span className="text-sm font-bold">1</span>
                    )}
                  </div>
                  <span className={`block text-sm font-medium ${
                    status?.stages.data_collected ? 'text-white' : 'text-gray-600'
                  }`}>
                    анализ
                  </span>
                </div>
                
                <div className={`text-center p-4 rounded-lg border transition-all duration-500 ${
                  status?.stages.images_downloaded 
                    ? 'bg-gray-800 text-white border-gray-800' 
                    : 'bg-gray-50 border-gray-200'
                }`}>
                  <div className={`w-10 h-10 mx-auto rounded-full flex items-center justify-center mb-2 transition-all duration-300 ${
                    status?.stages.images_downloaded ? 'bg-white text-gray-800' : 'bg-gray-200 text-gray-500'
                  }`}>
                    {status?.stages.images_downloaded ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <span className="text-sm font-bold">2</span>
                    )}
                  </div>
                  <span className={`block text-sm font-medium ${
                    status?.stages.images_downloaded ? 'text-white' : 'text-gray-600'
                  }`}>
                    фотографии
                  </span>
                </div>
                
                <div className={`text-center p-4 rounded-lg border transition-all duration-500 ${
                  status?.stages.book_generated 
                    ? 'bg-gray-800 text-white border-gray-800' 
                    : 'bg-gray-50 border-gray-200'
                }`}>
                  <div className={`w-10 h-10 mx-auto rounded-full flex items-center justify-center mb-2 transition-all duration-300 ${
                    status?.stages.book_generated ? 'bg-white text-gray-800' : 'bg-gray-200 text-gray-500'
                  }`}>
                    {status?.stages.book_generated ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <span className="text-sm font-bold">3</span>
                    )}
                  </div>
                  <span className={`block text-sm font-medium ${
                    status?.stages.book_generated ? 'text-white' : 'text-gray-600'
                  }`}>
                    книга
                  </span>
                </div>
              </div>

              {/* Превью профиля */}
              {status?.profile && (
                <div className="bg-gray-50 p-6 rounded-lg border border-gray-100">
                  <h3 className="font-semibold text-gray-800 mb-3 text-lg flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-gray-600" />
                    профиль найден
                  </h3>
                  <p className="text-base text-gray-700 mb-1">
                    <span className="font-semibold text-gray-800">{status.profile.fullName}</span> 
                    <span className="text-gray-500 ml-2">@{status.profile.username}</span>
                  </p>
                  <p className="text-sm text-gray-500 flex items-center gap-4 flex-wrap">
                    <span className="flex items-center gap-1">
                      <User className="w-4 h-4" />
                      {status.profile.followers.toLocaleString()} подписчиков
                    </span>
                    <span className="flex items-center gap-1">
                      <Camera className="w-4 h-4" />
                      {status.profile.posts} постов
                    </span>
                    {status.profile.stories && status.profile.stories > 0 && (
                      <span className="flex items-center gap-1">
                        <span className="text-sm">📖</span>
                        {status.profile.stories} историй
                      </span>
                    )}
                  </p>
                </div>
              )}

              {/* Кнопка возврата */}
              <div className="text-center pt-6 border-t border-gray-100">
                <Button
                  onClick={onReset}
                  variant="ghost"
                  className="text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                >
                  ← вернуться к форме
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      
      {/* Диалог выбора формата книги */}
      <Dialog open={showFormatDialog} onOpenChange={setShowFormatDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-2xl text-center">
              Выберите формат книги
            </DialogTitle>
            <DialogDescription className="text-center">
              Данные собраны! Теперь выберите, в каком формате создать вашу книгу.
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            {/* Классический формат */}
            <div 
              className="border rounded-lg p-6 cursor-pointer hover:border-blue-500 transition-colors"
              onClick={() => createBookWithFormat('classic')}
            >
              <div className="flex items-center justify-center mb-4">
                <Book className="h-12 w-12 text-blue-600" />
              </div>
              <h3 className="font-semibold text-lg text-center mb-2">Классическая книга</h3>
              <p className="text-sm text-gray-600 text-center">
                Традиционный формат с главами, красивым дизайном и плавным повествованием
              </p>
            </div>
            
            {/* Журнальный формат */}
            <div 
              className="border rounded-lg p-6 cursor-pointer hover:border-purple-500 transition-colors"
              onClick={() => createBookWithFormat('magazine')}
            >
              <div className="flex items-center justify-center mb-4">
                <Newspaper className="h-12 w-12 text-purple-600" />
              </div>
              <h3 className="font-semibold text-lg text-center mb-2">Журнальный формат</h3>
              <p className="text-sm text-gray-600 text-center">
                Стильный журнальный дизайн с обложкой, оглавлением и разворотами как в модном издании
              </p>
            </div>
          </div>
          
          <div className="mt-6 text-center">
            <Button 
              variant="outline" 
              onClick={() => setShowFormatDialog(false)}
              className="mr-4"
            >
              Отмена
            </Button>
          </div>
        </DialogContent>
      </Dialog>
      
      <BookReadyDialog
        isOpen={isBookReadyDialogOpen}
        onOpenChange={(isOpen) => {
          if (!isOpen) {
            setIsBookReadyDialogOpen(false);
          }
        }}
        runId={runId}
        status={status}
      />
    </>
  );
} 
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { CheckCircle, Loader2, RefreshCw, AlertTriangle, Heart, Book, Camera, User, Lock } from 'lucide-react';
import { useUser, SignInButton, UserButton, useAuth } from '@clerk/clerk-react';
import { api, type StatusResponse } from '@/lib/api';
import { BookReadyDialog } from './BookReadyDialog';

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
        inProgress: 'создаем вашу историю',
        completed: 'книга готова'
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
              <div className="mx-auto w-16 h-16 bg-foreground rounded-full flex items-center justify-center mb-6 relative">
                {status?.stages.book_generated ? (
                  <Book className="h-8 w-8 text-background" />
                ) : (
                  <Heart className="h-8 w-8 text-background animate-pulse" />
                )}
              </div>

              <CardTitle className="text-3xl font-bold text-foreground mb-2">
                Создаем вашу историю любви
              </CardTitle>
              <CardDescription className="text-muted-foreground text-lg leading-relaxed">
                Наш искусственный интеллект анализирует ваш Instagram и создает персональную романтическую книгу
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
                  className="h-14 px-8"
                >
                  {isManualChecking ? (
                    <Loader2 className="h-5 w-5 mr-3 animate-spin" />
                  ) : (
                    <RefreshCw className="h-5 w-5 mr-3" />
                  )}
                  {isManualChecking ? 'проверяем статус' : 'обновить статус'}
                </Button>
                {lastChecked && (
                  <p className="text-sm text-muted-foreground mt-2">
                    последняя проверка: {lastChecked.toLocaleTimeString()}
                  </p>
                )}
              </div>

              {/* Живой статус */}
              {status && (
                <div className="bg-muted/50 p-8 rounded-lg border">
                  <h4 className="font-semibold mb-6 text-foreground text-lg flex items-center gap-2">
                    <div className="w-2 h-2 bg-foreground rounded-full animate-pulse"></div>
                    Сейчас происходит:
                  </h4>
                  
                  {/* Романтическое сообщение от API */}
                  {status.message && !status.stages.book_generated && (
                    <div className="mb-6 p-5 bg-background rounded-lg border shadow-sm">
                      <p className="text-foreground italic text-base leading-relaxed font-medium">
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
                      <span className="text-foreground flex items-center gap-3 font-medium">
                        <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center">
                          <User className="w-4 h-4 text-muted-foreground" />
                        </div>
                        анализ профиля
                      </span>
                      <span className={`font-semibold transition-colors duration-300 ${status.stages.data_collected ? 'text-foreground' : 'text-muted-foreground'}`}>
                        {getHumanStatus('data_collected', status.stages.data_collected)}
                      </span>
                    </div>
                    <div className={`flex items-center justify-between transition-all duration-700 delay-300 ${visibleSteps >= 2 ? 'opacity-100 transform translate-y-0' : 'opacity-0 transform translate-y-4'}`}>
                      <span className="text-foreground flex items-center gap-3 font-medium">
                        <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center">
                          <Camera className="w-4 h-4 text-muted-foreground" />
                        </div>
                        сбор фотографий
                      </span>
                      <span className={`font-semibold transition-colors duration-300 ${status.stages.images_downloaded ? 'text-foreground' : 'text-muted-foreground'}`}>
                        {getHumanStatus('images_downloaded', status.stages.images_downloaded) || 'ожидание'}
                      </span>
                    </div>
                    <div className={`flex items-center justify-between transition-all duration-700 delay-600 ${visibleSteps >= 3 ? 'opacity-100 transform translate-y-0' : 'opacity-0 transform translate-y-4'}`}>
                      <span className="text-foreground flex items-center gap-3 font-medium">
                        <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center">
                          <Book className="w-4 h-4 text-muted-foreground" />
                        </div>
                        создание книги
                      </span>
                      <span className={`font-semibold transition-colors duration-300 ${status.stages.book_generated ? 'text-foreground' : 'text-muted-foreground'}`}>
                        {getHumanStatus('book_generated', status.stages.book_generated) || 'ожидание'}
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
                <p className="text-center text-lg text-muted-foreground italic transition-all duration-500">
                  {getCurrentPhrase()}
                </p>
              </div>

              {/* Детальные шаги - минималистичные */}
              <div className="grid grid-cols-3 gap-4">
                <div className={`text-center p-4 rounded-lg border transition-all duration-500 ${
                  status?.stages.data_collected 
                    ? 'bg-foreground text-background border-foreground' 
                    : 'bg-muted/50 border-border'
                }`}>
                  <div className={`w-10 h-10 mx-auto rounded-full flex items-center justify-center mb-2 transition-all duration-300 ${
                    status?.stages.data_collected ? 'bg-background text-foreground' : 'bg-muted text-muted-foreground'
                  }`}>
                    {status?.stages.data_collected ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <span className="text-sm font-bold">1</span>
                    )}
                  </div>
                  <span className={`block text-sm font-medium ${
                    status?.stages.data_collected ? 'text-background' : 'text-muted-foreground'
                  }`}>
                    анализ
                  </span>
                </div>
                
                <div className={`text-center p-4 rounded-lg border transition-all duration-500 ${
                  status?.stages.images_downloaded 
                    ? 'bg-foreground text-background border-foreground' 
                    : 'bg-muted/50 border-border'
                }`}>
                  <div className={`w-10 h-10 mx-auto rounded-full flex items-center justify-center mb-2 transition-all duration-300 ${
                    status?.stages.images_downloaded ? 'bg-background text-foreground' : 'bg-muted text-muted-foreground'
                  }`}>
                    {status?.stages.images_downloaded ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <span className="text-sm font-bold">2</span>
                    )}
                  </div>
                  <span className={`block text-sm font-medium ${
                    status?.stages.images_downloaded ? 'text-background' : 'text-muted-foreground'
                  }`}>
                    фотографии
                  </span>
                </div>
                
                <div className={`text-center p-4 rounded-lg border transition-all duration-500 ${
                  status?.stages.book_generated 
                    ? 'bg-foreground text-background border-foreground' 
                    : 'bg-muted/50 border-border'
                }`}>
                  <div className={`w-10 h-10 mx-auto rounded-full flex items-center justify-center mb-2 transition-all duration-300 ${
                    status?.stages.book_generated ? 'bg-background text-foreground' : 'bg-muted text-muted-foreground'
                  }`}>
                    {status?.stages.book_generated ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <span className="text-sm font-bold">3</span>
                    )}
                  </div>
                  <span className={`block text-sm font-medium ${
                    status?.stages.book_generated ? 'text-background' : 'text-muted-foreground'
                  }`}>
                    книга
                  </span>
                </div>
              </div>

              {/* Превью профиля */}
              {status?.profile && (
                <div className="bg-muted/30 p-6 rounded-lg border">
                  <h3 className="font-semibold text-foreground mb-3 text-lg flex items-center gap-2">
                    <CheckCircle className="w-5 h-5" />
                    профиль найден
                  </h3>
                  <p className="text-base text-foreground mb-1">
                    <span className="font-semibold">{status.profile.fullName}</span> 
                    <span className="text-muted-foreground ml-2">@{status.profile.username}</span>
                  </p>
                  <p className="text-sm text-muted-foreground flex items-center gap-4">
                    <span className="flex items-center gap-1">
                      <User className="w-4 h-4" />
                      {status.profile.followers.toLocaleString()} подписчиков
                    </span>
                    <span className="flex items-center gap-1">
                      <Camera className="w-4 h-4" />
                      {status.profile.posts} постов
                    </span>
                  </p>
                </div>
              )}

              {/* Кнопка возврата */}
              <div className="text-center pt-6 border-t">
                <Button
                  onClick={onReset}
                  variant="ghost"
                  className="text-muted-foreground hover:text-foreground"
                >
                  ← вернуться к форме
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
          }
        }}
        runId={runId}
        status={status}
      />
    </>
  );
} 
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
    if (!status) return 'начинаем работу над вашей историей';
    
    // Используем романтические сообщения от API
    if (status.message) {
      return status.message;
    }
    
    // Fallback к статичным сообщениям
    if (status.stages.book_generated) return 'ваша романтическая книга готова';
    if (status.stages.images_downloaded) return 'пишем вашу уникальную историю';
    if (status.stages.data_collected) return 'анализируем ваши лучшие моменты';
    return 'знакомимся с вашим профилем';
  };

  return (
    <>
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <div className="w-full max-w-2xl">
          <Card className="bg-white border border-gray-200">
            <CardHeader className="text-center">
              {/* Информация о пользователе в правом верхнем углу */}
              <div className="absolute top-4 right-4">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">
                    {user?.firstName || 'Пользователь'}
                  </span>
                  <UserButton />
                </div>
              </div>

              <div className="mx-auto w-16 h-16 bg-gradient-to-br from-pink-100 to-purple-100 rounded-full flex items-center justify-center mb-4">
                {status?.stages.book_generated ? (
                  <Book className="h-8 w-8 text-purple-600" />
                ) : (
                  <Heart className="h-8 w-8 text-pink-600 animate-pulse" />
                )}
              </div>
              <CardTitle className="text-2xl text-black">Создаем вашу историю любви</CardTitle>
              <CardDescription className="text-gray-600">
                Наш искусственный интеллект анализирует ваш Instagram и создает персональную романтическую книгу
              </CardDescription>
              <div className="text-xs text-gray-500 mt-2">
                Номер заказа: {runId}
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
                  {isManualChecking ? 'проверяем статус' : 'обновить статус'}
                </Button>
                {lastChecked && (
                  <p className="text-xs text-muted-foreground mt-1">
                    последняя проверка: {lastChecked.toLocaleTimeString()}
                  </p>
                )}
              </div>

              {/* Живой статус */}
              {status && (
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-xl border border-blue-200 transition-all duration-500">
                  <h4 className="font-medium mb-4 text-blue-900">Сейчас происходит:</h4>
                  
                  {/* Романтическое сообщение от API */}
                  {status.message && !status.stages.book_generated && (
                    <div className="mb-4 p-3 bg-white rounded-lg border border-pink-200 shadow-sm">
                      <p className="text-pink-700 italic text-sm leading-relaxed">
                        {status.message}
                      </p>
                    </div>
                  )}
                  
                  <div className="space-y-3 text-sm">
                    <div className={`flex items-center justify-between transition-all duration-700 ${visibleSteps >= 1 ? 'opacity-100 transform translate-y-0' : 'opacity-0 transform translate-y-4'}`}>
                      <span className="text-blue-700 flex items-center gap-2">
                        <User className="w-4 h-4" />
                        анализ профиля
                      </span>
                      <span className={`font-medium transition-colors duration-300 ${status.stages.data_collected ? 'text-green-600' : 'text-orange-600'}`}>
                        {getHumanStatus('data_collected', status.stages.data_collected)}
                      </span>
                    </div>
                    <div className={`flex items-center justify-between transition-all duration-700 delay-300 ${visibleSteps >= 2 ? 'opacity-100 transform translate-y-0' : 'opacity-0 transform translate-y-4'}`}>
                      <span className="text-blue-700 flex items-center gap-2">
                        <Camera className="w-4 h-4" />
                        сбор фотографий
                      </span>
                      <span className={`font-medium transition-colors duration-300 ${status.stages.images_downloaded ? 'text-green-600' : 'text-gray-500'}`}>
                        {getHumanStatus('images_downloaded', status.stages.images_downloaded) || 'ожидание'}
                      </span>
                    </div>
                    <div className={`flex items-center justify-between transition-all duration-700 delay-600 ${visibleSteps >= 3 ? 'opacity-100 transform translate-y-0' : 'opacity-0 transform translate-y-4'}`}>
                      <span className="text-blue-700 flex items-center gap-2">
                        <Book className="w-4 h-4" />
                        создание книги
                      </span>
                      <span className={`font-medium transition-colors duration-300 ${status.stages.book_generated ? 'text-green-600' : 'text-gray-500'}`}>
                        {getHumanStatus('book_generated', status.stages.book_generated) || 'ожидание'}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Прогресс */}
              <div className="space-y-4">
                <ProgressBar value={status ? (Object.values(status.stages).filter(Boolean).length / 3) * 100 : 0} className="h-3" />
                <p className="text-center text-sm text-muted-foreground italic transition-all duration-500">
                  {getCurrentPhrase()}
                </p>
              </div>

              {/* Детальные шаги */}
              <div className="space-y-3">
                <div className={`flex items-center gap-3 p-4 rounded-xl transition-all duration-500 ${
                  status?.stages.data_collected 
                    ? 'bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 shadow-sm' 
                    : 'bg-gray-50 border border-gray-200'
                }`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 ${
                    status?.stages.data_collected ? 'bg-green-500 scale-110' : 'bg-gray-300'
                  }`}>
                    {status?.stages.data_collected ? (
                      <CheckCircle className="w-5 h-5 text-white" />
                    ) : (
                      <span className="text-xs text-white font-medium">1</span>
                    )}
                  </div>
                  <div className="flex-1">
                    <span className={`block font-medium transition-colors duration-300 ${
                      status?.stages.data_collected ? 'text-green-800' : 'text-gray-600'
                    }`}>
                      изучаем ваш профиль
                    </span>
                    <span className="text-xs text-gray-500">
                      анализируем ваши интересы, стиль жизни и уникальные особенности
                    </span>
                  </div>
                </div>
                
                <div className={`flex items-center gap-3 p-4 rounded-xl transition-all duration-500 ${
                  status?.stages.images_downloaded 
                    ? 'bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 shadow-sm' 
                    : 'bg-gray-50 border border-gray-200'
                }`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 ${
                    status?.stages.images_downloaded ? 'bg-green-500 scale-110' : 'bg-gray-300'
                  }`}>
                    {status?.stages.images_downloaded ? (
                      <CheckCircle className="w-5 h-5 text-white" />
                    ) : (
                      <span className="text-xs text-white font-medium">2</span>
                    )}
                  </div>
                  <div className="flex-1">
                    <span className={`block font-medium transition-colors duration-300 ${
                      status?.stages.images_downloaded ? 'text-green-800' : 'text-gray-600'
                    }`}>
                      собираем ваши лучшие моменты
                    </span>
                    <span className="text-xs text-gray-500">
                      загружаем фотографии и создаем галерею для вашей персональной истории
                    </span>
                  </div>
                </div>
                
                <div className={`flex items-center gap-3 p-4 rounded-xl transition-all duration-500 ${
                  status?.stages.book_generated 
                    ? 'bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 shadow-sm' 
                    : 'bg-gray-50 border border-gray-200'
                }`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 ${
                    status?.stages.book_generated ? 'bg-green-500 scale-110' : 'bg-gray-300'
                  }`}>
                    {status?.stages.book_generated ? (
                      <CheckCircle className="w-5 h-5 text-white" />
                    ) : (
                      <span className="text-xs text-white font-medium">3</span>
                    )}
                  </div>
                  <div className="flex-1">
                    <span className={`block font-medium transition-colors duration-300 ${
                      status?.stages.book_generated ? 'text-green-800' : 'text-gray-600'
                    }`}>
                      создаем вашу книгу любви
                    </span>
                    <span className="text-xs text-gray-500">
                      пишем романтическую историю специально для вас
                    </span>
                  </div>
                </div>
              </div>

              {/* Превью профиля */}
              {status?.profile && (
                <div className="bg-gradient-to-r from-gray-50 to-blue-50 p-4 rounded-xl border border-gray-200 transition-all duration-500">
                  <h3 className="font-medium text-black mb-2">профиль найден</h3>
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">{status.profile.fullName}</span> (@{status.profile.username})
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {status.profile.followers.toLocaleString()} подписчиков • {status.profile.posts} постов
                  </p>
                </div>
              )}

              {/* Кнопка возврата */}
              <div className="text-center pt-4 border-t border-gray-100">
                <Button
                  onClick={onReset}
                  variant="ghost"
                  className="text-gray-500 hover:text-gray-700 transition-colors duration-200"
                >
                  вернуться к форме
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
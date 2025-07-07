import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { CheckCircle, Loader2, RefreshCw, AlertTriangle, Heart, Book, Camera, User, Lock, BookOpen, Newspaper, X, ArrowLeft } from 'lucide-react';
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
import { motion } from 'framer-motion';

interface ProgressTrackerProps {
  runId: string;
  onComplete: () => void;
  onReset: () => void;
}

const steps = [
  { id: 'analysis', name: 'Анализ' },
  { id: 'photos', name: 'Фотографии' },
  { id: 'book', name: 'Книга' },
];

const stageMessages: Record<string, string[]> = {
  initial: ["Начинаем магический ритуал..."],
  analysis: [
    "Анализируем ваш профиль, ищем скрытые сокровища...",
    "Наши алгоритмы-гномы копаются в данных...",
    "Составляем карту вашей уникальной истории...",
    "Изучаем ваш стиль, чтобы книга была идеальной...",
  ],
  photos: [
    "Собираем самые яркие моменты вашей жизни...",
    "Каждая фотография - это глава вашей будущей книги...",
    "Наши цифровые художники обрабатывают изображения...",
    "Создаем визуальную палитру вашей истории...",
  ],
  book: [
    "Сплетаем слова и образы в единое повествование...",
    "Магия уже близко, последние штрихи...",
    "Ваша книга почти готова к выходу в свет...",
    "Переплетаем страницы вашей эпической саги...",
  ],
  ready: ["Ваша эпическая сага готова! Отправляйтесь в магическое приключение."]
};

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
  const [isBookReadyDialogOpen, setIsBookReadyDialogOpen] = useState(false);
  const [showFormatDialog, setShowFormatDialog] = useState(false);
  const [isCreatingBook, setIsCreatingBook] = useState(false);
  const [currentMessage, setCurrentMessage] = useState(stageMessages.initial[0]);
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

  const getCurrentStageKey = () => {
    if (!status) return 'initial';
    if (status.stages.book_generated) return 'ready';
    if (isCreatingBook) return 'book';
    if (status.stages.images_downloaded) return 'book';
    if (status.stages.data_collected) return 'photos';
    return 'analysis';
  };

  useEffect(() => {
    const stageKey = getCurrentStageKey();
    const messages = stageMessages[stageKey];
    const messageInterval = setInterval(() => {
      const randomIndex = Math.floor(Math.random() * messages.length);
      setCurrentMessage(status?.message || messages[randomIndex]);
    }, 4500);
      
    return () => clearInterval(messageInterval);
  }, [status, isCreatingBook]);

  const handleStatusUpdate = (newStatus: StatusResponse) => {
    setStatus(newStatus);

    const apiMessage = newStatus.message;
    const stageKey = getCurrentStageKey();
    const messages = stageMessages[stageKey];
    const randomIndex = Math.floor(Math.random() * messages.length);
    setCurrentMessage(apiMessage || messages[randomIndex]);

    if (newStatus.stages.images_downloaded && !newStatus.stages.book_generated && !showFormatDialog && !isCreatingBook) {
      setShowFormatDialog(true);
    }

    if (newStatus.stages.book_generated && !isBookReadyDialogOpen) {
        setIsBookReadyDialogOpen(true);
        onComplete();
    }
  };

  const createBookWithFormat = async (format: 'classic' | 'magazine') => {
    setShowFormatDialog(false);
    setIsCreatingBook(true);
    toast({
      title: "Отличный выбор!",
      description: `Начинаем создание вашей книги в ${format === 'classic' ? 'классическом' : 'журнальном'} формате.`,
    });
    try {
      const token = await getToken();
      await api.createBook(runId, format, token || undefined);
    } catch (error) {
      console.error('Error creating book:', error);
      toast({
        title: "Ошибка",
        description: "Не удалось начать создание книги.",
        variant: "destructive",
      });
      setIsCreatingBook(false);
      setShowFormatDialog(true);
    }
  };

  useEffect(() => {
    let isCancelled = false;

    const pollStatus = async () => {
      if (isCancelled || showFormatDialog || isCreatingBook || (status?.stages.book_generated ?? false)) return;
      
      try {
        const token = await getToken();
        const currentStatus = await api.getStatus(runId, token || undefined);
        if (!isCancelled) {
          handleStatusUpdate(currentStatus);
        }
      } catch (err) {
        console.error("Polling error:", err);
        setError('Не удалось обновить статус. Обновите страницу через несколько минут.');
      }
    };

    pollStatus();
    const intervalId = setInterval(pollStatus, 7000);

    return () => {
      isCancelled = true;
      clearInterval(intervalId);
    };
  }, [runId, onComplete, status, showFormatDialog, isCreatingBook, getToken]);

  const progressValue = status ? (Object.values(status.stages).filter(Boolean).length / Object.keys(status.stages).length) * 100 : 0;
  
  const bookStyle = status?.style === 'fantasy' ? 'эпическую фэнтези-книгу' : 
                   status?.style === 'humor' ? 'уморительную комедию' : 
                   'уникальную историю';

  const getCurrentStepIndex = () => {
    if (!status) return 0;
    if (status.stages.book_generated) return 2;
    if (status.stages.images_downloaded) return 2; // On book generation
    if (status.stages.data_collected) return 1;
    return 0;
  };
  const currentStepIndex = getCurrentStepIndex();

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-950 p-4">
        <div className="w-full max-w-2xl">
        <header className="flex justify-end mb-8">
          <UserButton afterSignOutUrl="/" />
        </header>

        <Card className="w-full bg-white dark:bg-gray-900 shadow-xl rounded-2xl border-gray-100 dark:border-gray-800">
          <CardHeader className="text-center items-center pt-8">
            <div className="w-16 h-16 rounded-full border-2 border-dashed border-gray-300 dark:border-gray-700 flex items-center justify-center mb-4">
              <Book className="w-8 h-8 text-gray-400 dark:text-gray-500" />
              </div>
            <CardTitle className="text-3xl font-bold text-gray-900 dark:text-gray-50">Создаем {bookStyle}</CardTitle>
            <CardDescription className="text-lg text-gray-500 dark:text-gray-400 mt-2">
              Наш искусственный интеллект анализирует ваш Instagram и создает {bookStyle}-хронику о великом герое.
              </CardDescription>
            </CardHeader>
          <CardContent className="px-8 pb-8">
            <div className="bg-gray-100 dark:bg-gray-800/50 rounded-lg p-4 text-center my-8">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Сейчас происходит:</p>
              <p className="font-medium text-gray-800 dark:text-gray-200 h-10 flex items-center justify-center">
                <motion.span
                  key={currentMessage}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                >
                  {currentMessage}
                </motion.span>
                </p>
              </div>

            <Progress value={progressValue} className="mb-2 h-2" />
            <p className="text-center text-sm text-gray-500 dark:text-gray-400 mb-8">{currentMessage}</p>
            
            <div className="flex justify-between items-center">
              {steps.map((step, index) => (
                <div key={step.id} className="flex flex-col items-center">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${
                      index <= currentStepIndex
                        ? 'bg-purple-600 border-purple-600 text-white'
                        : 'bg-gray-100 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-400'
                    } transition-colors duration-500`}
                  >
                    {index < currentStepIndex ? <CheckCircle className="w-5 h-5" /> : index + 1}
                  </div>
                  <p className={`mt-2 text-sm font-medium ${
                      index <= currentStepIndex ? 'text-gray-800 dark:text-gray-200' : 'text-gray-400'
                    } transition-colors duration-500`}
                  >
                    {step.name}
                  </p>
                </div>
              ))}
            </div>

            <div className="mt-12 text-center border-t border-gray-100 dark:border-gray-800 pt-6">
              <Button onClick={onReset} variant="ghost" className="text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Вернуться и создать новую книгу
                </Button>
              </div>
            </CardContent>
          </Card>
      </div>
      
      {/* Format Selection Dialog */}
      {showFormatDialog && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl w-full max-w-2xl m-4"
          >
            <div className="p-8 text-center">
              <div className="flex justify-end">
                <Button variant="ghost" size="icon" onClick={() => setShowFormatDialog(false)} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
                  <X className="w-5 h-5" />
                </Button>
              </div>
              <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-50 mb-2">Выберите формат книги</h2>
              <p className="text-gray-500 dark:text-gray-400 mb-8">Данные собраны! Теперь выберите, в каком формате создать вашу книгу.</p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <button
                  onClick={() => createBookWithFormat('classic')}
                  className="p-6 border-2 border-gray-200 dark:border-gray-700 rounded-xl text-left hover:border-purple-500 hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-all duration-300"
                >
                  <Book className="w-8 h-8 text-purple-600 mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">Классическая книга</h3>
                  <p className="text-gray-500 dark:text-gray-400">Традиционный формат с главами, красивым дизайном и плавным повествованием.</p>
                </button>
                <button
              onClick={() => createBookWithFormat('magazine')}
                  className="p-6 border-2 border-gray-200 dark:border-gray-700 rounded-xl text-left hover:border-purple-500 hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-all duration-300"
                >
                  <Newspaper className="w-8 h-8 text-purple-600 mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">Журнальный формат</h3>
                  <p className="text-gray-500 dark:text-gray-400">Стильный журнальный дизайн с обложкой, оглавлением и разворотами как в модном издании.</p>
                </button>
              </div>
              <div className="mt-8">
                <Button variant="ghost" onClick={() => setShowFormatDialog(false)} className="text-gray-500 dark:text-gray-400">Отмена</Button>
              </div>
            </div>
          </motion.div>
          </div>
      )}

      {isBookReadyDialogOpen && status && (
      <BookReadyDialog
        isOpen={isBookReadyDialogOpen}
          onOpenChange={(isOpen) => !isOpen && setIsBookReadyDialogOpen(false)}
        runId={runId}
        status={status}
      />
      )}
    </div>
  );
} 
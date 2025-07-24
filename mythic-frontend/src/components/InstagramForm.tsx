import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';
import { 
  Heart, 
  Instagram, 
  Sparkles, 
  CheckCircle, 
  AlertCircle, 
  Loader2,
  BookOpen,
  Camera,
  Palette,
  Zap,
  Lock,
  Crown
} from 'lucide-react';
import { api } from '@/lib/api';
import { StylePicker, STYLES } from './StylePicker';
import { useAuth, useUser, SignInButton } from '@clerk/clerk-react';

interface InstagramFormProps {
  onScrapeStart: (runId: string) => void;
}

export function InstagramForm({ onScrapeStart }: InstagramFormProps) {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isCheckingConnection, setIsCheckingConnection] = useState(false);
  const [style, setStyle] = useState<string>('romantic');
  const { toast } = useToast();
  const { getToken } = useAuth();
  const { isSignedIn } = useUser();

  const validateInstagramUrl = (url: string): boolean => {
    const instagramUrlPattern = /^https?:\/\/(www\.)?instagram\.com\/[a-zA-Z0-9_.]+\/?$/;
    return instagramUrlPattern.test(url);
  };

  // Функция для извлечения username из URL
  const extractUsername = (url: string): string => {
    const urlMatch = url.match(/^https?:\/\/(www\.)?instagram\.com\/([a-zA-Z0-9_.]+)\/?$/);
    if (urlMatch) {
      return urlMatch[2];
    }
    return 'unknown'; // Fallback если не удалось извлечь
  };

  const checkConnection = async () => {
    setIsCheckingConnection(true);
    try {
      await api.healthCheck();
      setIsConnected(true);
      setError('');
      toast({
        title: "✅ Соединение установлено",
        description: "Сервер готов к работе",
      });
    } catch (error) {
      setIsConnected(false);
      setError('Не удается подключиться к серверу. Проверьте, что сервер запущен на localhost:8000');
      toast({
        title: "❌ Ошибка соединения",
        description: "Не удается подключиться к серверу",
        variant: "destructive",
      });
    } finally {
      setIsCheckingConnection(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url.trim()) {
      setError('Пожалуйста, введите ссылку на Instagram профиль');
      return;
    }

    if (!validateInstagramUrl(url)) {
      setError('Пожалуйста, введите корректную ссылку на Instagram профиль (например: https://instagram.com/username)');
      return;
    }

    if (!isConnected) {
      setError('Сначала проверьте соединение с сервером');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const token = await getToken?.();
      const extractedUsername = extractUsername(url);
      const result = await api.startScrape(url, extractedUsername, style, token || undefined);
      toast({
        title: "🚀 Начинаем создание книги!",
        description: isSignedIn 
          ? `Ваш запрос принят, создаем "${STYLES.find(s=>s.value===style)?.label}" книгу`
          : `Книга создается! Вы сможете просмотреть первые 10 страниц бесплатно.`,
      });
      onScrapeStart(result.runId);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Неизвестная ошибка';
      setError(`Ошибка при запуске: ${errorMessage}`);
      toast({
        title: "❌ Ошибка",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const features = [
    { 
      icon: Camera, 
      title: "Анализ фото", 
      description: "Собираем красивые фотографии из профиля",
      isPremium: false
    },
    { 
      icon: Palette, 
      title: "ИИ генерация", 
      description: "Создаем романтическую историю с помощью ИИ",
      isPremium: false
    },
    { 
      icon: BookOpen, 
      title: "Полная книга", 
      description: "Доступ ко всем страницам + сохранение",
      isPremium: true
    },
  ];

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-rose-50 via-pink-50 to-purple-50">
      <div className="w-full max-w-4xl space-y-8">
        {/* Hero Section */}
        <div className="text-center space-y-6">
          <div className="flex justify-center">
            <div className="relative">
              <div className="bg-gradient-to-r from-pink-500 to-purple-600 p-4 rounded-full">
                <Heart className="h-16 w-16 text-white" />
              </div>
              <div className="absolute -top-2 -right-2">
                <Sparkles className="h-8 w-8 text-yellow-500 animate-bounce" />
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-pink-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent" style={{ fontFamily: 'Dancing Script, cursive' }}>
              Создайте Романтическую Книгу
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Превратите Instagram профиль в прекрасную романтическую книгу с помощью искусственного интеллекта
            </p>
            {!isSignedIn && (
              <p className="text-lg text-blue-600 font-medium">
                📖 Попробуйте бесплатно - просмотрите первые 10 страниц!
              </p>
            )}
          </div>

          <div className="flex justify-center gap-2">
            <Badge variant="secondary" className="px-3 py-1">
              <Instagram className="h-3 w-3 mr-1" />
              Instagram
            </Badge>
            <Badge variant="secondary" className="px-3 py-1">
              <Zap className="h-3 w-3 mr-1" />
              ИИ генерация
            </Badge>
            <Badge variant="secondary" className="px-3 py-1">
              <BookOpen className="h-3 w-3 mr-1" />
              HTML книга
            </Badge>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-6">
          {features.map((feature, index) => {
            const IconComponent = feature.icon;
            return (
              <Card key={index} className={`border-0 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02] ${
                feature.isPremium && !isSignedIn 
                  ? 'bg-gradient-to-br from-amber-50 to-orange-50 border-2 border-amber-200' 
                  : 'bg-white/60 backdrop-blur-sm'
              }`}>
                <CardContent className="p-6 text-center space-y-4">
                  <div className="flex justify-center relative">
                    <div className={`p-3 rounded-full ${
                      feature.isPremium && !isSignedIn
                        ? 'bg-gradient-to-r from-amber-500 to-orange-600'
                        : 'bg-gradient-to-r from-pink-500 to-purple-600'
                    }`}>
                      <IconComponent className="h-6 w-6 text-white" />
                    </div>
                    {feature.isPremium && !isSignedIn && (
                      <Crown className="h-4 w-4 text-amber-600 absolute -top-1 -right-1" />
                    )}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800 flex items-center justify-center gap-2">
                      {feature.title}
                      {feature.isPremium && !isSignedIn && (
                        <Lock className="h-4 w-4 text-amber-600" />
                      )}
                    </h3>
                    <p className="text-sm text-gray-600">{feature.description}</p>
                    {feature.isPremium && !isSignedIn && (
                      <p className="text-xs text-amber-700 font-medium mt-2">Требует авторизацию</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Main Form */}
        <Card className="shadow-2xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="text-center space-y-4">
            <CardTitle className="text-2xl bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
              Начните создание книги
            </CardTitle>
            <CardDescription className="text-lg">
              {isSignedIn 
                ? "Введите ссылку на Instagram профиль для создания полной романтической книги"
                : "Введите ссылку на Instagram профиль и попробуйте бесплатно первые 10 страниц"}
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-6">
            {/* Connection Status */}
            <div className="flex justify-center">
              <Button
                onClick={checkConnection}
                disabled={isCheckingConnection}
                variant={isConnected ? "default" : "outline"}
                className={`h-12 px-6 ${isConnected 
                  ? 'bg-green-500 hover:bg-green-600 text-white' 
                  : 'border-2 border-gray-300 hover:border-pink-400'
                } transition-all duration-300`}
              >
                {isCheckingConnection ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : isConnected ? (
                  <CheckCircle className="h-4 w-4 mr-2" />
                ) : (
                  <AlertCircle className="h-4 w-4 mr-2" />
                )}
                {isCheckingConnection 
                  ? 'Проверяем соединение...' 
                  : isConnected 
                  ? 'Соединение установлено' 
                  : 'Проверить соединение'
                }
              </Button>
            </div>

            <Separator />

            {/* Preview Mode Banner for Non-Authenticated Users */}
            {!isSignedIn && (
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <Lock className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div className="flex-1">
                    <h4 className="font-semibold text-blue-900">Режим предварительного просмотра</h4>
                    <p className="text-sm text-blue-700 mt-1">
                      Вы можете создать книгу и просмотреть первые 10 страниц бесплатно. 
                      Для полного доступа ко всем страницам и возможности сохранения требуется авторизация.
                    </p>
                    <div className="mt-3">
                      <SignInButton mode="modal">
                        <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white">
                          Войти для полного доступа
                        </Button>
                      </SignInButton>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-3">
                <Label htmlFor="instagram-url" className="text-base font-medium text-gray-700">
                  Ссылка на Instagram профиль
                </Label>
                <div className="relative">
                  <Instagram className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input
                    id="instagram-url"
                    type="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://instagram.com/username"
                    className="pl-12 h-14 text-lg border-2 border-gray-200 focus:border-pink-400 focus:ring-pink-400 rounded-xl"
                    disabled={isLoading}
                  />
                </div>
                <p className="text-sm text-gray-500">
                  Например: https://instagram.com/username или https://www.instagram.com/username
                </p>
              </div>

              {/* Style Picker */}
              <div className="space-y-2">
                <Label htmlFor="style-picker" className="text-sm font-medium text-black">
                  Стиль книги
                </Label>
                <StylePicker value={style} onChange={setStyle} />
              </div>

              {error && (
                <Alert className="border-red-200 bg-red-50">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription className="text-red-700">
                    {error}
                  </AlertDescription>
                </Alert>
              )}

              <Button
                type="submit"
                disabled={isLoading || !isConnected || !url.trim()}
                className="w-full h-14 text-lg font-semibold bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 text-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    Создаем книгу...
                  </>
                ) : (
                  <>
                    <Heart className="h-5 w-5 mr-2" />
                    {isSignedIn ? 'Создать романтическую книгу' : 'Попробовать бесплатно (10 страниц)'}
                  </>
                )}
              </Button>
            </form>

            {/* Help Text */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-xl border border-blue-200">
              <h3 className="font-semibold text-gray-800 mb-2">💡 Как это работает:</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Мы анализируем открытый Instagram профиль</li>
                <li>• Собираем красивые фотографии и информацию</li>
                <li>• ИИ создает романтическую историю на основе контента</li>
                <li>• Генерируем красивую HTML книгу для просмотра</li>
                {!isSignedIn && (
                  <li className="text-blue-700 font-medium">• 📖 Без авторизации: доступ к первым 10 страницам</li>
                )}
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 
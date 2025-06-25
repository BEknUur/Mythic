import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { Instagram, CheckCircle, AlertCircle, Loader2, Lock } from 'lucide-react';
import { useUser, SignInButton, useAuth } from '@clerk/clerk-react';
import { api } from '@/lib/api';

interface FormProps {
  onStartScrape: (runId: string) => void;
}

export function Form({ onStartScrape }: FormProps) {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isCheckingConnection, setIsCheckingConnection] = useState(false);
  const { toast } = useToast();
  const { isSignedIn } = useUser();
  const { getToken } = useAuth();

  const validateInstagramUrl = (url: string): boolean => {
    const pattern = /^https?:\/\/(www\.)?instagram\.com\/[a-zA-Z0-9_.]+\/?$/;
    return pattern.test(url);
  };

  const checkConnection = async () => {
    setIsCheckingConnection(true);
    try {
      await api.healthCheck();
      setIsConnected(true);
      setError('');
      toast({
        title: "Соединение установлено",
        description: "Сервер готов к работе",
      });
    } catch (error) {
      setIsConnected(false);
      setError('Не удается подключиться к серверу');
      toast({
        title: "Ошибка соединения",
        description: "Проверьте, что сервер запущен на localhost:8000",
        variant: "destructive",
      });
    } finally {
      setIsCheckingConnection(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isSignedIn) {
      setError('Для создания книги необходимо войти в систему');
      return;
    }
    
    if (!url.trim()) {
      setError('Введите ссылку на Instagram профиль');
      return;
    }

    if (!validateInstagramUrl(url)) {
      setError('Введите корректную ссылку на Instagram профиль');
      return;
    }

    if (!isConnected) {
      setError('Сначала проверьте соединение с сервером');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const token = await getToken();
      const result = await api.startScrape(url, token || undefined);
      toast({
        title: "Начинаем создание книги",
        description: "Ваш запрос принят в обработку",
      });
      onStartScrape(result.runId);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Неизвестная ошибка';
      setError(errorMessage);
      toast({
        title: "Ошибка",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="py-16 px-4">
      <div className="max-w-2xl mx-auto">
        <Card className="bg-white border border-gray-200">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-black">Начните создание книги</CardTitle>
            <CardDescription className="text-gray-600">
              Введите ссылку на Instagram профиль для создания романтической книги
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-6">
            {/* Authentication Check */}
            {!isSignedIn && (
              <Alert className="border-orange-200 bg-orange-50">
                <Lock className="h-4 w-4 text-orange-600" />
                <AlertDescription className="text-orange-700">
                  Для создания книги необходимо войти в систему. 
                  <SignInButton mode="modal">
                    <Button variant="link" className="p-0 h-auto text-orange-700 underline">
                      Войти сейчас
                    </Button>
                  </SignInButton>
                </AlertDescription>
              </Alert>
            )}

            {/* Connection Status */}
            {isConnected && (
              <Alert className="border-green-200 bg-green-50">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-700">
                  Соединение установлено
                </AlertDescription>
              </Alert>
            )}

            {!isConnected && (
              <div className="text-center">
                <Button
                  onClick={checkConnection}
                  disabled={isCheckingConnection}
                  variant="outline"
                  className="border-gray-300 hover:bg-gray-50 hover:border-gray-900"
                >
                  {isCheckingConnection ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <AlertCircle className="h-4 w-4 mr-2" />
                  )}
                  {isCheckingConnection ? 'Проверяем соединение...' : 'Проверить соединение'}
                </Button>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="instagram-url" className="text-sm font-medium text-black">
                  Ссылка на Instagram профиль
                </Label>
                <div className="relative">
                  <Instagram className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="instagram-url"
                    type="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://instagram.com/username"
                    className="pl-10 border-gray-300 focus:border-gray-900 focus:ring-gray-900"
                    disabled={isLoading || !isSignedIn}
                  />
                </div>
              </div>

              {error && (
                <Alert variant="destructive" className="border-red-200 bg-red-50">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription className="text-red-700">
                    {error}
                  </AlertDescription>
                </Alert>
              )}

              <Button
                type="submit"
                disabled={isLoading || !isConnected || !url.trim() || !isSignedIn}
                className="w-full bg-black text-white hover:bg-gray-800 disabled:opacity-50"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Создаем книгу...
                  </>
                ) : !isSignedIn ? (
                  <>
                    <Lock className="h-4 w-4 mr-2" />
                    Войдите для создания книги
                  </>
                ) : (
                  'Создать книгу'
                )}
              </Button>
            </form>

            {/* How it works */}
            <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <h3 className="font-medium text-black mb-2">Как это работает</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Анализируем открытый Instagram профиль</li>
                <li>• Собираем фотографии и информацию</li>
                <li>• ИИ создает романтическую историю</li>
                <li>• Генерируем HTML книгу для просмотра</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
} 
import  { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { Badge } from '@/components/ui/badge';
import { 
  Book, 
  Download, 
  Trash2, 
  Eye, 
  Calendar, 
  User, 
  Loader2,
  ArrowLeft,
  FileText
} from 'lucide-react';
import { useAuth } from '@clerk/clerk-react';
import { api, type UserBook} from '@/lib/api';

interface MyBooksLibraryProps {
  onBack: () => void;
  onOpenBook: (bookId?: string, runId?: string) => void;
  onOpenFlip: (bookId?: string, runId?: string) => void;
}

export function MyBooksLibrary({ onBack, onOpenBook, onOpenFlip }: MyBooksLibraryProps) {
  const [books, setBooks] = useState<UserBook[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { getToken } = useAuth();
  const { toast } = useToast();

  const loadBooks = async () => {
    try {
      setLoading(true);
      setError(null);
      const token = await getToken();
      if (!token) {
        throw new Error('Нужно войти в аккаунт');
      }
      
      const response = await api.getMyBooks(token);
      setBooks(response.books);
    } catch (err) {
      console.error('Ошибка загрузки книг:', err);
      setError(err instanceof Error ? err.message : 'Что-то пошло не так');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBooks();
  }, []);

  const handleViewBook = async (book: UserBook) => {
    try {
      // Открываем в новой вкладке через SPA роут
      window.open(`/reader/${book.run_id}`, '_blank');
    } catch (err) {
      toast({
        title: "Ошибка",
        description: "Не удалось открыть книгу",
        variant: "destructive",
      });
    }
  };

  const handleFlipBook = (book: UserBook) => {
    // Открываем в новой вкладке через SPA роут
    window.open(`/reader/${book.run_id}`, '_blank');
  };

  const handleDownloadBook = async (book: UserBook) => {
    try {
      const token = await getToken();
      if (!token) {
        toast({
          title: "Ошибка", 
          description: "Нужно войти в аккаунт",
          variant: "destructive",
        });
        return;
      }
      
      await api.downloadSavedBook(book.id, 'book.pdf', token);
      toast({
        title: "Готово",
        description: "Книга скачана",
      });
    } catch (err) {
      toast({
        title: "Ошибка",
        description: "Не удалось скачать книгу",
        variant: "destructive",
      });
    }
  };

  const handleDeleteBook = async (book: UserBook) => {
    if (!confirm('Вы уверены, что хотите удалить эту книгу?')) {
      return;
    }

    try {
      const token = await getToken();
      if (!token) {
        toast({
          title: "Ошибка",
          description: "Нужно войти в аккаунт",
          variant: "destructive",
        });
        return;
      }

      await api.deleteBook(book.id, token);
      setBooks(prev => prev.filter(b => b.id !== book.id));
      toast({
        title: "Готово",
        description: "Книга удалена",
      });
    } catch (err) {
      toast({
        title: "Ошибка",
        description: "Не удалось удалить книгу",
        variant: "destructive",
      });
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center mobile-padding">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-600 dark:text-gray-400" />
          <p className="text-gray-600 dark:text-gray-400">Загружаем ваши книги...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="responsive-container py-6 sm:py-8">
        {/* Заголовок */}
        <div className="mb-6 sm:mb-8">
          <div className="flex items-center gap-3 sm:gap-4 mb-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={onBack}
              className="shrink-0 touch-target"
            >
              <ArrowLeft className="h-4 w-4 sm:h-5 sm:w-5" />
              <span className="sr-only">Назад</span>
            </Button>
            <div>
              <h1 className="text-xl sm:text-2xl font-bold text-black dark:text-white">Мои книги</h1>
              <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">Все ваши созданные книги</p>
            </div>
          </div>
        </div>

        {/* Карточки статистики */}
        <div className="mobile-friendly-grid mb-6 sm:mb-8">
          <Card className="border-gray-200 dark:border-gray-800 dark:bg-gray-950">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
                  <Book className="h-4 w-4 sm:h-5 sm:w-5 text-gray-700 dark:text-gray-300" />
                </div>
                <div>
                  <p className="text-xl sm:text-2xl font-bold text-black dark:text-white">{books.length}</p>
                  <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">книг</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-gray-200 dark:border-gray-800 dark:bg-gray-950">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
                  <Download className="h-4 w-4 sm:h-5 sm:w-5 text-gray-700 dark:text-gray-300" />
                </div>
                <div>
                  <p className="text-xl sm:text-2xl font-bold text-black dark:text-white">{books.filter(b => b.has_pdf).length}</p>
                  <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">PDF файлов</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-gray-200 dark:border-gray-800 dark:bg-gray-950">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
                  <FileText className="h-4 w-4 sm:h-5 sm:w-5 text-gray-700 dark:text-gray-300" />
                </div>
                <div>
                  <p className="text-xl sm:text-2xl font-bold text-black dark:text-white">{books.filter(b => b.has_html).length}</p>
                  <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">веб-версий</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Состояние ошибки */}
        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50 dark:border-red-900/50 dark:bg-red-900/20">
            <AlertDescription className="text-red-800 dark:text-red-300">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Пустое состояние */}
        {!loading && books.length === 0 && (
          <Card className="border-gray-200 dark:border-gray-800 dark:bg-gray-950">
            <CardContent className="p-8 sm:p-12 text-center">
              <div className="mb-4">
                <Book className="h-12 w-12 sm:h-16 sm:w-16 mx-auto text-gray-400" />
              </div>
              <h3 className="text-base sm:text-lg font-medium text-black dark:text-white mb-2">Пока нет книг</h3>
              <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400 mb-6">
                Создайте свою первую книгу, чтобы она появилась здесь
              </p>
              <Button 
                onClick={onBack}
                className="bg-black dark:bg-white text-white dark:text-black hover:bg-gray-800 dark:hover:bg-gray-200 touch-target"
              >
                Создать книгу
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Список книг */}
        <div className="space-y-4 sm:space-y-6">
          {books.map((book) => (
            <Card key={book.id} className="border-gray-200 dark:border-gray-800 dark:bg-gray-950">
              <CardContent className="p-4 sm:p-6">
                <div className="flex flex-col gap-4">
                  {/* Информация о книге */}
                  <div className="flex-grow">
                    <h2 className="text-lg sm:text-xl font-bold text-black dark:text-white mb-2">{book.title}</h2>
                    <div className="flex flex-col sm:flex-row gap-2 sm:gap-6 text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-3 sm:mb-4">
                      <div className="flex items-center gap-2">
                        <User className="h-3 w-3 sm:h-4 sm:w-4" />
                        <span>{book.profile_full_name ?? book.profile_username ?? '—'}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="h-3 w-3 sm:h-4 sm:w-4" />
                        <span>{formatDate(book.created_at)}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 mb-4">
                      {book.has_html && (
                        <Badge variant="outline" className="border-blue-300 text-blue-600 dark:border-blue-700 dark:text-blue-400 text-xs">
                          Веб-версия
                        </Badge>
                      )}
                      {book.has_pdf && (
                        <Badge variant="outline" className="border-green-300 text-green-600 dark:border-green-700 dark:text-green-400 text-xs">
                          PDF
                        </Badge>
                      )}
                    </div>
                  </div>
                  
                  {/* Кнопки действий */}
                  <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
                    <div className="flex gap-2 flex-1">
                      <Button
                        variant="outline"
                        onClick={() => handleViewBook(book)}
                        className="border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 flex-1 sm:flex-none touch-target"
                        size="sm"
                      >
                        <Eye className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                        <span className="text-xs sm:text-sm">Читать</span>
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => handleFlipBook(book)}
                        className="border-gray-300 dark:border-gray-700 text-purple-700 dark:text-purple-300 hover:bg-purple-50 dark:hover:bg-purple-900/20 flex-1 sm:flex-none touch-target"
                        size="sm"
                      >
                        <span className="text-xs sm:text-sm">Flipbook</span>
                      </Button>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        onClick={() => handleDownloadBook(book)}
                        className="border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 flex-1 sm:flex-none touch-target"
                        disabled={!book.has_pdf}
                        size="sm"
                      >
                        <Download className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                        <span className="text-xs sm:text-sm">PDF</span>
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteBook(book)}
                        className="text-gray-500 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 touch-target"
                      >
                        <Trash2 className="h-3 w-3 sm:h-4 sm:w-4" />
                        <span className="sr-only">Удалить</span>
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
} 
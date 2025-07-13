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
    if (!confirm(`Удалить книгу "${book.title}"?`)) {
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
      setBooks(books.filter(b => b.id !== book.id));
      toast({
        title: "Удалено",
        description: "Книга удалена из библиотеки",
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
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white dark:bg-gray-900 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center gap-4 mb-8">
            <Button
              variant="ghost"
              onClick={onBack}
              className="text-gray-700 dark:text-gray-300 hover:text-black dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Назад
            </Button>
          </div>
          
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-600 dark:text-gray-400" />
              <p className="text-gray-600 dark:text-gray-400">Загружаем ваши книги...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost" 
              onClick={onBack}
              className="text-gray-700 dark:text-gray-300 hover:text-black dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Назад
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-black dark:text-white">Мои книги</h1>
              <p className="text-gray-600 dark:text-gray-400">Все ваши созданные книги</p>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="border-gray-200 dark:border-gray-800 dark:bg-gray-950">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
                  <Book className="h-5 w-5 text-gray-700 dark:text-gray-300" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-black dark:text-white">{books.length}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">книг</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-gray-200 dark:border-gray-800 dark:bg-gray-950">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
                  <Download className="h-5 w-5 text-gray-700 dark:text-gray-300" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-black dark:text-white">{books.filter(b => b.has_pdf).length}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">PDF файлов</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-gray-200 dark:border-gray-800 dark:bg-gray-950">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
                  <FileText className="h-5 w-5 text-gray-700 dark:text-gray-300" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-black dark:text-white">{books.filter(b => b.has_html).length}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">веб-версий</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Error State */}
        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50 dark:border-red-900/50 dark:bg-red-900/20">
            <AlertDescription className="text-red-800 dark:text-red-300">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Empty State */}
        {!loading && books.length === 0 && (
          <Card className="border-gray-200 dark:border-gray-800 dark:bg-gray-950">
            <CardContent className="p-12 text-center">
              <div className="mb-4">
                <Book className="h-16 w-16 mx-auto text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-black dark:text-white mb-2">Пока нет книг</h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Создайте свою первую книгу, чтобы она появилась здесь
              </p>
              <Button 
                onClick={onBack}
                className="bg-black dark:bg-white text-white dark:text-black hover:bg-gray-800 dark:hover:bg-gray-200"
              >
                Создать книгу
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Books List */}
        <div className="space-y-6">
            {books.map((book) => (
            <Card key={book.id} className="border-gray-200 dark:border-gray-800 dark:bg-gray-950">
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row gap-6">
                  {/* Book Info */}
                  <div className="flex-grow">
                    <h2 className="text-xl font-bold text-black dark:text-white mb-2">{book.title}</h2>
                    <div className="flex items-center gap-6 text-sm text-gray-600 dark:text-gray-400 mb-4">
                      <div className="flex items-center gap-2">
                        <User className="h-4 w-4" />
                        <span>{book.profile_full_name ?? book.profile_username ?? '—'}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        <span>{formatDate(book.created_at)}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {book.has_html && <Badge variant="outline" className="border-blue-300 text-blue-600 dark:border-blue-700 dark:text-blue-400">Веб-версия</Badge>}
                      {book.has_pdf && <Badge variant="outline" className="border-green-300 text-green-600 dark:border-green-700 dark:text-green-400">PDF</Badge>}
                    </div>
                  </div>
                  
                  {/* Action Buttons */}
                  <div className="flex-shrink-0 flex items-center gap-2">
                      <Button
                        variant="outline"
                        onClick={() => handleViewBook(book)}
                      className="border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800"
                      >
                      <Eye className="h-4 w-4 mr-2" />
                        Читать
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => handleFlipBook(book)}
                        className="border-gray-300 dark:border-gray-700 text-purple-700 dark:text-purple-300 hover:bg-purple-50 dark:hover:bg-purple-900/20"
                      >
                        Flipbook
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => handleDownloadBook(book)}
                      className="border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800"
                      disabled={!book.has_pdf}
                      >
                      <Download className="h-4 w-4 mr-2" />
                        PDF
                      </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDeleteBook(book)}
                      className="text-gray-500 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
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
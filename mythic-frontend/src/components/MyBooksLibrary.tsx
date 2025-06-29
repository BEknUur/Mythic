import  { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
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
}

export function MyBooksLibrary({ onBack }: MyBooksLibraryProps) {
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
      const token = await getToken();
      if (!token) {
        toast({
          title: "Ошибка",
          description: "Нужно войти в аккаунт",
          variant: "destructive",
        });
        return;
      }
      
      const url = api.getSavedBookViewUrl(book.id, token);
      window.open(url, '_blank');
    } catch (err) {
      toast({
        title: "Ошибка",
        description: "Не удалось открыть книгу",
        variant: "destructive",
      });
    }
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
      <div className="min-h-screen bg-white p-6">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center gap-4 mb-8">
            <Button
              variant="ghost"
              onClick={onBack}
              className="text-gray-700 hover:text-black hover:bg-gray-100"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Назад
            </Button>
          </div>
          
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-600" />
              <p className="text-gray-600">Загружаем ваши книги...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost" 
              onClick={onBack}
              className="text-gray-700 hover:text-black hover:bg-gray-100"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Назад
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-black">Мои книги</h1>
              <p className="text-gray-600">Все ваши созданные книги</p>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="border-gray-200">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gray-100 rounded-lg">
                  <Book className="h-5 w-5 text-gray-700" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-black">{books.length}</p>
                  <p className="text-sm text-gray-600">книг</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-gray-200">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gray-100 rounded-lg">
                  <Download className="h-5 w-5 text-gray-700" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-black">{books.filter(b => b.has_pdf).length}</p>
                  <p className="text-sm text-gray-600">PDF файлов</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-gray-200">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gray-100 rounded-lg">
                  <FileText className="h-5 w-5 text-gray-700" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-black">{books.filter(b => b.has_html).length}</p>
                  <p className="text-sm text-gray-600">веб-версий</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Error State */}
        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertDescription className="text-red-800">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Empty State */}
        {!loading && books.length === 0 && (
          <Card className="border-gray-200">
            <CardContent className="p-12 text-center">
              <div className="mb-4">
                <Book className="h-16 w-16 mx-auto text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-black mb-2">Пока нет книг</h3>
              <p className="text-gray-600 mb-6">
                Создайте свою первую книгу, чтобы она появилась здесь
              </p>
              <Button 
                onClick={onBack}
                className="bg-black text-white hover:bg-gray-800"
              >
                Создать книгу
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Books Grid */}
        {books.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {books.map((book) => (
              <Card key={book.id} className="border-gray-200 hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg font-medium text-black line-clamp-2">
                    {book.title}
                  </CardTitle>
                  <CardDescription className="text-gray-600">
                    {book.profile_full_name && (
                      <div className="flex items-center gap-1 mb-1">
                        <User className="h-3 w-3" />
                        <span className="text-sm">{book.profile_full_name}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      <span className="text-sm">{formatDate(book.created_at)}</span>
                    </div>
                  </CardDescription>
                </CardHeader>
                
                <CardContent className="pt-0">
                  <div className="flex flex-wrap gap-2 mb-4">
                    {book.has_html && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                        Веб-версия
                      </span>
                    )}
                    {book.has_pdf && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                        PDF
                      </span>
                    )}
                  </div>
                  
                  <div className="flex gap-2">
                    {book.has_html && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleViewBook(book)}
                        className="flex-1 border-gray-300 text-gray-700 hover:bg-gray-50 hover:text-black"
                      >
                        <Eye className="h-4 w-4 mr-1" />
                        Читать
                      </Button>
                    )}
                    
                    {book.has_pdf && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDownloadBook(book)}
                        className="flex-1 border-gray-300 text-gray-700 hover:bg-gray-50 hover:text-black"
                      >
                        <Download className="h-4 w-4 mr-1" />
                        PDF
                      </Button>
                    )}
                    
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDeleteBook(book)}
                      className="text-gray-500 hover:text-red-600 hover:bg-red-50"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
} 
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Instagram, Zap, BookOpen, LogIn, UserPlus } from 'lucide-react';
import { useUser, SignInButton, SignUpButton, UserButton } from '@clerk/clerk-react';

export function Hero() {
  const { isSignedIn, user } = useUser();

  return (
    <section className="py-20 px-4">
      <div className="max-w-4xl mx-auto text-center">
        <div className="absolute top-6 right-6 flex gap-3">
          {isSignedIn ? (
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600">
                Привет, {user?.firstName || 'Пользователь'}!
              </span>
              <UserButton />
            </div>
          ) : (
            <>
              <SignInButton mode="modal">
                <Button variant="outline" size="sm" className="flex items-center gap-2">
                  <LogIn className="h-4 w-4" />
                  Войти
                </Button>
              </SignInButton>
              <SignUpButton mode="modal">
                <Button size="sm" className="flex items-center gap-2">
                  <UserPlus className="h-4 w-4" />
                  Регистрация
                </Button>
              </SignUpButton>
            </>
          )}
        </div>

        <h1 className="text-5xl md:text-6xl font-semibold italic text-black mb-6" style={{ fontFamily: 'Playfair Display, serif' }}>
          Создайте романтическую книгу
        </h1>
        
        <p className="text-xl text-gray-600 mb-4 max-w-2xl mx-auto">
          Превратите Instagram профиль в прекрасную книгу
        </p>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          с помощью искусственного интеллекта
        </p>

        {!isSignedIn && (
          <div className="mb-8 p-4 bg-amber-50 border border-amber-200 rounded-lg max-w-lg mx-auto">
            <p className="text-amber-800 text-sm">
              💡 Для создания и просмотра книги необходима регистрация
            </p>
          </div>
        )}

        <div className="flex justify-center gap-3 flex-wrap">
          <Badge variant="secondary" className="px-4 py-2 bg-gray-100 text-gray-800 hover:bg-gray-200">
            <Instagram className="h-4 w-4 mr-2" />
            Instagram
          </Badge>
          <Badge variant="secondary" className="px-4 py-2 bg-gray-100 text-gray-800 hover:bg-gray-200">
            <Zap className="h-4 w-4 mr-2" />
            AI-генерация
          </Badge>
          <Badge variant="secondary" className="px-4 py-2 bg-gray-100 text-gray-800 hover:bg-gray-200">
            <BookOpen className="h-4 w-4 mr-2" />
            HTML-книга
          </Badge>
        </div>
      </div>
    </section>
  );
} 
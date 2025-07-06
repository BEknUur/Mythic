import { Link } from 'react-router-dom';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { LogIn, UserPlus, Lock, MoveRight, Sparkles } from 'lucide-react';
import { useUser, SignInButton, SignUpButton, UserButton } from '@clerk/clerk-react';

export function Hero() {
  const { isSignedIn, user } = useUser();

  return (
    <section className="relative w-full h-screen flex flex-col items-center justify-center text-center px-4 overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 left-0 w-full h-full bg-white -z-10">
        <div className="absolute bottom-0 left-[-20%] right-0 top-[-10%] h-[500px] w-[500px] rounded-full bg-[radial-gradient(circle_farthest-side,rgba(255,0,182,.15),rgba(255,255,255,0))]"></div>
        <div className="absolute bottom-0 right-[-20%] top-[-10%] h-[500px] w-[500px] rounded-full bg-[radial-gradient(circle_farthest-side,rgba(255,0,182,.15),rgba(255,255,255,0))]"></div>
      </div>
      
      {/* Auth buttons */}
      <div className="absolute top-6 right-6 flex gap-3 animate-fade-in-down">
        {isSignedIn ? (
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-700">
              Привет, {user?.firstName || 'Пользователь'}
            </span>
            <UserButton afterSignOutUrl="/" />
          </div>
        ) : (
          <>
            <SignUpButton mode="modal">
              <Button variant="ghost" size="sm" className="group transition-all duration-300">
                Регистрация
                <MoveRight className="h-4 w-4 ml-2 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300"/>
              </Button>
            </SignUpButton>
            <SignInButton mode="modal">
              <Button size="sm" className="bg-gray-900 text-white hover:bg-gray-800 shadow-lg transition-all duration-300">
                Войти
              </Button>
            </SignInButton>
          </>
        )}
      </div>

      <div className="animate-fade-in-up">
        <Badge variant="outline" className="mb-6 border-gray-300 text-gray-600">
          <Sparkles className="h-3 w-3 mr-2 text-purple-500" />
          Создано с любовью и AI
        </Badge>
        
        <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 tracking-tighter" style={{ fontFamily: 'Manrope, sans-serif' }}>
          Превратите ваш <span className="text-purple-600 italic">Instagram</span><br /> в романтическую книгу
        </h1>
        
        <p className="text-lg text-gray-500 mb-8 max-w-2xl mx-auto">
          Сохраните вашу цифровую историю любви в уникальной книге, созданной искусственным интеллектом.
          Идеальный подарок для вашего партнера.
        </p>

        <div className="flex justify-center items-center gap-4 mb-12">
          <Link to="/generate">
            <Button size="lg" className="bg-gray-900 text-white hover:bg-gray-800 shadow-lg px-8 py-6 text-lg group">
              Начать создание
              <MoveRight className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform duration-300" />
            </Button>
          </Link>
          <Button variant="link" className="text-gray-600">
            Как это работает?
          </Button>
        </div>

        {!isSignedIn && (
          <div className="mb-8">
            <div className="inline-flex items-center gap-2 text-sm text-gray-500">
              <Lock className="h-4 w-4" />
              Требуется регистрация для продолжения
            </div>
          </div>
        )}
      </div>
    </section>
  );
} 
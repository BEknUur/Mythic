import { Link } from 'react-router-dom';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { LogIn, UserPlus, Lock, MoveRight, Sparkles, Camera, Bot, BookHeart } from 'lucide-react';
import { useUser, SignInButton, SignUpButton, UserButton } from '@clerk/clerk-react';
import { TOUR_STEP_IDS } from './ui/tour';
import { ThemeToggle } from './theme-toggle';

export function Hero() {
  const { isSignedIn, user } = useUser();

  return (
    <section className="relative w-full h-screen flex flex-col items-center justify-center text-center px-4 overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 left-0 w-full h-full bg-white dark:bg-gray-950 -z-10">
        <div className="absolute bottom-0 left-[-20%] right-0 top-[-10%] h-[500px] w-[500px] rounded-full bg-[radial-gradient(circle_farthest-side,rgba(255,0,182,.15),rgba(255,255,255,0))]"></div>
        <div className="absolute bottom-0 right-[-20%] top-[-10%] h-[500px] w-[500px] rounded-full bg-[radial-gradient(circle_farthest-side,rgba(255,0,182,.15),rgba(255,255,255,0))]"></div>
      </div>
      
      {/* Auth buttons */}
      <div className="absolute top-6 right-6 flex items-center gap-4 animate-fade-in-down">
        {isSignedIn ? (
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-700 dark:text-gray-300">
              Привет, {user?.firstName || 'Пользователь'}
            </span>
            <UserButton afterSignOutUrl="/" />
          </div>
        ) : (
          <>
            <SignUpButton mode="modal">
              <Button variant="ghost" size="sm">
                Регистрация
              </Button>
            </SignUpButton>
            <SignInButton mode="modal">
              <Button size="sm" className="bg-gray-900 text-white hover:bg-gray-800 dark:bg-gray-50 dark:text-gray-900 dark:hover:bg-gray-200">
                Войти
              </Button>
            </SignInButton>
          </>
        )}
        <ThemeToggle />
      </div>

      <div className="animate-fade-in-up">
        <Badge variant="outline" className="mb-6 border-gray-300 dark:border-gray-700 text-gray-600 dark:text-gray-400">
          <Sparkles className="h-3 w-3 mr-2 text-purple-500" />
          Создано с любовью и AI
        </Badge>
        
        <h1 className="text-5xl md:text-7xl font-bold text-gray-900 dark:text-gray-50 mb-6 tracking-tighter tour-step-1" style={{ fontFamily: 'Manrope, sans-serif' }}>
          Превратите ваш <span className="text-purple-600 italic">Instagram</span><br /> в  книгу
        </h1>
        
        <p className="text-lg text-gray-500 dark:text-gray-400 mb-8 max-w-2xl mx-auto">
          Сохраните вашу цифровую историю любви в уникальной книге, созданной искусственным интеллектом.
          Идеальный подарок для вашего партнера.
        </p>

        <div className="flex justify-center items-center gap-4 mb-12">
          <Link to="/generate" id={TOUR_STEP_IDS.START_CREATING_BUTTON}>
            <Button size="lg" className="bg-gray-900 text-white hover:bg-gray-800 dark:bg-gray-50 dark:text-gray-900 dark:hover:bg-gray-200 shadow-lg px-8 py-6 text-lg group">
              Начать создание
              <MoveRight className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform duration-300" />
            </Button>
          </Link>
          <Button variant="link" className="text-gray-600 dark:text-gray-400" onClick={() => window.dispatchEvent(new CustomEvent('start-tour'))}>
            Как это работает?
          </Button>
        </div>

        <div className="text-sm font-medium text-gray-500 dark:text-gray-400 animate-fade-in-up" style={{ animationDelay: '300ms' }}>
          <div className="flex justify-center items-center gap-4 sm:gap-8">
            <div className="flex items-center gap-2">
              <Camera className="h-4 w-4 text-purple-500" />
              <span>Анализ фото</span>
            </div>
            <div className="text-gray-300 dark:text-gray-600 font-mono text-sm">→</div>
            <div className="flex items-center gap-2">
              <Bot className="h-4 w-4 text-purple-500" />
              <span>Магия ИИ</span>
            </div>
            <div className="text-gray-300 dark:text-gray-600 font-mono text-sm">→</div>
            <div className="flex items-center gap-2">
              <BookHeart className="h-4 w-4 text-purple-500" />
              <span>Ваша книга</span>
            </div>
          </div>
        </div>

        {!isSignedIn && (
          <div className="mt-8">
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
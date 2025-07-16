import { Link } from 'react-router-dom';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { LogIn, UserPlus, Lock, MoveRight, Sparkles, Camera, Bot, BookHeart, ChevronDown } from 'lucide-react';
import { PhoneMockup } from './PhoneMockup';
import { useUser, SignInButton, SignUpButton, UserButton } from '@clerk/clerk-react';
import { TOUR_STEP_IDS } from './ui/tour';
import { ThemeToggle } from './theme-toggle';

export function Hero() {
  const { isSignedIn, user } = useUser();

  return (
    <section className="relative w-full overflow-hidden bg-gradient-to-br from-gray-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-950 dark:to-purple-950">
      {/* Auth buttons */}
      <div className="absolute top-6 right-6 flex items-center gap-4 animate-fade-in-down z-10">
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
              <Button
                size="sm"
                className="bg-gray-900 text-white hover:bg-gray-800 dark:bg-gray-50 dark:text-gray-900 dark:hover:bg-gray-200"
              >
                Войти
              </Button>
            </SignInButton>
          </>
        )}
        <ThemeToggle />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 md:px-12 py-24 md:py-32 flex flex-col md:flex-row items-center justify-between gap-16 md:gap-24">
        {/* Left: Content */}
        <div className="w-full md:w-1/2 text-left animate-fade-in-up">
          <Badge
            variant="outline"
            className="mb-6 border-gray-300 dark:border-gray-700 text-gray-600 dark:text-gray-400 inline-flex items-center"
          >
            <Sparkles className="h-3 w-3 mr-2 text-purple-500" />
            Создано с любовью и AI
          </Badge>

          <h1
            className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-gray-900 dark:text-gray-50 mb-6 tracking-tight tour-step-1"
            style={{ fontFamily: 'Manrope, sans-serif' }}
          >
            Превратите ваш <span className="text-purple-600 italic">Instagram</span>
            <br className="hidden sm:block" /> в книгу
          </h1>

          <p className="text-base sm:text-lg lg:text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-xl">
            Сохраните вашу цифровую историю любви в уникальной книге, созданной искусственным интеллектом.
            Идеальный подарок для вашего партнера.
          </p>

          <div className="flex items-center gap-4 mb-10">
            <Link to="/generate" id={TOUR_STEP_IDS.START_CREATING_BUTTON}>
              <Button
                size="lg"
                className="bg-purple-600 hover:bg-purple-700 text-white shadow-lg px-8 py-6 text-lg group"
              >
                Начать создание
                <MoveRight className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform duration-300" />
              </Button>
            </Link>
            <Button
              variant="link"
              className="text-gray-600 dark:text-gray-400"
              onClick={() => window.dispatchEvent(new CustomEvent('start-tour'))}
            >
              Как это работает?
            </Button>
          </div>

          {/* Mini process icons */}
          <div className="hidden sm:flex items-center gap-4 sm:gap-6 text-sm font-medium text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-2">
              <Camera className="h-4 w-4 text-purple-500" />
              <span>Анализ фото</span>
            </div>
            <span className="text-gray-300 dark:text-gray-600">→</span>
            <div className="flex items-center gap-2">
              <Bot className="h-4 w-4 text-purple-500" />
              <span>Магия ИИ</span>
            </div>
            <span className="text-gray-300 dark:text-gray-600">→</span>
            <div className="flex items-center gap-2">
              <BookHeart className="h-4 w-4 text-purple-500" />
              <span>Ваша книга</span>
            </div>
          </div>

          {!isSignedIn && (
            <div className="mt-6">
              <div className="inline-flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <Lock className="h-4 w-4" />
                Требуется регистрация для продолжения
              </div>
            </div>
          )}
        </div>

        {/* Right: Mock-up */}
        <div className="w-full md:w-1/2 flex justify-center md:justify-end animate-slide-in-right">
          <PhoneMockup
            src="/photo.png"                // <-- абсолютный путь из public/
            className="w-64 md:w-80 lg:w-96" // <-- задаём размер через Tailwind
          />
        </div>
      </div>

      {/* Scroll anchor */}
      <a
        href="#features"
        className="absolute bottom-6 left-1/2 -translate-x-1/2 text-gray-500 dark:text-gray-400 animate-bounce"
      >
        <ChevronDown className="h-6 w-6" />
      </a>
    </section>
  );
}

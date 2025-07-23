import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { 
  Settings, 
  User, 
  CreditCard, 
  Bell, 
  Lock, 
  Moon, 
  Sun, 
  Download,
  Trash2,
  ExternalLink
} from 'lucide-react';
import { useUser, UserButton } from '@clerk/clerk-react';
import { useState, useEffect } from 'react';

export function SettingsPage() {
  const { user } = useUser();
  const [theme, setThemeState] = useState<'light' | 'dark' | 'system'>('system');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'system';
    if (savedTheme) {
      setThemeState(savedTheme);
    }
  }, []);

  const setTheme = (newTheme: 'light' | 'dark' | 'system') => {
    setThemeState(newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Применяем тему к документу
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else if (newTheme === 'light') {
      document.documentElement.classList.remove('dark');
    } else {
      // system
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (isDark) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  };

  const handleClearCache = () => {
    localStorage.clear();
    sessionStorage.clear();
    window.location.reload();
  };

  const handleExportData = () => {
    // В будущем здесь будет экспорт пользовательских данных
    alert('Экспорт данных будет доступен в ближайшее время');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-3">
            <Settings className="h-8 w-8 text-primary" />
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Настройки</h1>
          </div>
          <UserButton afterSignOutUrl="/" />
        </div>

        <div className="grid gap-6">
          {/* Profile Settings */}
          <Card>
            <CardHeader>
              <div className="flex items-center space-x-2">
                <User className="h-5 w-5" />
                <CardTitle>Профиль</CardTitle>
              </div>
              <CardDescription>
                Управление информацией профиля
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Email</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {user?.primaryEmailAddress?.emailAddress || 'Не указан'}
                  </p>
                </div>
                <Badge variant="secondary">Подтвержден</Badge>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Имя пользователя</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {user?.fullName || user?.firstName || 'Не указано'}
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  Изменить
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Theme Settings */}
          <Card>
            <CardHeader>
              <div className="flex items-center space-x-2">
                {theme === 'dark' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
                <CardTitle>Тема</CardTitle>
              </div>
              <CardDescription>
                Настройка внешнего вида приложения
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex space-x-2">
                <Button
                  variant={theme === 'light' ? 'default' : 'outline'}
                  onClick={() => setTheme('light')}
                  className="flex items-center space-x-2"
                >
                  <Sun className="h-4 w-4" />
                  <span>Светлая</span>
                </Button>
                <Button
                  variant={theme === 'dark' ? 'default' : 'outline'}
                  onClick={() => setTheme('dark')}
                  className="flex items-center space-x-2"
                >
                  <Moon className="h-4 w-4" />
                  <span>Темная</span>
                </Button>
                <Button
                  variant={theme === 'system' ? 'default' : 'outline'}
                  onClick={() => setTheme('system')}
                >
                  Системная
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Subscription */}
          <Card>
            <CardHeader>
              <div className="flex items-center space-x-2">
                <CreditCard className="h-5 w-5" />
                <CardTitle>Подписка</CardTitle>
              </div>
              <CardDescription>
                Управление подпиской и оплатой
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Текущий план</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Бесплатный</p>
                </div>
                <Badge variant="outline">Free</Badge>
              </div>
              <Button variant="outline" className="w-full">
                <ExternalLink className="h-4 w-4 mr-2" />
                Перейти к тарифам
              </Button>
            </CardContent>
          </Card>

          {/* Data & Privacy */}
          <Card>
            <CardHeader>
              <div className="flex items-center space-x-2">
                <Lock className="h-5 w-5" />
                <CardTitle>Данные и конфиденциальность</CardTitle>
              </div>
              <CardDescription>
                Управление личными данными
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button
                variant="outline"
                onClick={handleExportData}
                className="w-full justify-start"
              >
                <Download className="h-4 w-4 mr-2" />
                Экспортировать данные
              </Button>
              <Button
                variant="outline"
                onClick={handleClearCache}
                className="w-full justify-start"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Очистить кэш
              </Button>
            </CardContent>
          </Card>

          {/* Notifications */}
          <Card>
            <CardHeader>
              <div className="flex items-center space-x-2">
                <Bell className="h-5 w-5" />
                <CardTitle>Уведомления</CardTitle>
              </div>
              <CardDescription>
                Настройка уведомлений
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Email уведомления</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Получать уведомления о готовности книг
                    </p>
                  </div>
                  <Badge variant="secondary">Скоро</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 
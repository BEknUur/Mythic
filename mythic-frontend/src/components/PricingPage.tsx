import React, { useState } from 'react';
import { Check, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { ProModal } from './ProModal';
import { useAuth } from '@clerk/clerk-react';
import { useToast } from '@/hooks/use-toast';
import { payments } from '@/lib/api';

const tiers = [
  {
    name: 'Бесплатно',
    price: '$0',
    frequency: 'навсегда',
    description: 'Две бесплатные генерации: одна Classic и одна Flipbook. Дальнейшие генерации — платные.',
    features: [
      '1 бесплатная генерация Classic',
      '1 бесплатная генерация Flipbook',
      'Веб-версия книги',
      'Возможность скачать PDF',
      'Стандартная поддержка',
    ],
    cta: 'Начать бесплатно',
    isMostPopular: false,
    action: 'free'
  },
  {
    name: 'Pro',
    price: '$9.99',
    frequency: '/ месяц',
    description: 'Раскройте полный потенциал и создавайте неограниченное количество историй.',
    features: [
      'Неограниченные генерации книг',
      'Приоритетная обработка',
      'Доступ к премиум-стилям',
      'Создание видео для TikTok (скоро)',
      'Приоритетная поддержка',
    ],
    cta: 'Перейти на Pro',
    isMostPopular: true,
    action: 'pro'
  },
];

export function PricingPage() {
  const [isProModalOpen, setIsProModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { getToken } = useAuth();
  const { toast } = useToast();

  const handleProClick = () => {
    setIsProModalOpen(true);
  };

  const handleSinglePayment = async () => {
    setIsLoading(true);
    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Необходима авторизация');
      }

      const response = await payments.createCheckout({
        product_type: 'single_generation'
      }, token);

      if (response.success) {
        window.location.href = response.checkout_url;
      } else {
        throw new Error(response.message);
      }
    } catch (error) {
      console.error('Ошибка создания checkout:', error);
      toast({
        title: "Ошибка",
        description: error instanceof Error ? error.message : 'Не удалось создать платеж',
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFreeClick = () => {
    // Перенаправляем на страницу создания книги
    window.location.href = '/generate';
  };

  return (
    <>
      <div className="bg-white dark:bg-gray-950 py-20 sm:py-28 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-gray-50 mb-4 tracking-tighter">
              Выберите свой план
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Начните бесплатно и переходите на Pro, когда будете готовы к безграничному творчеству.
            </p>
          </div>

          <div className="mt-16 grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Инфоблок теперь первый элемент сетки */}
            <div className="col-span-1 lg:col-span-2 flex justify-center mb-4">
              <div className="bg-purple-50 border border-purple-200 rounded-xl px-6 py-4 text-center max-w-xl w-full text-purple-900 text-base font-medium">
                После бесплатных генераций каждая новая генерация книги (Classic или Flipbook) стоит <span className="font-bold">$0.99</span>.
                <div className="mt-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={handleSinglePayment}
                    disabled={isLoading}
                    className="bg-white hover:bg-purple-50"
                  >
                    {isLoading ? 'Загрузка...' : 'Оплатить одну генерацию ($0.99)'}
                  </Button>
                </div>
              </div>
            </div>
            {tiers.map((tier) => (
              <div
                key={tier.name}
                className={cn(
                  'relative flex flex-col p-8 rounded-2xl bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800',
                  tier.isMostPopular ? 'border-purple-500 dark:border-purple-500 border-2' : ''
                )}
              >
                {tier.isMostPopular && (
                  <div className="absolute top-0 -translate-y-1/2 w-full flex justify-center">
                    <span className="inline-flex items-center gap-2 rounded-full bg-purple-500 px-4 py-1 text-sm font-semibold text-white">
                      <Sparkles className="h-4 w-4" />
                      Самый популярный
                    </span>
                  </div>
                )}
                <h3 className="text-2xl font-semibold text-gray-900 dark:text-gray-50">{tier.name}</h3>
                <p className="mt-4 text-gray-500 dark:text-gray-400">{tier.description}</p>
                <div className="mt-6">
                  <span className="text-4xl font-bold text-gray-900 dark:text-gray-50">{tier.price}</span>
                  <span className="text-lg font-medium text-gray-500 dark:text-gray-400">{tier.frequency}</span>
                </div>
                <ul role="list" className="mt-8 space-y-4 flex-1">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-3">
                      <Check className="h-5 w-5 text-purple-500" />
                      <span className="text-gray-700 dark:text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button
                  size="lg"
                  className={cn(
                    'mt-10 w-full',
                    tier.isMostPopular 
                      ? 'bg-purple-600 text-white hover:bg-purple-700 dark:bg-purple-500 dark:hover:bg-purple-600'
                      : 'bg-gray-900 text-white hover:bg-gray-800 dark:bg-gray-50 dark:text-gray-900 dark:hover:bg-gray-200'
                  )}
                  onClick={tier.action === 'pro' ? handleProClick : handleFreeClick}
                >
                  {tier.cta}
                </Button>
              </div>
            ))}
          </div>
        </div>
      </div>
      <ProModal isOpen={isProModalOpen} setIsOpen={setIsProModalOpen} />
    </>
  );
} 
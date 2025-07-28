import React, { useState } from 'react';
import { Check, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { ProModal } from './ProModal';
import { useAuth } from '@clerk/clerk-react';
import { useToast } from '@/hooks/use-toast';
import { payments } from '@/lib/api';
import { useLanguage } from '@/contexts/LanguageContext';

export function PricingPage() {
  const [isProModalOpen, setIsProModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { getToken } = useAuth();
  const { toast } = useToast();
  const { t } = useLanguage();

  const tiers = [
    {
      name: t('pricing.free.name'),
      price: t('pricing.free.price'),
      frequency: t('pricing.free.frequency'),
      description: t('pricing.free.description'),
      features: [
        t('pricing.features.free.1'),
        t('pricing.features.free.2'),
        t('pricing.features.free.3'),
        t('pricing.features.free.4'),
        t('pricing.features.free.5'),
      ],
      cta: t('pricing.free.cta'),
      isMostPopular: false,
      action: 'free'
    },
    {
      name: t('pricing.pro.name'),
      price: t('pricing.pro.price'),
      frequency: t('pricing.pro.frequency'),
      description: t('pricing.pro.description'),
      features: [
        t('pricing.features.pro.1'),
        t('pricing.features.pro.2'),
        t('pricing.features.pro.3'),
        t('pricing.features.pro.4'),
        t('pricing.features.pro.5'),
      ],
      cta: t('pricing.pro.cta'),
      isMostPopular: true,
      action: 'pro'
    },
  ];

  const handleProClick = () => {
    setIsProModalOpen(true);
  };

  const handleSinglePayment = async () => {
    setIsLoading(true);
    try {
      const token = await getToken();
      if (!token) {
        throw new Error(t('library.toast.error.auth'));
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
        title: t('common.error'),
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
              {t('pricing.title')}
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              {t('pricing.subtitle')}
            </p>
          </div>

          <div className="mt-16 grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Инфоблок теперь первый элемент сетки */}
            <div className="col-span-1 lg:col-span-2 flex justify-center mb-4">
              <div className="bg-purple-50 border border-purple-200 rounded-xl px-6 py-4 text-center max-w-xl w-full text-purple-900 text-base font-medium">
                {t('pricing.single_info')} <span className="font-bold">$0.99</span>.
                <div className="mt-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={handleSinglePayment}
                    disabled={isLoading}
                    className="bg-white hover:bg-purple-50"
                  >
                    {isLoading ? t('pricing.loading') : t('pricing.single_button')}
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
                      {t('pricing.popular')}
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
"use client"

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@clerk/clerk-react';
import { Mail, Loader2, CreditCard } from 'lucide-react';
import { payments } from '@/lib/api';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"


export function ProModal({ isOpen, setIsOpen }: { isOpen: boolean, setIsOpen: (open: boolean) => void }) {
  const { toast } = useToast();
  const { getToken } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [email, setEmail] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Необходима авторизация');
      }

      // Создаем checkout для Pro подписки
      const response = await payments.createCheckout({
        product_type: 'pro_subscription',
        customer_email: email || undefined
      }, token);

      if (response.success) {
        // Перенаправляем на Polar checkout
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

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogContent className="bg-gray-50 dark:bg-gray-950 border-gray-200 dark:border-gray-800">
        <DialogHeader className="text-center">
          <DialogTitle className="text-2xl font-bold tracking-tight">Перейти на Pro</DialogTitle>
          <DialogDescription>
            Разблокируйте неограниченные возможности и создавайте сколько угодно книг
          </DialogDescription>
          <div className="flex justify-center items-center gap-2 mt-2">
            <span className="font-semibold text-purple-500">$9.99/месяц</span>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 pt-4">
            <div className="space-y-2">
                <Label htmlFor="email">Email для чека (опционально)</Label>
                <Input 
                  id="email" 
                  type="email" 
                  placeholder="Ваш email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                <p className="text-xs text-gray-500">
                  Если не указать, будет использован email из вашего аккаунта
                </p>
            </div>
            
            <div className="p-4 rounded-md bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800">
                <h4 className="font-semibold text-purple-900 dark:text-purple-100 mb-2">Что входит в Pro:</h4>
                <ul className="text-sm text-purple-700 dark:text-purple-200 space-y-1">
                    <li>✨ Неограниченные генерации книг</li>
                    <li>⚡ Приоритетная обработка</li>
                    <li>🎨 Доступ к премиум-стилям</li>
                    <li>🎬 Создание видео для TikTok (скоро)</li>
                    <li>💬 Приоритетная поддержка</li>
                </ul>
            </div>

            <div className="flex items-start space-x-3 p-4 rounded-md bg-gray-100 dark:bg-gray-900">
                <Checkbox id="consent" className="mt-1" required />
                <div className="grid gap-1.5 leading-none">
                    <Label htmlFor="consent" className="font-normal">
                        Я согласен с условиями подписки и обработкой персональных данных. Подписку можно отменить в любое время.
                    </Label>
                </div>
            </div>
            
            <Button type="submit" className="w-full h-12" disabled={isLoading}>
                {isLoading ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                    <CreditCard className="mr-2 h-4 w-4" />
                )}
                Перейти к оплате
            </Button>
            
            <p className="text-xs text-center text-gray-500">
                Безопасная оплата через Polar. Отмена подписки в любое время.
            </p>
        </form>
      </DialogContent>
    </Dialog>
  );
} 
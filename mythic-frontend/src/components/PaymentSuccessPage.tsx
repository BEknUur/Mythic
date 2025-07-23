import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckCircle, Sparkles, ArrowRight } from 'lucide-react';
import { useAuth } from '@clerk/clerk-react';
import { payments } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

export function PaymentSuccessPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { getToken } = useAuth();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [checkoutStatus, setCheckoutStatus] = useState<any>(null);

  const checkoutId = searchParams.get('checkout_id');

  useEffect(() => {
    if (checkoutId) {
      verifyPayment();
    } else {
      setIsLoading(false);
    }
  }, [checkoutId]);

  const verifyPayment = async () => {
    try {
      const token = await getToken();
      if (!token || !checkoutId) return;

      const response = await payments.getCheckoutStatus(checkoutId, token);
      setCheckoutStatus(response.status);
      
      toast({
        title: "🎉 Оплата прошла успешно!",
        description: "Добро пожаловать в Pro! Теперь вы можете создавать неограниченное количество книг.",
      });
    } catch (error) {
      console.error('Ошибка проверки статуса:', error);
      toast({
        title: "Ошибка",
        description: "Не удалось проверить статус оплаты",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Проверяем статус оплаты...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md text-center">
        <CardHeader>
          <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
          <CardTitle className="text-2xl font-bold text-green-600">
            Оплата успешна!
          </CardTitle>
          <CardDescription>
            Добро пожаловать в Mythic Pro
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Sparkles className="h-5 w-5 text-purple-600" />
              <span className="font-semibold text-purple-800">Pro активирован!</span>
            </div>
            <p className="text-sm text-purple-600">
              Теперь вы можете создавать неограниченное количество книг
            </p>
          </div>

          {checkoutStatus && (
            <div className="text-sm text-gray-600 space-y-1">
              <p><strong>Checkout ID:</strong> {checkoutStatus.id}</p>
              <p><strong>Статус:</strong> {checkoutStatus.status}</p>
              {checkoutStatus.customer_email && (
                <p><strong>Email:</strong> {checkoutStatus.customer_email}</p>
              )}
            </div>
          )}

          <div className="space-y-3">
            <Button onClick={() => navigate('/generate')} className="w-full">
              <ArrowRight className="mr-2 h-4 w-4" />
              Создать первую Pro книгу
            </Button>
            <Button variant="outline" onClick={() => navigate('/library')} className="w-full">
              Перейти в библиотеку
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 
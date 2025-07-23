import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { XCircle, ArrowLeft, CreditCard } from 'lucide-react';

export function PaymentCancelPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md text-center">
        <CardHeader>
          <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
            <XCircle className="h-8 w-8 text-red-600" />
          </div>
          <CardTitle className="text-2xl font-bold text-red-600">
            Оплата отменена
          </CardTitle>
          <CardDescription>
            Вы отменили процесс оплаты
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="bg-yellow-50 p-4 rounded-lg">
            <p className="text-sm text-yellow-800">
              Ничего страшного! Вы всегда можете вернуться и оформить Pro подписку позже.
            </p>
          </div>

          <div className="space-y-3">
            <Button onClick={() => navigate('/pricing')} className="w-full">
              <CreditCard className="mr-2 h-4 w-4" />
              Попробовать еще раз
            </Button>
            <Button variant="outline" onClick={() => navigate('/')} className="w-full">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Вернуться на главную
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 
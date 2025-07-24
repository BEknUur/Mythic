import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { 
  BookOpen, 
  Download, 
  Copy, 
  CheckCircle, 
  Edit3, 
  X, 
  ArrowLeft,
  Lock,
  Crown
} from 'lucide-react';
import { useAuth, useUser, SignInButton } from '@clerk/clerk-react';
import { api, type StatusResponse } from '@/lib/api';
import { BookReader } from './BookReader';

interface BookReadyDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  runId?: string;
  status?: StatusResponse;
}

export function BookReadyDialog({
  isOpen,
  onOpenChange,
  runId,
  status,
}: BookReadyDialogProps) {
  const { toast } = useToast();
  const { getToken } = useAuth();
  const { isSignedIn } = useUser();
  const [isCopied, setIsCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [customTitle, setCustomTitle] = useState('');

  const isFlipbook = status?.format === 'flipbook';
  const hasLimitations = !isSignedIn && !isFlipbook; // Ограничения только для неавторизованных в классических книгах

  const openBookInNewTab = async () => {
    if (!runId) return;

    // Для flipbook И обычной книги - используем SPA роут
    // Это обеспечит правильное отображение через React компоненты
    window.open(`/reader/${runId}`, '_blank');
  };

  const downloadBook = async () => {
    if (!runId) return;
    
    if (!isSignedIn) {
      toast({
        title: 'Требуется авторизация',
        description: 'Для скачивания книги необходимо войти в систему',
        variant: 'destructive',
      });
      return;
    }
    
    try {
      const token = await getToken();
      await api.downloadFile(runId, 'book.pdf', token || undefined);
    } catch (error) {
      console.error('Error downloading book:', error);
      toast({
        title: 'Ошибка',
        description: 'Не удалось скачать книгу',
        variant: 'destructive',
      });
    }
  };

  const saveToLibrary = async () => {
    if (!runId) return;
    
    if (!isSignedIn) {
      toast({
        title: 'Требуется авторизация',
        description: 'Для сохранения книги необходимо войти в систему',
        variant: 'destructive',
      });
      return;
    }

    try {
      const token = await getToken();
      await api.saveBookToLibrary(runId, customTitle || undefined, token || undefined);
      toast({
        title: 'Успешно!',
        description: 'Книга сохранена в вашей библиотеке',
      });
      setIsEditing(false);
    } catch (error) {
      console.error('Error saving book:', error);
      toast({
        title: 'Ошибка',
        description: 'Не удалось сохранить книгу',
        variant: 'destructive',
      });
    }
  };

  const shareableUrl = `${window.location.origin}/reader/${runId}`;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(shareableUrl);
    setIsCopied(true);
    toast({
      title: 'Ссылка скопирована!',
      description: isSignedIn 
        ? 'Поделитесь книгой с друзьями!' 
        : 'Внимание: для полного просмотра потребуется авторизация.',
    });
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handleBackFromReader = () => {
    setIsEditing(false);
    onOpenChange(true);
  };

  if (isEditing && runId) {
    return (
      <div className="fixed inset-0 z-50">
        <BookReader runId={runId} onBack={handleBackFromReader} />
      </div>
    );
  }

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-green-600" />
            Ваша книга готова!
          </DialogTitle>
          <DialogDescription>
            {isFlipbook 
              ? "Интерактивная книга создана! Доступна для просмотра всем пользователям."
              : isSignedIn 
                ? "Романтическая книга создана с любовью. Выберите действие:"
                : "Книга готова! Вы можете просмотреть первые 10 страниц бесплатно."}
          </DialogDescription>
        </DialogHeader>

        {/* Preview Mode Warning for Non-Authenticated Users - только для классических книг */}
        {hasLimitations && (
          <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
            <CardContent className="p-4">
              <div className="flex items-start space-x-3">
                <Lock className="h-5 w-5 text-blue-600 mt-0.5" />
                <div className="flex-1">
                  <h4 className="font-semibold text-blue-900">Режим предварительного просмотра</h4>
                  <p className="text-sm text-blue-700 mt-1">
                    Вы можете просмотреть первые 10 страниц. Для полного доступа ко всем страницам, 
                    скачивания и сохранения книги войдите в систему.
                  </p>
                  <div className="mt-3">
                    <SignInButton mode="modal">
                      <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white">
                        <Crown className="h-4 w-4 mr-2" />
                        Войти для полного доступа
                      </Button>
                    </SignInButton>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Success message for Flipbook */}
        {isFlipbook && !isSignedIn && (
          <Card className="bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
            <CardContent className="p-4">
              <div className="flex items-start space-x-3">
                <BookOpen className="h-5 w-5 text-green-600 mt-0.5" />
                <div className="flex-1">
                  <h4 className="font-semibold text-green-900">Flipbook готов!</h4>
                  <p className="text-sm text-green-700 mt-1">
                    Ваша интерактивная книга доступна полностью без ограничений. 
                    Для дополнительных возможностей (сохранение, скачивание PDF) войдите в систему.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="flex flex-col gap-3 py-4">
          <Button
            onClick={openBookInNewTab}
            className="h-12 text-base bg-blue-600 hover:bg-blue-700 text-white"
            size="lg"
          >
            <BookOpen className="mr-2 h-5 w-5" />
            {isFlipbook 
              ? 'Открыть Flipbook' 
              : hasLimitations 
                ? 'Просмотреть (10 страниц)' 
                : 'Открыть книгу'}
          </Button>

          <div className="grid grid-cols-2 gap-3">
            <Button
              onClick={downloadBook}
              variant="outline"
              className="h-10 text-sm"
              disabled={!isSignedIn}
            >
              <Download className="mr-2 h-4 w-4" />
              {isSignedIn ? 'Скачать PDF' : 'Требует вход'}
            </Button>

            {isSignedIn ? (
              <Button
                onClick={saveToLibrary}
                variant="outline"
                className="h-10 text-sm"
              >
                <BookOpen className="mr-2 h-4 w-4" />
                Сохранить
              </Button>
            ) : (
              <Button
                variant="outline"
                className="h-10 text-sm"
                disabled
              >
                <Lock className="mr-2 h-4 w-4" />
                Требует вход
              </Button>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="share-url" className="text-sm text-gray-600">
              Поделиться книгой:
            </Label>
            <div className="flex gap-2">
              <Input
                id="share-url"
                value={shareableUrl}
                readOnly
                className="text-sm"
              />
              <Button
                onClick={copyToClipboard}
                variant="outline"
                size="sm"
                className="shrink-0"
              >
                {isCopied ? (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>
            {!isSignedIn && (
              <p className="text-xs text-gray-500">
                {isFlipbook 
                  ? "✨ Flipbook доступен полностью для всех по ссылке"
                  : "⚠️ Для полного просмотра по ссылке потребуется авторизация"}
              </p>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
} 
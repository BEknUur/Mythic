import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import {
  ClipboardCopy,
  ExternalLink,
  Users,
  FileText,
  Check,
  Download,
  Pencil,
} from 'lucide-react';
import { useAuth } from '@clerk/clerk-react';
import { api, type StatusResponse } from '@/lib/api';
import { BookReader } from './BookReader';
import { EditChat } from './EditChat';

interface BookReadyDialogProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  runId: string | null;
  status: StatusResponse | null;
}

export function BookReadyDialog({
  isOpen,
  onOpenChange,
  runId,
  status,
}: BookReadyDialogProps) {
  const { toast } = useToast();
  const [isCopied, setIsCopied] = useState(false);
  const [bookContent, setBookContent] = useState<string>('');
  const [isLoadingContent, setIsLoadingContent] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const { getToken } = useAuth();

  const profile = status?.profile;
  const hasHtmlFile = status?.stages.book_generated || status?.files?.html;

  const loadBookContentForPreview = async () => {
    if (!hasHtmlFile || !runId) return;
    setIsLoadingContent(true);
    try {
        const token = await getToken();
        const rawHtml = await api.getBookContent(runId, token || undefined);
        const bodyMatch = rawHtml.match(/<body[^>]*>([\s\S]*)<\/body>/i);
        let bodyContent = bodyMatch ? bodyMatch[1] : rawHtml;
        bodyContent = bodyContent.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '');
        setBookContent(bodyContent);
    } catch (error) {
        console.error("Ошибка загрузки контента:", error);
        toast({ title: "Ошибка", description: "Не удалось загрузить контент книги.", variant: "destructive" });
    } finally {
        setIsLoadingContent(false);
    }
  };

  useEffect(() => {
    if (isOpen && hasHtmlFile) {
        loadBookContentForPreview();
    }
  }, [isOpen, hasHtmlFile]);

  const openBookInNewTab = async () => {
    if (!runId) return;
    
    try {
      const token = await getToken();
      const content = await api.getBookContent(runId, token || undefined);
      
      // Создаем новое окно с содержимым книги
      const newWindow = window.open('', '_blank');
      if (newWindow) {
        newWindow.document.write(content);
        newWindow.document.close();
      }
    } catch (error) {
      console.error('Error opening book:', error);
      toast({
        title: 'Ошибка',
        description: 'Не удалось открыть книгу',
        variant: 'destructive',
      });
    }
  };

  const downloadBook = async () => {
    if (!runId) return;
    
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

  const shareableUrl = `${window.location.origin}/view/${runId}/book.html`;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(shareableUrl);
    setIsCopied(true);
    toast({
      title: 'Ссылка скопирована!',
      description: 'Внимание: для просмотра потребуется авторизация.',
    });
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handleBackFromReader = () => {
    setIsEditing(false);
    onOpenChange(true);
  };

  if (isEditing) {
    return (
      <Dialog open={true} onOpenChange={(open) => !open && setIsEditing(false)}>
        <DialogContent className="max-w-full w-full h-full max-h-full p-0 gap-0">
          <BookReader runId={runId} onBack={handleBackFromReader} />
        </DialogContent>
      </Dialog>
    );
  }

  if (!runId || !status) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] bg-white border-none rounded-xl shadow-2xl">
        <DialogHeader className="text-center pt-4">
          <DialogTitle className="text-3xl font-normal text-violet-600">
            Книга готова!
          </DialogTitle>
          <DialogDescription className="text-muted-foreground">
            Ваша персональная история создана и готова к просмотру.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          <div className="relative border bg-white rounded-lg overflow-hidden h-[60vh]">
            {isLoadingContent ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center space-y-2">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-600 mx-auto"></div>
                  <p className="text-sm text-muted-foreground">Загружаем вашу книгу...</p>
                </div>
              </div>
            ) : (
              <div className="h-full overflow-auto p-6 book-content">
                <div dangerouslySetInnerHTML={{ __html: bookContent }} />
              </div>
            )}
          </div>

          <div className="space-y-4">
            <div className="bg-green-50 p-4 rounded-lg border border-green-200">
              <div className="flex items-center gap-2 text-green-800">
                <Check className="h-5 w-5" />
                <div>
                  <p className="font-semibold">Книга автоматически сохранена!</p>
                  <p className="text-sm text-green-700">
                    Ваша книга уже добавлена в раздел "Мои книги" и доступна в любое время
                  </p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button onClick={openBookInNewTab} size="lg" className="h-16">
                <ExternalLink className="h-5 w-5 mr-2" />
                <div className="text-left">
                  <div className="font-semibold">Открыть в новой вкладке</div>
                  <div className="text-xs opacity-80">Полноэкранный режим</div>
                </div>
              </Button>
              
              <Button onClick={downloadBook} variant="outline" size="lg" className="h-16">
                <Download className="h-5 w-5 mr-2" />
                <div className="text-left">
                  <div className="font-semibold">Скачать PDF</div>
                  <div className="text-xs opacity-80">Сохранить на устройство</div>
                </div>
              </Button>

              {hasHtmlFile && (
                <Button onClick={() => setIsEditing(true)} variant="secondary" size="lg" className="h-16">
                  <Pencil className="h-5 w-5 mr-2" />
                  <div className="text-left">
                    <div className="font-semibold">Редактировать</div>
                    <div className="text-xs opacity-80">С помощью AI</div>
                  </div>
                </Button>
              )}
            </div>
          </div>

          {profile && (
            <div className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm bg-slate-50/50 p-4 rounded-lg border">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Users className="h-4 w-4 text-slate-400" />
                <span className="font-medium text-black">Пользователь:</span> @{profile.username}
              </div>
              <div className="flex items-center gap-2 text-muted-foreground">
                <FileText className="h-4 w-4 text-slate-400" />
                <span className="font-medium text-black">Имя:</span> {profile.fullName}
              </div>
               <div className="flex items-center gap-2 text-muted-foreground">
                <Users className="h-4 w-4 text-slate-400" />
                <span className="font-medium text-black">Подписчики:</span> {profile.followers}
              </div>
               <div className="flex items-center gap-2 text-muted-foreground">
                <FileText className="h-4 w-4 text-slate-400" />
                <span className="font-medium text-black">Постов:</span> {profile.posts}
              </div>
            </div>
          )}

          <div>
             <p className="text-sm font-medium mb-2">Ссылка для поделиться</p>
             <div className="relative">
                <Input readOnly value={shareableUrl} className="pr-12 bg-slate-100"/>
                <Button variant="ghost" size="icon" className="absolute top-1/2 right-1 -translate-y-1/2" onClick={copyToClipboard}>
                    {isCopied ? <Check className="h-4 w-4 text-green-500"/> : <ClipboardCopy className="h-4 w-4" />}
                    <span className="sr-only">Скопировать ссылку</span>
                </Button>
             </div>
             <p className="text-xs text-muted-foreground mt-1">
               ⚠️ Для просмотра по ссылке потребуется авторизация в системе
             </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
} 
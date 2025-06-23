import { useState, useMemo } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import {
  ClipboardCopy,
  ExternalLink,
  Users,
  FileText,
  Check,
  Expand,
  Shrink,
} from 'lucide-react';
import { api, type StatusResponse } from '@/lib/api';

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
  const [isFullScreen, setIsFullScreen] = useState(false);

  const profile = status?.profile;
  const htmlUrl = useMemo(() => (runId ? api.getViewUrl(runId) : ''), [runId]);
  const hasHtmlFile = status?.stages.book_generated || status?.files?.html;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(htmlUrl);
    setIsCopied(true);
    toast({
      title: 'Ссылка скопирована!',
      description: 'Вы можете поделиться ей с кем угодно.',
    });
    setTimeout(() => setIsCopied(false), 2000);
  };
  
  if (!runId || !status) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent
        className={`bg-white border-none transition-all duration-300 ease-in-out ${
          isFullScreen
            ? 'w-screen h-screen max-w-full'
            : 'max-w-lg rounded-xl shadow-2xl sm:max-w-[540px]'
        }`}
      >
        <DialogHeader className="text-center pt-4">
          <DialogTitle className="text-3xl font-normal text-violet-600">
            🎉 Книга готова!
          </DialogTitle>
          <DialogDescription className="text-muted-foreground">
            Ваша персональная история создана и готова к просмотру.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          <Tabs defaultValue={hasHtmlFile ? "embed" : "newtab"} className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-slate-100">
              {hasHtmlFile && <TabsTrigger value="embed">Встроенный просмотр</TabsTrigger>}
              <TabsTrigger value="newtab" className={!hasHtmlFile ? 'col-span-2' : ''}>
                Открыть в новой вкладке
              </TabsTrigger>
            </TabsList>
            
            {hasHtmlFile && (
               <TabsContent value="embed">
                <div className={`relative border bg-slate-50 rounded-lg overflow-hidden transition-all ${isFullScreen ? 'h-[calc(100vh-180px)]' : 'h-[60vh]'}`}>
                  <div className="absolute top-2 right-2 z-10">
                    <Button variant="ghost" size="icon" onClick={() => setIsFullScreen(!isFullScreen)}>
                      {isFullScreen ? <Shrink className="h-4 w-4" /> : <Expand className="h-4 w-4" />}
                      <span className="sr-only">{isFullScreen ? 'Свернуть' : 'Развернуть'}</span>
                    </Button>
                  </div>
                  <iframe
                    src={htmlUrl}
                    loading="lazy"
                    className="w-full h-full border-0"
                    title="Ваша романтическая книга"
                  />
                </div>
              </TabsContent>
            )}
           
            <TabsContent value="newtab">
              <div className="text-center py-10 flex flex-col items-center justify-center space-y-4 bg-slate-50 rounded-lg border">
                 <p className="text-muted-foreground">Нажмите, чтобы открыть книгу в новой вкладке.</p>
                 <Button asChild size="lg">
                    <a href={htmlUrl} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="h-4 w-4 mr-2" /> Открыть книгу
                    </a>
                </Button>
              </div>
            </TabsContent>
          </Tabs>

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
             <p className="text-sm font-medium mb-2">Ссылка для копирования</p>
             <div className="relative">
                <Input readOnly value={htmlUrl} className="pr-12 bg-slate-100"/>
                <Button variant="ghost" size="icon" className="absolute top-1/2 right-1 -translate-y-1/2" onClick={copyToClipboard}>
                    {isCopied ? <Check className="h-4 w-4 text-green-500"/> : <ClipboardCopy className="h-4 w-4" />}
                    <span className="sr-only">Скопировать ссылку</span>
                </Button>
             </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
} 
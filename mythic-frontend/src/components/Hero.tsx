import { Badge } from '@/components/ui/badge';
import { Instagram, Zap, BookOpen } from 'lucide-react';

export function Hero() {
  return (
    <section className="py-20 px-4">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-5xl md:text-6xl font-semibold italic text-black mb-6" style={{ fontFamily: 'Playfair Display, serif' }}>
          Создайте романтическую книгу
        </h1>
        
        <p className="text-xl text-gray-600 mb-4 max-w-2xl mx-auto">
          Превратите Instagram профиль в прекрасную книгу
        </p>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          с помощью искусственного интеллекта
        </p>

        <div className="flex justify-center gap-3 flex-wrap">
          <Badge variant="secondary" className="px-4 py-2 bg-gray-100 text-gray-800 hover:bg-gray-200">
            <Instagram className="h-4 w-4 mr-2" />
            Instagram
          </Badge>
          <Badge variant="secondary" className="px-4 py-2 bg-gray-100 text-gray-800 hover:bg-gray-200">
            <Zap className="h-4 w-4 mr-2" />
            AI-генерация
          </Badge>
          <Badge variant="secondary" className="px-4 py-2 bg-gray-100 text-gray-800 hover:bg-gray-200">
            <BookOpen className="h-4 w-4 mr-2" />
            HTML-книга
          </Badge>
        </div>
      </div>
    </section>
  );
} 
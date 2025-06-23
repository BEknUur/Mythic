import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Camera, Palette, BookOpen } from 'lucide-react';

const steps = [
  {
    icon: Camera,
    title: 'Анализ фото',
    description: 'Собираем красивые фотографии из Instagram профиля'
  },
  {
    icon: Palette,
    title: 'ИИ-текст',
    description: 'Создаем романтическую историю с помощью искусственного интеллекта'
  },
  {
    icon: BookOpen,
    title: 'HTML-книга',
    description: 'Генерируем красивую веб-книгу для просмотра и скачивания'
  }
];

export function Steps() {
  return (
    <section className="py-16 px-4 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, index) => {
            const IconComponent = step.icon;
            return (
              <Card key={index} className="bg-white border border-gray-200 hover:shadow-md transition-shadow">
                <CardHeader className="text-center pb-4">
                  <div className="mx-auto w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mb-4">
                    <IconComponent className="h-6 w-6 text-gray-700" />
                  </div>
                  <CardTitle className="text-xl text-black">{step.title}</CardTitle>
                </CardHeader>
                <CardContent className="text-center">
                  <CardDescription className="text-gray-600">
                    {step.description}
                  </CardDescription>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
} 
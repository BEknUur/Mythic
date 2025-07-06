import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Camera, Bot, BookHeart } from 'lucide-react';

const steps = [
  {
    icon: Camera,
    title: 'Анализ фото',
    description: 'Собираем самые яркие и красивые фотографии из вашего Instagram профиля.'
  },
  {
    icon: Bot,
    title: 'Магия ИИ',
    description: 'Создаем уникальную и трогательную историю вашей любви с помощью ИИ.'
  },
  {
    icon: BookHeart,
    title: 'Ваша книга',
    description: 'Генерируем красивую онлайн-книгу, которую можно читать и скачивать.'
  }
];

export function Steps() {
  return (
    <section className="py-20 px-4 bg-white">
      <div className="max-w-6xl mx-auto text-center">
        <h2 className="text-4xl font-bold text-gray-900 mb-4 tracking-tighter">Всего 3 шага к вашей истории</h2>
        <p className="text-lg text-gray-500 mb-12 max-w-2xl mx-auto">
          Наш процесс прост и прозрачен. Мы превращаем ваши воспоминания в нечто волшебное.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, index) => {
            const IconComponent = step.icon;
            return (
              <div key={index} className="text-left p-6 border border-gray-100 rounded-xl hover:shadow-lg transition-shadow duration-300 animate-fade-in-up" style={{ animationDelay: `${index * 200}ms` }}>
                <div className="mb-4">
                  <IconComponent className="h-10 w-10 text-purple-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">{step.title}</h3>
                <p className="text-gray-500">{step.description}</p>
                  </div>
            );
          })}
        </div>
      </div>
    </section>
  );
} 
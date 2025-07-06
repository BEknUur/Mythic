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
    <section className="py-20 sm:py-28 px-4 bg-gray-50 dark:bg-gray-950">
      <div className="max-w-6xl mx-auto text-center">
        <div className="inline-block rounded-full bg-purple-100 dark:bg-purple-900/40 px-4 py-1.5 mb-4">
          <p className="text-sm font-semibold text-purple-700 dark:text-purple-300 tracking-wide">
            Как это работает
          </p>
        </div>
        <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-gray-50 mb-4 tracking-tighter">
          <span className="bg-gradient-to-br from-purple-600 to-pink-500 bg-clip-text text-transparent">Всего 3 шага</span> к вашей истории
        </h2>
        <p className="text-lg text-gray-600 dark:text-gray-400 mb-16 max-w-2xl mx-auto">
          Наш процесс прост и прозрачен. Мы превращаем ваши воспоминания в нечто волшебное.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, index) => {
            const IconComponent = step.icon;
            return (
              <div 
                key={index} 
                className="relative overflow-hidden text-left p-6 rounded-2xl group transition-all duration-300 ease-in-out hover:scale-[1.02] bg-white dark:bg-gray-900/60 border border-gray-200 dark:border-gray-800/80 animate-fade-in-up" 
                style={{ animationDelay: `${index * 150}ms` }}
              >
                {/* Glow effect for dark mode */}
                <div className="hidden dark:block absolute -inset-px rounded-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100 bg-[radial-gradient(400px_at_center,rgba(168,85,247,0.15),transparent_80%)]"></div>
                
                {/* A different glow for light mode */}
                <div className="dark:hidden absolute -inset-px rounded-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100 bg-[radial-gradient(400px_at_center,rgba(168,85,247,0.1),transparent_80%)]"></div>

                <div className="relative">
                    <div className="mb-4 inline-block p-3 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                        <IconComponent className="h-8 w-8 text-purple-600 dark:text-purple-400" />
                    </div>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-gray-50 mb-2">{step.title}</h3>
                    <p className="text-gray-500 dark:text-gray-400">{step.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
} 
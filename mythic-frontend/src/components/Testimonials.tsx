import React from 'react';

const testimonials = [
  {
    name: 'Айзере',
    handle: '@aizerek',
    avatar: 'https://avatar.iran.liara.run/public/girl?username=aizere',
    text: 'Это просто невероятно! Мы с парнем были в восторге. Книга получилась очень личной и трогательной, собраны все самые важные моменты. Спасибо за такие эмоции!',
  },
  {
    name: 'Алихан',
    handle: '@alikhan',
    avatar: 'https://avatar.iran.liara.run/public/boy?username=alikhan',
    text: 'Сделал подарок своей девушке на годовщину. Она была в шоке! Сказала, что это лучший подарок за все время. Сервис работает быстро, результат превзошел все ожидания.',
  },
  {
    name: 'Мадина',
    handle: '@madina_m',
    avatar: 'https://avatar.iran.liara.run/public/girl?username=madina',
    text: 'Изначально отнеслась скептически, но результат меня поразил. ИИ так точно подобрал подписи к фото и создал красивую историю. Теперь советую всем подругам!',
  },
  {
    name: 'Тимур',
    handle: '@timur.pro',
    avatar: 'https://avatar.iran.liara.run/public/boy?username=timur',
    text: 'Очень удобный и понятный интерфейс. Буквально в несколько кликов получил готовую книгу. Качество на высоте, и веб-версия, и PDF выглядят отлично.',
  },
  {
    name: 'Диана',
    handle: '@di.di',
    avatar: 'https://avatar.iran.liara.run/public/girl?username=diana',
    text: 'Это идеальный способ сохранить цифровые воспоминания. Гораздо круче, чем просто фотоальбом. История получилась очень живой, как будто заново все пережила.',
  },
  {
    name: 'Санжар',
    handle: '@sanzhar_b',
    avatar: 'https://avatar.iran.liara.run/public/boy?username=sanzhar',
    text: 'Поддержка на высоте! Были небольшие вопросы по процессу, ответили очень быстро и помогли. Сам продукт — 10/10. Обязательно воспользуюсь еще раз.',
  },
];

export function Testimonials() {
  return (
    <section className="py-20 sm:py-28 px-4 bg-white dark:bg-gray-950">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-gray-50 mb-4 tracking-tighter">
            Что говорят наши клиенты
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Отзывы от первых пользователей, которые уже превратили свои воспоминания в книгу.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <div 
              key={index}
              className="p-8 rounded-2xl bg-gray-50 dark:bg-gray-900 border border-gray-100 dark:border-gray-800/80 animate-fade-in-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex items-center gap-4 mb-4">
                <img src={testimonial.avatar} alt={testimonial.name} className="w-12 h-12 rounded-full object-cover" />
                <div>
                  <h3 className="font-bold text-gray-900 dark:text-gray-50">{testimonial.name}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{testimonial.handle}</p>
                </div>
              </div>
              <p className="text-gray-700 dark:text-gray-300">
                {testimonial.text}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
} 
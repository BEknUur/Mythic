import React, { createContext, useContext, useState, useEffect } from 'react';

export type Language = 'ru' | 'en';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// Переводы
const translations = {
  ru: {
    // Header
    'mythic.title': 'Mythic AI',
    'mythic.subtitle': 'Создаём истории',
    
    // Navigation
    'nav.create': 'Создать',
    'nav.create.book': 'Создать книгу',
    'nav.create.tiktok': 'Книга → TikTok',
    'nav.library': 'Библиотека',
    'nav.library.books': 'Мои книги',
    'nav.pricing': 'Тарифы',
    'nav.help': 'Помощь',
    'nav.new': 'Новое',
    
    // Authentication
    'auth.register': 'Регистрация',
    'auth.login': 'Войти',
    'auth.hello': 'Привет',
    'auth.user': 'Пользователь',
    'auth.required': 'Требуется регистрация для продолжения',
    
    // Homepage
    'home.title': 'Превратите ваш',
    'home.instagram': 'Instagram',
    'home.subtitle': 'в книгу',
    'home.description': 'Сохраните вашу цифровую историю любви в уникальной книге, созданной искусственным интеллектом.',
    'home.gift': 'Идеальный подарок для вашего партнера.',
    'home.start': 'Начать создание',
    'home.how': 'Как это работает?',
    'home.analyze': 'Анализ фото',
    'home.magic': 'Магия ИИ',
    'home.book': 'Ваша книга',
    'home.badge': 'Создано с любовью и AI',
    
    // Testimonials
    'testimonials.title': 'Что говорят о Mythic AI',
    'testimonials.subtitle': 'Реальные отзывы пользователей, которые уже создали свою фэнтези-книгу с помощью Mythic AI.',
    
    // Pricing
    'pricing.title': 'Выберите свой план',
    'pricing.subtitle': 'Начните бесплатно и переходите на Pro, когда будете готовы к безграничному творчеству.',
    'pricing.single_info': 'После бесплатных генераций каждая новая генерация книги (Classic или Flipbook) стоит',
    'pricing.single_button': 'Оплатить одну генерацию ($0.99)',
    'pricing.free.name': 'Бесплатно',
    'pricing.free.price': '$0',
    'pricing.free.frequency': 'навсегда',
    'pricing.free.description': 'Две бесплатные генерации: одна Classic и одна Flipbook. Дальнейшие генерации — платные.',
    'pricing.free.cta': 'Начать бесплатно',
    'pricing.pro.name': 'Pro',
    'pricing.pro.price': '$9.99',
    'pricing.pro.frequency': '/ месяц',
    'pricing.pro.description': 'Раскройте полный потенциал и создавайте неограниченное количество историй.',
    'pricing.pro.cta': 'Перейти на Pro',
    'pricing.popular': 'Самый популярный',
    'pricing.loading': 'Загрузка...',
    'pricing.features.free.1': '1 бесплатная генерация Classic',
    'pricing.features.free.2': '1 бесплатная генерация Flipbook',
    'pricing.features.free.3': 'Веб-версия книги',
    'pricing.features.free.4': 'Возможность скачать PDF',
    'pricing.features.free.5': 'Стандартная поддержка',
    'pricing.features.pro.1': 'Неограниченные генерации книг',
    'pricing.features.pro.2': 'Приоритетная обработка',
    'pricing.features.pro.3': 'Доступ к премиум-стилям',
    'pricing.features.pro.4': 'Создание видео для TikTok (скоро)',
    'pricing.features.pro.5': 'Приоритетная поддержка',
    
    // Library
    'library.title': 'Мои книги',
    'library.subtitle': 'Все ваши созданные книги',
    'library.back': 'Назад',
    'library.loading': 'Загружаем ваши книги...',
    'library.empty.title': 'Пока нет книг',
    'library.empty.description': 'Создайте свою первую книгу, чтобы она появилась здесь',
    'library.empty.button': 'Создать книгу',
    'library.stats.books': 'книг',
    'library.stats.pdfs': 'PDF файлов',
    'library.stats.webs': 'веб-версий',
    'library.read': 'Читать',
    'library.flipbook': 'Flipbook',
    'library.download': 'PDF',
    'library.delete': 'Удалить',
    'library.delete_confirm': 'Вы уверены, что хотите удалить эту книгу?',
    'library.badges.web': 'Веб-версия',
    'library.badges.pdf': 'PDF',
    'library.toast.downloaded': 'Книга скачана',
    'library.toast.deleted': 'Книга удалена',
    'library.toast.error.download': 'Не удалось скачать книгу',
    'library.toast.error.delete': 'Не удалось удалить книгу',
    'library.toast.error.open': 'Не удалось открыть книгу',
    'library.toast.error.auth': 'Нужно войти в аккаунт',
    
    // Help
    'help.title': 'Центр помощи',
    'help.subtitle': 'Найдите ответы на свои вопросы или свяжитесь с нами.',
    'help.faq.title': 'Часто задаваемые вопросы',
    'help.contact.title': 'Остались вопросы?',
    'help.contact.email.title': 'Написать на почту',
    'help.contact.email.description': 'Лучший способ для подробных вопросов. Мы отвечаем в течение 24 часов.',
    'help.contact.telegram.title': 'Написать в Telegram',
    'help.contact.telegram.description': 'Идеально для быстрых вопросов и оперативной поддержки.',
    'help.faq.1.question': 'Как именно работает сервис?',
    'help.faq.1.answer': 'Мы анализируем ваш открытый профиль в Instagram, собираем фотографии и информацию, а затем наш искусственный интеллект создает на их основе уникальную романтическую историю. В результате вы получаете красивую веб-книгу.',
    'help.faq.2.question': 'Какие данные из Instagram вы используете?',
    'help.faq.2.answer': 'Мы используем только общедоступную информацию: ваши фотографии, подписи к ним и даты публикаций. Мы не собираем и не храним личные данные, такие как пароли или переписки.',
    'help.faq.3.question': 'Сколько времени занимает создание книги?',
    'help.faq.3.answer': 'Обычно процесс занимает от 1до 5 минут в зависимости от количества фотографий в вашем профиле и текущей нагрузки на сервер. Вы получите уведомление, когда ваша книга будет готова.',
    'help.faq.4.question': 'Можно ли использовать закрытый (приватный) профиль?',
    'help.faq.4.answer': 'К сожалению, на данный момент мы можем анализировать только открытые профили Instagram. Пожалуйста, убедитесь, что ваш профиль является общедоступным на время создания книги.',
    
    // TikTok
    'tiktok.title': 'Книга → TikTok',
    'tiktok.description': 'Этот раздел находится в активной разработке. Совсем скоро вы сможете превращать ваши книги в захватывающие TikTok-видео!',
    
    // Form
    'form.title': 'Создайте вашу книгу',
    'form.subtitle': 'Создайте книгу с полным доступом',
    'form.instagram_label': 'Instagram профиль',
    'form.instagram_placeholder': 'ualikhaanuly',
    'form.instagram_help': 'Просто введите username (например: ualikhaanuly) или полную ссылку',
    'form.style_label': 'Выберите стиль книги',
    'form.create_button': 'Создать книгу',
    'form.data_security': 'Ваши данные в безопасности.',
    'form.loading': 'Проверяем профиль...',
    'form.checking': 'Проверяем соединение...',
    'form.invalid_url': 'Введите корректный Instagram профиль',
    'form.private_profile': 'Профиль закрыт. Пожалуйста, сделайте его открытым для создания книги.',
    'form.connection_error': 'Не удалось подключиться к Instagram. Попробуйте позже.',
    'form.error.auth': 'Необходима авторизация',
    'form.error.generation': 'Ошибка при создании книги',
    'form.success': 'Книга создается!',
    'form.progress_message': 'Процесс создания начался, переходим к отслеживанию...',
    'form.sign_in_required': 'Войдите, чтобы создать книгу',
    'form.sign_in_button': 'Войти',
    'form.features.personal': 'Персональная история',
    'form.features.ai': 'Магия ИИ',
    'form.features.pdf': 'PDF + Веб-версия',
    'form.features.instant': 'Мгновенное создание',
    'form.how_it_works': 'Как это работает',
    'form.step1': 'Анализ профиля',
    'form.step1_desc': 'Мы изучаем ваши фото и создаем персонажей',
    'form.step2': 'Создание истории',
    'form.step2_desc': 'ИИ пишет уникальную историю на основе ваших воспоминаний',
    'form.step3': 'Готовая книга',
    'form.step3_desc': 'Получите красивую книгу в PDF и веб-формате',
    'form.hero_title': 'Создайте Романтическую Книгу',
    'form.hero_description': 'Превратите Instagram профиль в прекрасную романтическую книгу с помощью искусственного интеллекта',
    'form.hero_free_trial': '📖 Попробуйте бесплатно - просмотрите первые 10 страниц!',
    'form.premium_text': 'Требует авторизацию',
    'form.start_title': 'Начните создание книги',
    'form.start_description_signed_in': 'Введите ссылку на Instagram профиль для создания полной романтической книги',
    'form.start_description_signed_out': 'Введите ссылку на Instagram профиль и попробуйте бесплатно первые 10 страниц',
    'form.checking_connection': 'Проверяем соединение...',
    'form.connection_established': 'Соединение установлено',
    'form.check_connection': 'Проверить соединение',
    'form.preview_mode_title': 'Режим предварительного просмотра',
    'form.preview_mode_description': 'Вы можете создать книгу и просмотреть первые 10 страниц бесплатно. Для полного доступа ко всем страницам и возможности сохранения требуется авторизация.',
    'form.sign_in_for_full_access': 'Войти для полного доступа',
    'form.instagram_url_label': 'Ссылка на Instagram профиль',
    'form.instagram_url_placeholder': 'https://instagram.com/username',
    'form.instagram_url_example': 'Например: https://instagram.com/username или https://www.instagram.com/username',
    'form.creating_book': 'Создаем книгу...',
    'form.create_romantic_book': 'Создать романтическую книгу',
    'form.try_free_10_pages': 'Попробовать бесплатно (10 страниц)',
    'form.how_it_works_title': '💡 Как это работает:',
    'form.how_it_works_step1': 'Мы анализируем открытый Instagram профиль',
    'form.how_it_works_step2': 'Собираем красивые фотографии и информацию',
    'form.how_it_works_step3': 'ИИ создает романтическую историю на основе контента',
    'form.how_it_works_step4': 'Генерируем красивую HTML книгу для просмотра',
    'form.how_it_works_free_trial': '• 📖 Без авторизации: доступ к первым 10 страницам',
    'form.connection_success': '✅ Соединение установлено',
    'form.connection_success_desc': 'Сервер готов к работе',
    'form.connection_error_desc': 'Не удается подключиться к серверу',
    
    // Footer
    'footer.tagline': 'Превращаем мысли в истории',
    'footer.contact': 'Связь: t.me/beknur_10',
    'footer.description': 'Превращаем ваши цифровые воспоминания в вечные истории.',
    'footer.nav.title': 'Навигация',
    'footer.nav.home': 'Главная',
    'footer.nav.create': 'Создать книгу',
    'footer.nav.library': 'Мои книги',
    'footer.help.title': 'Помощь',
    'footer.help.faq': 'FAQ',
    'footer.help.support': 'Поддержка',
    'footer.social.title': 'Следите за нами',
    'footer.made_with': 'Brought to you with',
    'footer.by': 'by',
    'footer.backed_by': 'Backed by',
    
    // Common
    'common.scroll_to_features': 'Прокрутить к функциям',
    'common.error': 'Ошибка',
    'common.success': 'Готово',
    'common.loading': 'Загрузка...',
  },
  en: {
    // Header
    'mythic.title': 'Mythic AI',
    'mythic.subtitle': 'Creating stories',
    
    // Navigation
    'nav.create': 'Create',
    'nav.create.book': 'Create book',
    'nav.create.tiktok': 'Book → TikTok',
    'nav.library': 'Library',
    'nav.library.books': 'My books',
    'nav.pricing': 'Pricing',
    'nav.help': 'Help',
    'nav.new': 'New',
    
    // Authentication
    'auth.register': 'Register',
    'auth.login': 'Login',
    'auth.hello': 'Hello',
    'auth.user': 'User',
    'auth.required': 'Registration required to continue',
    
    // Homepage
    'home.title': 'Turn your',
    'home.instagram': 'Instagram',
    'home.subtitle': 'into a book',
    'home.description': 'Preserve your digital love story in a unique book, created by artificial intelligence.',
    'home.gift': 'Perfect gift for your partner.',
    'home.start': 'Start creating',
    'home.how': 'How it works?',
    'home.analyze': 'Photo analysis',
    'home.magic': 'AI Magic',
    'home.book': 'Your book',
    'home.badge': 'Created with love and AI',
    
    // Testimonials
    'testimonials.title': 'What people say about Mythic AI',
    'testimonials.subtitle': 'Real reviews from users who have already created their fantasy book with Mythic AI.',
    
    // Pricing
    'pricing.title': 'Choose your plan',
    'pricing.subtitle': 'Start for free and upgrade to Pro when you\'re ready for unlimited creativity.',
    'pricing.single_info': 'After free generations, each new book generation (Classic or Flipbook) costs',
    'pricing.single_button': 'Pay for one generation ($0.99)',
    'pricing.free.name': 'Free',
    'pricing.free.price': '$0',
    'pricing.free.frequency': 'forever',
    'pricing.free.description': 'Two free generations: one Classic and one Flipbook. Further generations are paid.',
    'pricing.free.cta': 'Start free',
    'pricing.pro.name': 'Pro',
    'pricing.pro.price': '$9.99',
    'pricing.pro.frequency': '/ month',
    'pricing.pro.description': 'Unlock full potential and create unlimited stories.',
    'pricing.pro.cta': 'Upgrade to Pro',
    'pricing.popular': 'Most popular',
    'pricing.loading': 'Loading...',
    'pricing.features.free.1': '1 free Classic generation',
    'pricing.features.free.2': '1 free Flipbook generation',
    'pricing.features.free.3': 'Web version of book',
    'pricing.features.free.4': 'PDF download available',
    'pricing.features.free.5': 'Standard support',
    'pricing.features.pro.1': 'Unlimited book generations',
    'pricing.features.pro.2': 'Priority processing',
    'pricing.features.pro.3': 'Access to premium styles',
    'pricing.features.pro.4': 'TikTok video creation (coming soon)',
    'pricing.features.pro.5': 'Priority support',
    
    // Library
    'library.title': 'My books',
    'library.subtitle': 'All your created books',
    'library.back': 'Back',
    'library.loading': 'Loading your books...',
    'library.empty.title': 'No books yet',
    'library.empty.description': 'Create your first book to see it here',
    'library.empty.button': 'Create book',
    'library.stats.books': 'books',
    'library.stats.pdfs': 'PDF files',
    'library.stats.webs': 'web versions',
    'library.read': 'Read',
    'library.flipbook': 'Flipbook',
    'library.download': 'PDF',
    'library.delete': 'Delete',
    'library.delete_confirm': 'Are you sure you want to delete this book?',
    'library.badges.web': 'Web version',
    'library.badges.pdf': 'PDF',
    'library.toast.downloaded': 'Book downloaded',
    'library.toast.deleted': 'Book deleted',
    'library.toast.error.download': 'Failed to download book',
    'library.toast.error.delete': 'Failed to delete book',
    'library.toast.error.open': 'Failed to open book',
    'library.toast.error.auth': 'Need to log in',
    
    // Help
    'help.title': 'Help Center',
    'help.subtitle': 'Find answers to your questions or contact us.',
    'help.faq.title': 'Frequently Asked Questions',
    'help.contact.title': 'Still have questions?',
    'help.contact.email.title': 'Send email',
    'help.contact.email.description': 'Best way for detailed questions. We respond within 24 hours.',
    'help.contact.telegram.title': 'Write on Telegram',
    'help.contact.telegram.description': 'Perfect for quick questions and prompt support.',
    'help.faq.1.question': 'How exactly does the service work?',
    'help.faq.1.answer': 'We analyze your public Instagram profile, collect photos and information, and then our artificial intelligence creates a unique romantic story based on them. As a result, you get a beautiful web book.',
    'help.faq.2.question': 'What Instagram data do you use?',
    'help.faq.2.answer': 'We only use publicly available information: your photos, their captions, and publication dates. We do not collect or store personal data such as passwords or messages.',
    'help.faq.3.question': 'How long does it take to create a book?',
    'help.faq.3.answer': 'Usually the process takes from 1 to 5 minutes depending on the number of photos in your profile and current server load. You will get a notification when your book is ready.',
    'help.faq.4.question': 'Can I use a private profile?',
    'help.faq.4.answer': 'Unfortunately, at the moment we can only analyze public Instagram profiles. Please make sure your profile is public during book creation.',
    
    // TikTok
    'tiktok.title': 'Book → TikTok',
    'tiktok.description': 'This section is in active development. Soon you will be able to turn your books into exciting TikTok videos!',
    
    // Form
    'form.title': 'Create your book',
    'form.subtitle': 'Create book with full access',
    'form.instagram_label': 'Instagram profile',
    'form.instagram_placeholder': 'ualikhaanuly',
    'form.instagram_help': 'Just enter username (example: ualikhaanuly) or full link',
    'form.style_label': 'Choose book style',
    'form.create_button': 'Create book',
    'form.data_security': 'Your data is secure.',
    'form.loading': 'Checking profile...',
    'form.checking': 'Checking connection...',
    'form.invalid_url': 'Enter a valid Instagram profile',
    'form.private_profile': 'Profile is private. Please make it public to create a book.',
    'form.connection_error': 'Failed to connect to Instagram. Try again later.',
    'form.error.auth': 'Authorization required',
    'form.error.generation': 'Error creating book',
    'form.success': 'Book is being created!',
    'form.progress_message': 'Creation process started, moving to tracking...',
    'form.sign_in_required': 'Sign in to create a book',
    'form.sign_in_button': 'Sign in',
    'form.features.personal': 'Personal story',
    'form.features.ai': 'AI Magic',
    'form.features.pdf': 'PDF + Web version',
    'form.features.instant': 'Instant creation',
    'form.how_it_works': 'How it works',
    'form.step1': 'Profile analysis',
    'form.step1_desc': 'We study your photos and create characters',
    'form.step2': 'Story creation',
    'form.step2_desc': 'AI writes a unique story based on your memories',
    'form.step3': 'Ready book',
    'form.step3_desc': 'Get a beautiful book in PDF and web format',
    'form.hero_title': 'Create a Romantic Book',
    'form.hero_description': 'Turn your Instagram profile into a beautiful romantic book using artificial intelligence',
    'form.hero_free_trial': '📖 Try for free - preview the first 10 pages!',
    'form.premium_text': 'Requires authentication',
    'form.start_title': 'Start creating a book',
    'form.start_description_signed_in': 'Enter your Instagram profile link to create a full romantic book',
    'form.start_description_signed_out': 'Enter your Instagram profile link and try for free first 10 pages',
    'form.checking_connection': 'Checking connection...',
    'form.connection_established': 'Connection established',
    'form.check_connection': 'Check connection',
    'form.preview_mode_title': 'Preview mode',
    'form.preview_mode_description': 'You can create a book and preview the first 10 pages for free. Full access to all pages and the ability to save requires authentication.',
    'form.sign_in_for_full_access': 'Sign in for full access',
    'form.instagram_url_label': 'Instagram profile link',
    'form.instagram_url_placeholder': 'https://instagram.com/username',
    'form.instagram_url_example': 'For example: https://instagram.com/username or https://www.instagram.com/username',
    'form.creating_book': 'Creating book...',
    'form.create_romantic_book': 'Create a romantic book',
    'form.try_free_10_pages': 'Try for free (10 pages)',
    'form.how_it_works_title': '💡 How it works:',
    'form.how_it_works_step1': 'We analyze your public Instagram profile',
    'form.how_it_works_step2': 'Collect beautiful photos and information',
    'form.how_it_works_step3': 'AI creates a romantic story based on the content',
    'form.how_it_works_step4': 'Generate a beautiful HTML book for viewing',
    'form.how_it_works_free_trial': '• 📖 No authentication: access to the first 10 pages',
    'form.connection_success': '✅ Connection established',
    'form.connection_success_desc': 'Server is ready to work',
    'form.connection_error_desc': 'Unable to connect to server',
    
    // Footer
    'footer.tagline': 'Turning thoughts into stories',
    'footer.contact': 'Contact: t.me/beknur_10',
    'footer.description': 'Turning your digital memories into eternal stories.',
    'footer.nav.title': 'Navigation',
    'footer.nav.home': 'Home',
    'footer.nav.create': 'Create book',
    'footer.nav.library': 'My books',
    'footer.help.title': 'Help',
    'footer.help.faq': 'FAQ',
    'footer.help.support': 'Support',
    'footer.social.title': 'Follow us',
    'footer.made_with': 'Brought to you with',
    'footer.by': 'by',
    'footer.backed_by': 'Backed by',
    
    // Common
    'common.scroll_to_features': 'Scroll to features',
    'common.error': 'Error',
    'common.success': 'Success',
    'common.loading': 'Loading...',
  }
};

interface LanguageProviderProps {
  children: React.ReactNode;
}

export function LanguageProvider({ children }: LanguageProviderProps) {
  const [language, setLanguage] = useState<Language>(() => {
    const saved = localStorage.getItem('language');
    return (saved as Language) || 'ru';
  });

  useEffect(() => {
    localStorage.setItem('language', language);
  }, [language]);

  const t = (key: string): string => {
    return translations[language][key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
} 
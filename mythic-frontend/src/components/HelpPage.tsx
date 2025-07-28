import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Mail, Send } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLanguage } from '@/contexts/LanguageContext';

export function HelpPage() {
  const { t } = useLanguage();

  const faqItems = [
    {
      question: t('help.faq.1.question'),
      answer: t('help.faq.1.answer')
    },
    {
      question: t('help.faq.2.question'),
      answer: t('help.faq.2.answer')
    },
    {
      question: t('help.faq.3.question'),
      answer: t('help.faq.3.answer')
    },
    {
      question: t('help.faq.4.question'),
      answer: t('help.faq.4.answer')
    }
  ];

  return (
    <div className="container mx-auto max-w-4xl py-12 px-4 dark:text-gray-100">
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-gray-50 tracking-tighter">{t('help.title')}</h1>
        <p className="mt-4 text-lg text-gray-500 dark:text-gray-400">{t('help.subtitle')}</p>
      </div>

      {/* FAQ Section */}
      <div className="mb-12">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-50 mb-6 text-center">{t('help.faq.title')}</h2>
        <Accordion type="single" collapsible className="w-full">
          {faqItems.map((item, index) => (
            <AccordionItem value={`item-${index}`} key={index} className="border-b dark:border-gray-800">
              <AccordionTrigger className="text-lg text-left hover:no-underline text-gray-800 dark:text-gray-200">
                {item.question}
              </AccordionTrigger>
              <AccordionContent>
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3, ease: 'easeInOut' }}
                  className="overflow-hidden"
                >
                  <p className="pt-2 pb-4 text-base text-gray-600 dark:text-gray-400">
                    {item.answer}
                  </p>
                </motion.div>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>

      {/* Contact Section */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-50 mb-6 text-center">{t('help.contact.title')}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <a href="mailto:beknur_10@gmail.com" className="group">
            <Card className="h-full hover:shadow-lg transition-shadow bg-white dark:bg-gray-900 border dark:border-gray-800">
              <CardHeader className="flex flex-row items-center gap-4">
                <Mail className="h-8 w-8 text-purple-600" />
                <CardTitle className="dark:text-gray-100">{t('help.contact.email.title')}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-500 dark:text-gray-400">
                  {t('help.contact.email.description')}
                </p>
                <p className="text-purple-600 font-semibold mt-4 group-hover:underline">
                  ualihanulybeknur@gmail.com
                </p>
              </CardContent>
            </Card>
          </a>
          <a href="https://t.me/beknur_10" target="_blank" rel="noopener noreferrer" className="group">
            <Card className="h-full hover:shadow-lg transition-shadow bg-white dark:bg-gray-900 border dark:border-gray-800">
              <CardHeader className="flex flex-row items-center gap-4">
                <Send className="h-8 w-8 text-purple-600" />
                <CardTitle className="dark:text-gray-100">{t('help.contact.telegram.title')}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-500 dark:text-gray-400">
                  {t('help.contact.telegram.description')}
                </p>
                <p className="text-purple-600 font-semibold mt-4 group-hover:underline">
                  @beknur_10
                </p>
              </CardContent>
            </Card>
          </a>
        </div>
      </div>
    </div>
  );
} 
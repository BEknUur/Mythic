"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { useLanguage } from '@/contexts/LanguageContext';

const testimonials = [
  {
    name: 'Tataev Shoqan',
    position: 'Middle frontend developer at BCC',
    avatar: 'https://framerusercontent.com/images/iLrfalodnhI8A941IO9W44vOSY.png?scale-down-to=512',
    text: 'Mythic AI — это магия! Книга получилась очень атмосферной, будто я сам герой эпоса. Такой сервис — находка для любителей фэнтези.',
  },
  {
    name: 'Bakhredin Zurgambayev',
    position: 'Middle Typescript Dev @ BCC',
    avatar: 'https://framerusercontent.com/images/A2fJNeM0qxgW0jDh9VrONNUhR0.png?scale-down-to=1024',
    text: 'Я загрузил свои фото, и Mythic AI создал целую сагу! Всё быстро, красиво и с крутым сюжетом. Рекомендую всем друзьям.',
  },
  {
    name: 'Alikhan Gubayev',
    position: 'iOS Developer @ 1fit',
    avatar: 'https://framerusercontent.com/images/2sSG4VoBlQEaePDvTvL05v78ILM.png?scale-down-to=512',
    text: 'Если бы раньше был Mythic AI, я бы давно сделал подарок родителям. Истории получаются живые, с настоящей магией!',
  },
  {
    name: 'Bahauddin Toleu',
    position: 'Python Developer @ Surfaice',
    avatar: 'https://framerusercontent.com/images/zCFUAudUGZqUahAAJ1dZIWiw.png?scale-down-to=1024',
    text: 'Я пробовал разные генераторы, но только Mythic AI сделал книгу, которую не стыдно показать. Очень круто, что можно добавить свои фото!',
  },
  {
    name: 'Alibek Seitov',
    position: 'SWE @ Higgsfield AI',
    avatar: 'https://framerusercontent.com/images/4HD8lzy7aVGnsg3UzYylfK66Os.png',
    text: 'PDF и веб-версия книги от Mythic AI — просто топ! Всё стильно, удобно и реально вдохновляет. Спасибо за сервис!',
  },
  {
    name: 'Aimurzat Zhetkizgenov',
    position: 'AI Engineer @ Surfaice',
    avatar: 'https://framerusercontent.com/images/DYhF6sKoTH39Bu8GAN0zrb13U.png?scale-down-to=512',
    text: 'Сделал книгу для девушки через Mythic AI — она была в восторге! Очень крутая идея для подарка и просто для себя.',
  },
];

export function Testimonials() {
  const { t } = useLanguage();
  
  return (
    <section className="py-20 sm:py-28 px-4 bg-white dark:bg-gray-950">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-gray-50 mb-4 tracking-tighter">
            {t('testimonials.title')}
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            {t('testimonials.subtitle')}
          </p>
        </div>
        <div className="overflow-hidden w-full">
          <motion.div
            className="flex gap-8"
            animate={{ x: ["0%", "-100%"] }}
            transition={{ repeat: Infinity, repeatType: "loop", duration: 20, ease: "linear" }}
          >
            {[...testimonials, ...testimonials].map((testimonial, index) => (
              <div
                key={index}
                className="min-w-[320px] p-8 rounded-2xl bg-gray-50 dark:bg-gray-900 border border-gray-100 dark:border-gray-800/80 flex flex-col"
              >
                <div className="flex items-center gap-4 mb-4">
                  <img
                    src={testimonial.avatar}
                    alt={testimonial.name}
                    className="w-12 h-12 rounded-full object-cover"
                  />
                  <div>
                    <h3 className="font-bold text-gray-900 dark:text-gray-50">
                      {testimonial.name}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {testimonial.position}
                    </p>
                  </div>
                </div>
                <p className="text-gray-700 dark:text-gray-300 flex-1">
                  {testimonial.text}
                </p>
              </div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
} 
import React from 'react';
import { ComingSoonPage } from './ComingSoonPage';
import { useLanguage } from '@/contexts/LanguageContext';

export function TikTokPage() {
  const { t } = useLanguage();
  
  return (
    <ComingSoonPage 
      title={t('tiktok.title')}
      description={t('tiktok.description')}
    />
  );
} 
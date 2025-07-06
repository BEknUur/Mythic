"use client"

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { useToast } from '@/hooks/use-toast';
import { Mail, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"


export function ProModal({ isOpen, setIsOpen }: { isOpen: boolean, setIsOpen: (open: boolean) => void }) {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Имитация отправки формы
    setTimeout(() => {
      setIsLoading(false);
      setIsOpen(false);
      toast({
        title: "Заявка принята!",
        description: "Мы свяжемся с вами, как только Pro-доступ будет готов.",
      });
    }, 1500);
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogContent className="bg-gray-50 dark:bg-gray-950 border-gray-200 dark:border-gray-800">
        <DialogHeader className="text-center">
          <DialogTitle className="text-2xl font-bold tracking-tight">Claim Your Free Pro Access</DialogTitle>
          <DialogDescription>
            Fill out the form below to unlock your unlimited Pro subscription
            <div className="flex justify-center items-center gap-2 mt-2">
                <span className="line-through text-gray-400">$9.99/month</span>
                <span className="font-semibold text-purple-500">FREE</span>
            </div>
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 pt-4">
            <div className="space-y-2">
                <Label htmlFor="fullName">Full Name *</Label>
                <Input id="fullName" placeholder="Enter your full name" required />
            </div>
            <div className="space-y-2">
                <Label htmlFor="email">Email Address *</Label>
                <Input id="email" type="email" placeholder="Enter your email address" required />
            </div>
            
            <div className="space-y-3">
                <Label>Where did you hear about us? *</Label>
                <RadioGroup required>
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value="nfactorial" id="r1" />
                        <Label htmlFor="r1">nFactorial Incubator</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value="linkedin" id="r2" />
                        <Label htmlFor="r2">LinkedIn</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                        <RadioGroupItem value="threads" id="r3" />
                        <Label htmlFor="r3">Threads</Label>
                    </div>
                     <div className="flex items-center space-x-2">
                        <RadioGroupItem value="other" id="r4" />
                        <Label htmlFor="r4">Other</Label>
                    </div>
                </RadioGroup>
            </div>

            <div className="flex items-start space-x-3 p-4 rounded-md bg-gray-100 dark:bg-gray-900">
                <Checkbox id="consent" className="mt-1" required />
                <div className="grid gap-1.5 leading-none">
                    <Label htmlFor="consent" className="font-normal">
                        I consent to the processing of my personal data for the purpose of providing Pro access and receiving updates about new features. You can unsubscribe at any time.
                    </Label>
                </div>
            </div>
            
            <Button type="submit" className="w-full h-12" disabled={isLoading}>
                {isLoading ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                    <Mail className="mr-2 h-4 w-4" />
                )}
                Get Free Pro Access
            </Button>
            
            <p className="text-xs text-center text-gray-500">
                By submitting this form, you agree to receive promotional emails and updates. No spam, unsubscribe anytime.
            </p>
        </form>
      </DialogContent>
    </Dialog>
  );
} 
"use client";

import { AnimatePresence, motion } from "framer-motion";
import type React from "react";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { useLocation, useNavigate } from "react-router-dom";

import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Torus } from "lucide-react";

// ---------------------- Constants ----------------------
export const TOUR_STEP_IDS = {
  START_CREATING_BUTTON: "start-creating-button",
  INSTAGRAM_INPUT: "instagram-input",
  MY_BOOKS_BUTTON: "my-books-button",
} as const;

export interface TourStep {
  content: React.ReactNode;
  selectorId: string;
  width?: number;
  height?: number;
  onClickWithinArea?: () => void;
  position?: "top" | "bottom" | "left" | "right";
  path: string;
}

interface TourContextType {
  currentStep: number;
  totalSteps: number;
  nextStep: () => void;
  previousStep: () => void;
  endTour: () => void;
  isActive: boolean;
  startTour: () => void;
  setSteps: (steps: TourStep[]) => void;
  steps: TourStep[];
  isTourCompleted: boolean;
  setIsTourCompleted: (completed: boolean) => void;
  pendingStep: number | null;
}

interface TourProviderProps {
  children: React.ReactNode;
  onComplete?: () => void;
  className?: string;
  isTourCompleted?: boolean;
}

const TourContext = createContext<TourContextType | null>(null);

const PADDING = 16;
const CONTENT_WIDTH = 300;
const CONTENT_HEIGHT = 174;

function getElementPosition(id: string) {
  const element = document.getElementById(id);
  if (!element) return null;
  const rect = element.getBoundingClientRect();
  return {
    top: rect.top + window.scrollY,
    left: rect.left + window.scrollX,
    width: rect.width,
    height: rect.height,
  };
}

function calculateContentPosition(
  elementPos: { top: number; left: number; width: number; height: number },
  position: "top" | "bottom" | "left" | "right" = "bottom",
) {
  let left = elementPos.left;
  let top = elementPos.top;

  switch (position) {
    case "top":
      top = elementPos.top - CONTENT_HEIGHT - PADDING;
      left = elementPos.left + elementPos.width / 2 - CONTENT_WIDTH / 2;
      break;
    case "bottom":
      top = elementPos.top + elementPos.height + PADDING;
      left = elementPos.left + elementPos.width / 2 - CONTENT_WIDTH / 2;
      break;
    case "left":
      left = elementPos.left - CONTENT_WIDTH - PADDING;
      top = elementPos.top + elementPos.height / 2 - CONTENT_HEIGHT / 2;
      break;
    case "right":
      left = elementPos.left + elementPos.width + PADDING;
      top = elementPos.top + elementPos.height / 2 - CONTENT_HEIGHT / 2;
      break;
  }

  return {
    top,
    left,
    width: CONTENT_WIDTH,
    height: CONTENT_HEIGHT,
  };
}

export function TourProvider({
  children,
  onComplete,
  className,
  isTourCompleted = false,
}: TourProviderProps) {
  const [steps, setSteps] = useState<TourStep[]>([]);
  const [currentStep, setCurrentStep] = useState(-1);
  const [elementPosition, setElementPosition] = useState<{
    top: number;
    left: number;
    width: number;
    height: number;
  } | null>(null);
  const [isCompleted, setIsCompleted] = useState(isTourCompleted);
  const navigate = useNavigate();
  const location = useLocation();
  const [pendingStep, setPendingStep] = useState<number | null>(null);

  const updateElementPosition = useCallback(() => {
    if (currentStep >= 0 && currentStep < steps.length) {
      const position = getElementPosition(steps[currentStep]?.selectorId ?? "");
      if (position) {
        setElementPosition(position);
      }
    }
  }, [currentStep, steps]);

  useEffect(() => {
    updateElementPosition();
    window.addEventListener("resize", updateElementPosition);
    window.addEventListener("scroll", updateElementPosition);

    return () => {
      window.removeEventListener("resize", updateElementPosition);
      window.removeEventListener("scroll", updateElementPosition);
    };
  }, [updateElementPosition]);

  const endTour = useCallback(() => {
    setCurrentStep(-1);
    if (!isCompleted) {
      setIsCompleted(true);
      onComplete?.();
    }
  }, [isCompleted, onComplete]);

  const nextStep = useCallback(() => {
    const nextStepIndex = currentStep + 1;
    if (nextStepIndex >= steps.length) {
      endTour();
      return;
    }

    const nextStepConfig = steps[nextStepIndex];
    if (nextStepConfig.path !== location.pathname) {
      setPendingStep(nextStepIndex);
      setCurrentStep(-1);
      navigate(nextStepConfig.path);
    } else {
      setCurrentStep(nextStepIndex);
    }
  }, [currentStep, steps, location.pathname, navigate, endTour]);

  const previousStep = useCallback(() => {
    const prevStepIndex = currentStep - 1;
    if (prevStepIndex < 0) return;

    const prevStepConfig = steps[prevStepIndex];
    if (prevStepConfig.path !== location.pathname) {
      setPendingStep(prevStepIndex);
      setCurrentStep(-1);
      navigate(prevStepConfig.path);
    } else {
      setCurrentStep(prevStepIndex);
    }
  }, [currentStep, steps, location.pathname, navigate]);

  // Effect to resume tour after navigation
  useEffect(() => {
    if (pendingStep !== null && location.pathname === steps[pendingStep]?.path) {
      const interval = setInterval(() => {
        const element = document.getElementById(steps[pendingStep].selectorId);
        if (element) {
          clearInterval(interval);
          setCurrentStep(pendingStep);
          setPendingStep(null);
        }
      }, 100);
      const timeout = setTimeout(() => clearInterval(interval), 3000); // 3-second timeout
      return () => {
        clearInterval(interval);
        clearTimeout(timeout);
      };
    }
  }, [pendingStep, location.pathname, steps]);

  const startTour = useCallback(() => {
    if (isCompleted) return;
    setCurrentStep(0);
  }, [isCompleted]);

  // Handle clicks within highlighted area
  const handleClick = useCallback(
    (e: MouseEvent) => {
      if (
        currentStep >= 0 &&
        elementPosition &&
        steps[currentStep]?.onClickWithinArea
      ) {
        const clickX = e.clientX + window.scrollX;
        const clickY = e.clientY + window.scrollY;

        const isWithinBounds =
          clickX >= elementPosition.left &&
          clickX <=
            elementPosition.left + (steps[currentStep]?.width || elementPosition.width) &&
          clickY >= elementPosition.top &&
          clickY <=
            elementPosition.top + (steps[currentStep]?.height || elementPosition.height);

        if (isWithinBounds) {
          steps[currentStep].onClickWithinArea?.();
        }
      }
    },
    [currentStep, elementPosition, steps],
  );

  useEffect(() => {
    window.addEventListener("click", handleClick);
    return () => window.removeEventListener("click", handleClick);
  }, [handleClick]);

  const setIsTourCompleted = useCallback((completed: boolean) => {
    setIsCompleted(completed);
  }, []);

  return (
    <TourContext.Provider
      value={{
        currentStep,
        totalSteps: steps.length,
        nextStep,
        previousStep,
        endTour,
        isActive: currentStep >= 0,
        startTour,
        setSteps,
        steps,
        isTourCompleted: isCompleted,
        setIsTourCompleted,
        pendingStep,
      }}
    >
      {children}
      <AnimatePresence>
        {currentStep >= 0 && elementPosition && (
          <>
            {/* Dark overlay with cut-out */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 overflow-hidden bg-black/50"
              style={{
                clipPath: `polygon(0% 0%, 0% 100%, 100% 100%, 100% 0%, ${elementPosition.left}px 0%, ${elementPosition.left}px ${elementPosition.top}px, ${elementPosition.left + (steps[currentStep]?.width || elementPosition.width)}px ${elementPosition.top}px, ${elementPosition.left + (steps[currentStep]?.width || elementPosition.width)}px ${elementPosition.top + (steps[currentStep]?.height || elementPosition.height)}px, ${elementPosition.left}px ${elementPosition.top + (steps[currentStep]?.height || elementPosition.height)}px, ${elementPosition.left}px 0%)`,
              }}
            />
            {/* Highlight rectangle */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              style={{
                position: "fixed",
                top: elementPosition.top,
                left: elementPosition.left,
                width: elementPosition.width,
                height: elementPosition.height,
              }}
              className={cn("z-[100] border-2 border-primary", className)}
            />
            {/* Tooltip / popover */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{
                opacity: 1,
                y: 0,
                ...calculateContentPosition(elementPosition, steps[currentStep]?.position),
              }}
              exit={{ opacity: 0, y: 10 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
              style={{ position: "fixed", zIndex: 1000, width: CONTENT_WIDTH }}
              className="bg-background relative rounded-lg border p-4 shadow-lg min-h-[120px]"
            >
              <div className="text-muted-foreground absolute right-4 top-2 text-xs">
                {currentStep + 1} / {steps.length}
              </div>
              <AnimatePresence mode="wait">
                <motion.div
                  key={`tour-content-${currentStep}`}
                  initial={{ opacity: 0, scale: 0.95, filter: "blur(4px)" }}
                  animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
                  exit={{ opacity: 0, scale: 0.95, filter: "blur(4px)" }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden pt-4"
                >
                  {steps[currentStep]?.content}
                </motion.div>
              </AnimatePresence>
              <div className="mt-4 flex justify-between">
                {currentStep > 0 && (
                  <Button variant="ghost" onClick={previousStep} className="text-sm">
                    Previous
                  </Button>
                )}
                <Button variant="ghost" onClick={nextStep} className={cn("text-sm", !currentStep && "ml-auto")}>
                  {currentStep === steps.length - 1 ? "Finish" : "Next"}
                </Button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </TourContext.Provider>
  );
}

export function useTour() {
  const context = useContext(TourContext);
  if (!context) {
    throw new Error("useTour must be used within a TourProvider");
  }
  return context;
}

export function TourAlertDialog({
  isOpen,
  setIsOpen,
}: {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}) {
  const { startTour, steps, isTourCompleted, currentStep, pendingStep } = useTour();

  if (isTourCompleted || steps.length === 0 || currentStep > -1 || pendingStep !== null) {
    return null;
  }

  const handleSkip = () => setIsOpen(false);

  return (
    <AlertDialog open={isOpen}>
      <AlertDialogContent className="max-w-md p-6">
        <AlertDialogHeader className="flex flex-col items-center justify-center">
          <div className="relative mb-4">
            <motion.div
              initial={{ scale: 0.7, filter: "blur(10px)" }}
              animate={{
                scale: 1,
                filter: "blur(0px)",
                y: [0, -8, 0],
                rotate: [42, 48, 42],
              }}
              transition={{
                duration: 0.4,
                ease: "easeOut",
                y: { duration: 2.5, repeat: Infinity, ease: "easeInOut" },
                rotate: { duration: 3, repeat: Infinity, ease: "easeInOut" },
              }}
            >
              <Torus className="size-32 stroke-1 text-primary" />
            </motion.div>
          </div>
          <AlertDialogTitle className="text-center text-xl font-medium">
            Welcome to the Mythic Ai! ✨
          </AlertDialogTitle>
          <AlertDialogDescription className="text-muted-foreground mt-2 text-center text-sm">
            Take a quick tour to learn about the key features and functionality of this application.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <div className="mt-6 space-y-3">
          <Button onClick={startTour} className="w-full">
            Start Tour
          </Button>
          <Button onClick={handleSkip} variant="ghost" className="w-full">
            Skip Tour
          </Button>
        </div>
      </AlertDialogContent>
    </AlertDialog>
  );
} 
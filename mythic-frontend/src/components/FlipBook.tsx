import React from 'react';
import HTMLFlipBookLib from 'react-pageflip';

// The typings shipped with `react-pageflip` are not fully compatible with strict TypeScript
// settings used in this project (several props are marked as required while they are actually
// optional). To avoid tedious prop drilling we cast the component to `any`.
const HTMLFlipBook = HTMLFlipBookLib as unknown as React.ComponentType<any>;

export interface FlipBookProps {
  /**
   * Optional array of elements that will be rendered as individual pages inside the book.
   * If omitted, placeholder pages will be generated automatically.
   */
  pages?: React.ReactNode[];
}

/**
 * A single page to be rendered inside the FlipBook component.
 * The ref is forwarded because react-pageflip requires direct access to the DOM node.
 */
const Page = React.forwardRef<HTMLDivElement, { number: number; children?: React.ReactNode }>(
  ({ number, children }, ref) => {
    return (
      <div
        ref={ref}
        className="w-full h-full bg-white border border-gray-200 shadow-xl flex items-center justify-center text-2xl font-serif p-8 select-none"
      >
        {children ?? `Page ${number}`}
      </div>
    );
  }
);
Page.displayName = 'Page';

/**
 * FlipBook – a ready-to-use wrapper around HTMLFlipBook from the `react-pageflip` package.
 * You can supply arbitrary pages via the `pages` prop, otherwise it will show demo pages.
 */
export function FlipBook({ pages }: FlipBookProps) {
  // Prepare placeholder pages when the caller didn't provide anything.
  const placeholderPages = Array.from({ length: 6 }).map((_, idx) => (
    <Page key={idx} number={idx + 1} />
  ));

  const preparedPages = pages && pages.length
    ? pages.map((content, idx) => (
        <Page key={idx} number={idx + 1}>
          {content}
        </Page>
      ))
    : placeholderPages;

  return (
    <div className="flex-1 w-full h-full flex items-center justify-center p-4">
      <HTMLFlipBook
        width={450}
        height={600}
        size="stretch"
        minWidth={315}
        maxWidth={1000}
        minHeight={420}
        maxHeight={1350}
        maxShadowOpacity={0.5}
        showCover={false}
        className="shadow-2xl book-container"
        mobileScrollSupport
        showPageCorners
        useMouseEvents
      >
        {preparedPages}
      </HTMLFlipBook>
    </div>
  );
} 
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
        className="w-full h-full border shadow-xl flex items-center justify-center text-2xl font-serif p-8 select-none"
        style={{
          background: children ? 'transparent' : 'linear-gradient(135deg, #f8f6f0 0%, #f0ede5 30%, #e8e3d3 100%)',
          color: children ? 'inherit' : '#4a453f',
          fontFamily: children ? 'inherit' : "'Cormorant Garamond', serif",
          borderColor: children ? 'rgba(200, 180, 140, 0.3)' : 'rgba(180, 160, 130, 0.4)',
          boxShadow: children ? 'inherit' : '0 4px 20px rgba(160, 140, 100, 0.2)',
        }}
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
        width={900}
        height={700}
        size="fixed"
        minWidth={700}
        maxWidth={1600}
        minHeight={500}
        maxHeight={1200}
        maxShadowOpacity={0.18}
        showCover={false}
        className="shadow-2xl book-container"
        mobileScrollSupport
        showPageCorners={true}
        useMouseEvents
        flippingTime={800}
        usePortrait={false}
        swipeDistance={50}
        clickEventForward={false}
        drawShadow={true}
        autoSize={false}
        startPage={0}
        startZIndex={0}
        useBook={true}
        style={{ margin: '0 auto' }}
      >
        {preparedPages}
      </HTMLFlipBook>
    </div>
  );
} 
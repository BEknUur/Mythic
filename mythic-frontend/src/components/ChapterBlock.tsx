import { useRef, useEffect } from 'react';

interface ChapterBlockProps {
  idx: number;
  html: string;
  onUpdate: (idx: number, newHtml: string) => void;
  onTextSelected: (idx: number, range: Range, selected: string) => void;
}

export function ChapterBlock({ idx, html, onUpdate, onTextSelected }: ChapterBlockProps) {
  const divRef = useRef<HTMLDivElement>(null);
  const savedRangeRef = useRef<Range | null>(null);

  useEffect(() => {
    if (divRef.current && divRef.current.innerHTML !== html) {
      divRef.current.innerHTML = html;
    }
  }, [html]);

  // Сохраняем выделение
  const handleMouseUp = () => {
    const sel = window.getSelection();
    if (sel && sel.rangeCount) {
      const range = sel.getRangeAt(0);
      if (divRef.current && divRef.current.contains(range.commonAncestorContainer)) {
        savedRangeRef.current = range.cloneRange();
        onTextSelected(idx, savedRangeRef.current, sel.toString());
      }
    }
  };

  // Применение текста, который придёт снаружи
  const applySuggestion = (text: string, selected: string) => {
    if (!savedRangeRef.current) return;
    const sel = window.getSelection();
    if (!sel) return;
    sel.removeAllRanges();
    sel.addRange(savedRangeRef.current);
    savedRangeRef.current.deleteContents();
    savedRangeRef.current.insertNode(document.createTextNode(text));
    sel.removeAllRanges();
    savedRangeRef.current = null;
    onUpdate(idx, divRef.current!.innerHTML);
  };

  // expose method via attribute
  // We'll set a property on the DOM element to allow parent to call
  useEffect(() => {
    if (divRef.current) {
      (divRef.current as any).__applySuggestion = applySuggestion;
    }
  }, []);

  return (
    <div
      data-chapter-idx={idx}
      ref={divRef}
      className="chapter-block"
      contentEditable
      suppressContentEditableWarning
      onMouseUp={handleMouseUp}
    />
  );
} 
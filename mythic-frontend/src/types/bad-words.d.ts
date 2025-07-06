declare module 'bad-words' {
  interface FilterOptions {
    placeHolder?: string;
    list?: string[];
    exclude?: string[];
  }

  export class Filter {
    constructor(options?: FilterOptions);
    isProfane(str: string): boolean;
    clean(str: string): string;
    addWords(...words: string[]): this;
    removeWords(...words: string[]): this;
  }

  export default Filter;
} 
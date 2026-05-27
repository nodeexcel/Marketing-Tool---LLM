declare module '@tiptap/starter-kit';
declare module '@tiptap/extension-placeholder';
declare module '@tiptap/extension-image';

declare module 'zustand' {
  export type SetState<T> = (partial: Partial<T> | ((state: T) => Partial<T>)) => void;
  export type StateCreator<T> = (set: SetState<T>) => T;
  export function create<T>(creator: StateCreator<T>): any;
}

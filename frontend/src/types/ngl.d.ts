declare module "ngl" {
  export class Stage {
    constructor(el: HTMLElement, params?: any);
    loadFile(url: string, params?: any): Promise<any>;
    setSpin(flag: boolean): void;
    handleResize(): void;
    dispose(): void;
  }
}

import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface ModalConfig {
  id: string;
  title: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  backdrop?: boolean | 'static';
  keyboard?: boolean;
  centered?: boolean;
  scrollable?: boolean;
  data?: any;
}

export interface ModalResult {
  action: string;
  data?: any;
}

@Injectable({
  providedIn: 'root'
})
export class ModalService {
  private modals = new Map<string, BehaviorSubject<ModalConfig | null>>();
  private modalResults = new Map<string, BehaviorSubject<ModalResult | null>>();

  constructor() {}

  /**
   * Register a modal
   */
  registerModal(id: string): Observable<ModalConfig | null> {
    if (!this.modals.has(id)) {
      this.modals.set(id, new BehaviorSubject<ModalConfig | null>(null));
      this.modalResults.set(id, new BehaviorSubject<ModalResult | null>(null));
    }
    return this.modals.get(id)!.asObservable();
  }

  /**
   * Open a modal
   */
  openModal(config: ModalConfig): void {
    if (!this.modals.has(config.id)) {
      this.registerModal(config.id);
    }
    // Clear any previous result when opening a new modal
    this.modalResults.get(config.id)!.next(null);
    this.modals.get(config.id)!.next(config);
  }

  /**
   * Close a modal
   */
  closeModal(id: string): void {
    if (this.modals.has(id)) {
      this.modals.get(id)!.next(null);
    }
  }

  /**
   * Get modal result
   */
  getModalResult(id: string): Observable<ModalResult | null> {
    if (!this.modalResults.has(id)) {
      this.modalResults.set(id, new BehaviorSubject<ModalResult | null>(null));
    }
    return this.modalResults.get(id)!.asObservable();
  }

  /**
   * Set modal result
   */
  setModalResult(id: string, result: ModalResult): void {
    if (!this.modalResults.has(id)) {
      this.modalResults.set(id, new BehaviorSubject<ModalResult | null>(null));
    }
    this.modalResults.get(id)!.next(result);
  }

  /**
   * Confirm deletion
   */
  confirmDelete(message: string): Promise<boolean> {
    return new Promise((resolve) => {
      const config: ModalConfig = {
        id: 'deleteConfirmationModal',
        title: 'Confirm Delete',
        data: { message }
      };
      
      this.openModal(config);
      
      const subscription = this.getModalResult('deleteConfirmationModal').subscribe((result) => {
        if (result) {
          subscription.unsubscribe();
          resolve(result.action === 'confirm');
        }
      });
    });
  }

  /**
   * Show book details
   */
  showBookDetails(book: any): void {
    const config: ModalConfig = {
      id: 'bookDetailsModal',
      title: 'Book Details',
      size: 'lg',
      data: { book }
    };
    this.openModal(config);
  }

  /**
   * Show manga details
   */
  showMangaDetails(manga: any): void {
    const config: ModalConfig = {
      id: 'mangaDetailsModal',
      title: 'Manga Details',
      size: 'lg',
      scrollable: true,
      data: { manga }
    };
    this.openModal(config);
  }

  /**
   * Show import success
   */
  showImportSuccess(message: string, viewLink?: string): void {
    const config: ModalConfig = {
      id: 'importSuccessModal',
      title: 'Import Successful',
      data: { message, viewLink }
    };
    this.openModal(config);
  }
}

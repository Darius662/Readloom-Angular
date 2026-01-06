import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ModalService } from '../../../services/modal.service';

@Component({
    selector: 'app-delete-confirmation',
    imports: [FormsModule],
    templateUrl: './delete-confirmation.component.html',
    styleUrls: ['./delete-confirmation.component.css']
})
export class DeleteConfirmationComponent implements OnInit {
  isVisible = false;
  message = 'Are you sure you want to delete this item?';
  showWarning = false;
  showEbookCheckbox = false;
  removeEbookFiles = false;

  constructor(private modalService: ModalService) {}

  ngOnInit(): void {
    this.modalService.registerModal('deleteConfirmationModal').subscribe((config) => {
      if (config) {
        this.isVisible = true;
        this.message = config.data?.message || 'Are you sure you want to delete this item?';
        this.showWarning = true;
        this.showEbookCheckbox = config.data?.showEbookCheckbox || false;
        this.removeEbookFiles = false; // Reset checkbox each time modal opens
      } else {
        this.isVisible = false;
      }
    });
  }

  onConfirmDelete(): void {
    this.modalService.setModalResult('deleteConfirmationModal', { 
      action: 'confirm',
      data: {
        removeEbookFiles: this.removeEbookFiles
      }
    });
    this.closeModal();
  }

  closeModal(): void {
    this.isVisible = false;
    this.modalService.closeModal('deleteConfirmationModal');
  }
}

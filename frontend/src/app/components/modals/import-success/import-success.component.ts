import { Component, OnInit } from '@angular/core';

import { ModalService } from '../../../services/modal.service';

@Component({
    selector: 'app-import-success',
    imports: [],
    templateUrl: './import-success.component.html',
    styleUrls: ['./import-success.component.css']
})
export class ImportSuccessComponent implements OnInit {
  isVisible = false;
  message = '';
  viewLink: string | null = null;

  constructor(private modalService: ModalService) {}

  ngOnInit(): void {
    this.modalService.registerModal('importSuccessModal').subscribe((config) => {
      if (config) {
        this.isVisible = true;
        this.message = config.data?.message || 'Import successful!';
        this.viewLink = config.data?.viewLink || null;
      } else {
        this.isVisible = false;
      }
    });
  }

  closeModal(): void {
    this.isVisible = false;
    this.modalService.closeModal('importSuccessModal');
  }

  navigateToView(): void {
    if (this.viewLink) {
      window.location.href = this.viewLink;
    }
  }
}

import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { CommonModule } from '@angular/common';

interface AddCollectionForm {
  name: string;
  description: string;
  content_type: string;
  is_default: boolean;
}

@Component({
  selector: 'app-add-collection-modal',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatCheckboxModule
  ],
  templateUrl: './add-collection-modal.component.html',
  styleUrls: ['./add-collection-modal.component.css']
})
export class AddCollectionModalComponent implements OnInit {
  form: AddCollectionForm = {
    name: '',
    description: '',
    content_type: 'BOOK',
    is_default: false
  };

  contentTypes = [
    { value: 'BOOK', label: 'Book' },
    { value: 'MANGA', label: 'Manga' },
    { value: 'LIGHT_NOVEL', label: 'Light Novel' },
    { value: 'COMIC', label: 'Comic' },
    { value: 'GRAPHIC_NOVEL', label: 'Graphic Novel' },
    { value: 'WEBTOON', label: 'Webtoon' },
    { value: 'MIXED', label: 'Mixed' }
  ];

  constructor(public dialogRef: MatDialogRef<AddCollectionModalComponent>) {}

  ngOnInit(): void {}

  onCancel(): void {
    this.dialogRef.close();
  }

  onSave(): void {
    if (!this.form.name.trim()) {
      alert('Collection name is required');
      return;
    }

    this.dialogRef.close({
      action: 'save',
      data: this.form
    });
  }
}

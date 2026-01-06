import { Component, OnInit, Inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { CommonModule } from '@angular/common';

interface EditCollectionForm {
  id: number;
  name: string;
  description: string;
  type?: string;
  content_type?: string;
  is_default: boolean;
}

@Component({
  selector: 'app-edit-collection-modal',
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
  templateUrl: './edit-collection-modal.component.html',
  styleUrls: ['./edit-collection-modal.component.css']
})
export class EditCollectionModalComponent implements OnInit {
  form: EditCollectionForm;

  contentTypes = [
    { value: 'BOOK', label: 'Book' },
    { value: 'MANGA', label: 'Manga' },
    { value: 'LIGHT_NOVEL', label: 'Light Novel' },
    { value: 'COMIC', label: 'Comic' },
    { value: 'GRAPHIC_NOVEL', label: 'Graphic Novel' },
    { value: 'WEBTOON', label: 'Webtoon' },
    { value: 'MIXED', label: 'Mixed' }
  ];

  constructor(
    public dialogRef: MatDialogRef<EditCollectionModalComponent>,
    @Inject(MAT_DIALOG_DATA) public data: EditCollectionForm
  ) {
    this.form = { ...data };
    // Ensure we have the content_type set from either type or content_type field
    if (!this.form.content_type && !this.form.type) {
      this.form.content_type = 'BOOK';
    } else if (!this.form.content_type) {
      this.form.content_type = this.form.type;
    }
  }

  ngOnInit(): void {}

  onCancel(): void {
    this.dialogRef.close();
  }

  onSave(): void {
    if (!this.form.name.trim()) {
      alert('Collection name is required');
      return;
    }

    // Only send the fields that might have changed
    const updateData: any = {
      id: this.form.id,
      name: this.form.name,
      description: this.form.description,
      content_type: this.form.content_type || 'BOOK',
      is_default: this.form.is_default
    };

    this.dialogRef.close({
      action: 'update',
      data: updateData
    });
  }
}

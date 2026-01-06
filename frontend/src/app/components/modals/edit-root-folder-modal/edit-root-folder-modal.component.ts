import { Component, OnInit, Inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA, MatDialog } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { CommonModule } from '@angular/common';

import { FileBrowserDialogComponent, FileBrowserDialogData, FileBrowserDialogResult } from '../../file-browser-dialog/file-browser-dialog.component';

interface EditRootFolderForm {
  id: number;
  name: string;
  path: string;
  content_type: string;
}

@Component({
  selector: 'app-edit-root-folder-modal',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule,
    MatTooltipModule
  ],
  templateUrl: './edit-root-folder-modal.component.html',
  styleUrls: ['./edit-root-folder-modal.component.css']
})
export class EditRootFolderModalComponent implements OnInit {
  form: EditRootFolderForm;

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
    public dialogRef: MatDialogRef<EditRootFolderModalComponent>,
    @Inject(MAT_DIALOG_DATA) public data: EditRootFolderForm,
    private dialog: MatDialog
  ) {
    this.form = { ...data };
  }

  ngOnInit(): void {}

  onCancel(): void {
    this.dialogRef.close();
  }

  openFileBrowser(): void {
    const dialogData: FileBrowserDialogData = {
      initialPath: this.form.path || undefined,
      title: 'Select Root Folder',
      allowFolderSelection: true,
      allowFileSelection: false
    };

    const dialogRef = this.dialog.open<FileBrowserDialogComponent, FileBrowserDialogData, FileBrowserDialogResult>(
      FileBrowserDialogComponent,
      {
        width: '800px',
        maxWidth: '90vw',
        height: '80vh',
        data: dialogData
      }
    );

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.form.path = result.selectedPath;
        // Auto-fill name if empty
        if (!this.form.name.trim()) {
          this.form.name = result.selectedName || 'Library';
        }
      }
    });
  }

  onSave(): void {
    if (!this.form.name.trim()) {
      alert('Folder name is required');
      return;
    }
    if (!this.form.path.trim()) {
      alert('Folder path is required');
      return;
    }

    this.dialogRef.close({
      action: 'update',
      data: this.form
    });
  }
}

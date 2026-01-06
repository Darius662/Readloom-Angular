import { Component, OnInit, Inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { CommonModule } from '@angular/common';

interface RootFolder {
  id: number;
  name: string;
  path: string;
  content_type: string;
}

interface LinkRootFolderData {
  availableFolders: RootFolder[];
}

@Component({
  selector: 'app-link-root-folder-modal',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatSelectModule
  ],
  templateUrl: './link-root-folder-modal.component.html',
  styleUrls: ['./link-root-folder-modal.component.css']
})
export class LinkRootFolderModalComponent implements OnInit {
  selectedRootFolderId: number | null = null;
  availableFolders: RootFolder[] = [];

  constructor(
    public dialogRef: MatDialogRef<LinkRootFolderModalComponent>,
    @Inject(MAT_DIALOG_DATA) public data: LinkRootFolderData
  ) {
    this.availableFolders = data.availableFolders || [];
  }

  ngOnInit(): void {
    // Initialize component
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  onLink(): void {
    if (this.selectedRootFolderId !== null) {
      this.dialogRef.close({
        action: 'link',
        rootFolderId: this.selectedRootFolderId
      });
    }
  }
}

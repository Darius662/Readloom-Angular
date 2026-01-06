import { Component, Input, Output, EventEmitter } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { Collection } from '../../../models/collection.model';

@Component({
  selector: 'app-collection-cards-section',
  imports: [MatCardModule, MatButtonModule, MatIconModule],
  templateUrl: './collection-cards-section.component.html',
  styleUrl: './collection-cards-section.component.css'
})
export class CollectionCardsSectionComponent {
  @Input() collections: Collection[] = [];
  @Output() addCollection = new EventEmitter<void>();
  @Output() editCollection = new EventEmitter<Collection>();
  @Output() deleteCollection = new EventEmitter<Collection>();

  onAdd(): void {
    this.addCollection.emit();
  }

  onEdit(collection: Collection): void {
    this.editCollection.emit(collection);
  }

  onDelete(collection: Collection): void {
    this.deleteCollection.emit(collection);
  }
}

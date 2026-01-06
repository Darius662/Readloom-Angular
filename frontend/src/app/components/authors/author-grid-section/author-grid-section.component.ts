import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { Author } from '../../../models/author.model';

@Component({
    selector: 'app-author-grid-section',
    imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule],
    templateUrl: './author-grid-section.component.html',
    styleUrls: ['./author-grid-section.component.css']
})
export class AuthorGridSectionComponent {
  @Input() authors: Author[] = [];
  @Input() resultCount = 0;
}

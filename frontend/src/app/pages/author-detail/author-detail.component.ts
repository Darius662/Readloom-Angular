import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { LoadingSpinnerComponent } from '../../components/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../components/error-message/error-message.component';
import { AuthorService } from '../../services/author.service';
import { NotificationService } from '../../services/notification.service';
import { Author, AuthorMetadata } from '../../models/author.model';

@Component({
    selector: 'app-author-detail',
    imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule, LoadingSpinnerComponent, ErrorMessageComponent],
    templateUrl: './author-detail.component.html',
    styleUrls: ['./author-detail.component.css']
})
export class AuthorDetailComponent implements OnInit {
  isLoading = true;
  error: string | null = null;

  author: Author | null = null;
  metadata: AuthorMetadata | null = null;

  constructor(
    private route: ActivatedRoute,
    private authorService: AuthorService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadAuthorDetail();
  }

  private loadAuthorDetail(): void {
    this.isLoading = true;
    this.error = null;

    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.error = 'Author ID not found';
      this.isLoading = false;
      return;
    }

    this.authorService.getAuthorById(parseInt(id)).subscribe({
      next: (author) => {
        this.author = author;
        this.loadMetadata(parseInt(id));
      },
      error: (err) => {
        this.error = 'Failed to load author';
        this.notificationService.error('Failed to load author');
        this.isLoading = false;
      }
    });
  }

  private loadMetadata(authorId: number): void {
    this.authorService.getAuthorMetadata(authorId).subscribe({
      next: (metadata) => {
        this.metadata = metadata;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }
}

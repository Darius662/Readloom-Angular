import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';

@Component({
    selector: 'app-error-message',
    imports: [CommonModule, MatIconModule, MatButtonModule, MatCardModule],
    templateUrl: './error-message.component.html',
    styleUrls: ['./error-message.component.css']
})
export class ErrorMessageComponent {
  @Input() message = 'An error occurred';
  @Input() details?: string;
  @Input() showDetails = false;
}

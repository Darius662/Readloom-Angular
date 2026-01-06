import { Component } from '@angular/core';

import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
    selector: 'app-about',
    imports: [MatCardModule, MatButtonModule, MatIconModule],
    templateUrl: './about.component.html',
    styleUrls: ['./about.component.css']
})
export class AboutComponent {
  title = 'About';
  appVersion = '3.0.0';
  appName = 'Readloom';
}

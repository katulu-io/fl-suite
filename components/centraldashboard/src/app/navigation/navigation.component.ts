import { Component } from '@angular/core';
import { ConfigService } from '../config.service';

@Component({
  selector: 'app-navigation',
  templateUrl: './navigation.component.html',
  styleUrls: ['./navigation.component.scss'],
})
export class NavigationComponent {
  constructor(private configService: ConfigService) {}

  menuItems = this.configService.getApps();
}

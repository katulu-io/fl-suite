import { Component, OnInit } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
// @ts-expect-error
import LogoDeepblue from 'raw-loader!./logo-white.svg';

@Component({
  selector: 'app-logo',
  templateUrl: './logo.component.html',
  styleUrls: ['./logo.component.scss'],
})
export class LogoComponent {
  logo;

  constructor(private sanitizer: DomSanitizer) {
    this.logo = sanitizer.bypassSecurityTrustHtml(LogoDeepblue);
  }
}

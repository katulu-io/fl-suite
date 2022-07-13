import { TestBed } from '@angular/core/testing';

import { EdgeIdentityBackendService } from './backend.service';
import { HttpClientModule } from '@angular/common/http';

describe('EdgeListBackendService', () => {
  beforeEach(() =>
    TestBed.configureTestingModule({
      imports: [HttpClientModule],
    }),
  );

  it('should be created', () => {
    const service: EdgeIdentityBackendService = TestBed.inject(EdgeIdentityBackendService);
    expect(service).toBeTruthy();
  });
});

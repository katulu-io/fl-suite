import { Injectable } from '@angular/core';
import { BackendService, SnackBarService } from 'kubeflow';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { EdgeResponseObject, EdgeListBackendResponse, EdgePostObject } from '../types';

@Injectable({
  providedIn: 'root',
})
export class EdgeIdentityBackendService extends BackendService {
  constructor(public http: HttpClient, public snackBar: SnackBarService) {
    super(http, snackBar);
  }

  public getEdges(namespace: string): Observable<EdgeResponseObject[]> {
    const url = `api/namespaces/${namespace}/edges`;

    return this.http.get<EdgeListBackendResponse>(url).pipe(
      catchError(error => this.handleError(error)),
      map((resp: EdgeListBackendResponse) => {
        return resp.edges;
      }),
    );
  }

  // POST
  public createViewer(namespace: string, viewer: string) {
    const url = `api/namespaces/${namespace}/viewers`;

    return this.http
      .post<EdgeListBackendResponse>(url, { name: viewer })
      .pipe(catchError(error => this.handleError(error)));
  }

  public createEdge(namespace: string, edge: EdgePostObject) {
    const url = `api/namespaces/${namespace}/edges`;

    return this.http
      .post<EdgeListBackendResponse>(url, edge)
      .pipe(catchError(error => this.handleError(error)));
  }

  // DELETE
  public deleteEdge(namespace: string, edge: string) {
    const url = `api/namespaces/${namespace}/edges/${edge}`;

    return this.http
      .delete<EdgeListBackendResponse>(url)
      .pipe(catchError(error => this.handleError(error, false)));
  }
}

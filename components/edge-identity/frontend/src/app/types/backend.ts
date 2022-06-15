import { Status, BackendResponse } from 'kubeflow';

export interface EdgeListBackendResponse extends BackendResponse {
  edges?: EdgeResponseObject[];
}

export interface EdgeResponseObject {
  name: string;
  namespace: string;
  status: Status;
  age: string;
}

export interface EdgeProcessedObject extends EdgeResponseObject {
  deleteAction?: string;
}

export interface EdgePostObject {
  name: string;
}

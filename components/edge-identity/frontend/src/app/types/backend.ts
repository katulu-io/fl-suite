import { Status, BackendResponse } from 'kubeflow';

export interface EdgeListBackendResponse extends BackendResponse {
  edges?: EdgeResponseObject[];
}

export interface EdgeResponseObject {
  name: string;
  namespace: string;
  status: Status;
  age: string;
  join_token: string;
  server_address: string;
  server_port: number;
  trust_domain: string;
  skip_kubelet_verification: boolean;
  orchestrator_url: string;
  orchestrator_port: number;
  orchestrator_sni: string;
}

export interface EdgeProcessedObject extends EdgeResponseObject {
  deleteAction?: string;
  showAction?: string;
}

export interface EdgePostObject {
  name: string;
}

export interface EdgePostResponseObject {
  edge: EdgeResponseObject;
}

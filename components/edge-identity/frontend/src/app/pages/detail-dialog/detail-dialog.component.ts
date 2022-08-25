import { Inject, Injectable, Component, OnInit, OnDestroy } from '@angular/core';
import {Clipboard} from '@angular/cdk/clipboard'; import {
  FormBuilder,
  FormGroup,
  Validators,
  FormControl,
  ValidatorFn,
} from '@angular/forms';
import { Subscription } from 'rxjs';
import {
  DialogConfig,
  DIALOG_RESP,
  SnackBarService,
  SnackType,
} from 'kubeflow';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

import { EdgeResponseObject } from 'src/app/types';

@Component({
  selector: 'app-form-default',
  templateUrl: './detail-dialog.component.html',
  styleUrls: ['./detail-dialog.component.scss'],
})
export class DetailDialogComponent implements OnInit, OnDestroy {
  public TYPE_EMPTY = 'empty';

  public subs = new Subscription();
  public crdText = "";

  constructor(
    public dialog: MatDialogRef<DetailDialogComponent>,
    private clipboard: Clipboard,
    public snackBar: SnackBarService,
    @Inject(MAT_DIALOG_DATA) public edge: EdgeResponseObject,
  ) {
    this.crdText = `---
apiVersion: fl.katulu.io/v1alpha1
kind: FlEdge
metadata:
  name: ${edge.name}
spec:
  auth:
    spire:
      server-address: ${edge.server_address}
      server-port: ${edge.server_port}
      trust-domain: ${edge.trust_domain}
      join-token: ${edge.join_token}
      skip-kubelet-verification: ${edge.skip_kubelet_verification}
---
apiVersion: fl.katulu.io/v1alpha1
kind: FlOperator
metadata:
  name: ${edge.name}
spec:
  orchestrator-url: ${edge.orchestrator_url}
  orchestrator-port: ${edge.orchestrator_port}
  orchestrator-sni: ${edge.orchestrator_sni}
  registry-credentials:
    secret: regcred
---
apiVersion: v1
kind: Secret
type: kubernetes.io/dockerconfigjson
metadata:
  name: regcred
data:
  .dockerconfigjson: ${edge.registry_credentials}
`;
  }

  ngOnInit() { }

  ngOnDestroy() {
    this.subs.unsubscribe();
  }

  public onCancel() {
    this.dialog.close(DIALOG_RESP.CANCEL);
  }

  public onCopy() {
    this.clipboard.copy(this.crdText);

    this.snackBar.open(
      $localize`CRD copied to clipboard.`,
      SnackType.Success,
      2000,
    );
  }
}

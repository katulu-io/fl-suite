import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import {
  NamespaceService,
  ActionEvent,
  ConfirmDialogService,
  ExponentialBackoff,
  STATUS_TYPE,
  DIALOG_RESP,
  DialogConfig,
  SnackBarService,
  SnackType,
  ToolbarButton,
} from 'kubeflow';
import { defaultConfig } from './config';
import { environment } from '@app/environment';
import { EdgeIdentityBackendService } from 'src/app/services/backend.service';
import { EdgeResponseObject, EdgeProcessedObject } from 'src/app/types';
import { Subscription, Observable, Subject } from 'rxjs';
import { isEqual } from 'lodash';
import { FormDefaultComponent } from '../../form/form-default/form-default.component';
import { DetailDialogComponent } from '../../detail-dialog/detail-dialog.component'

@Component({
  selector: 'app-index-default',
  templateUrl: './index-default.component.html',
  styleUrls: ['./index-default.component.scss'],
})
export class IndexDefaultComponent implements OnInit {
  public env = environment;
  public poller: ExponentialBackoff;

  public currNamespace = '';
  public subs = new Subscription();

  public config = defaultConfig;
  public rawData: EdgeResponseObject[] = [];
  public processedData: EdgeProcessedObject[] = [];


  constructor(
    public ns: NamespaceService,
    public confirmDialog: ConfirmDialogService,
    public backend: EdgeIdentityBackendService,
    public dialog: MatDialog,
    public snackBar: SnackBarService,
  ) {}

  ngOnInit() {
    this.poller = new ExponentialBackoff({ interval: 1000, retries: 3 });

    // Poll for new data and reset the poller if different data is found
    this.subs.add(
      this.poller.start().subscribe(() => {
        if (!this.currNamespace) {
          return;
        }

        this.backend.getEdges(this.currNamespace).subscribe(edges => {
          if (!isEqual(this.rawData, edges)) {
            this.rawData = edges;

            // Update the frontend's state
            this.processedData = this.parseIncomingData(edges);
            this.poller.reset();
          }
        });
      }),
    );

    // Reset the poller whenever the selected namespace changes
    this.subs.add(
      this.ns.getSelectedNamespace().subscribe(ns => {
        this.currNamespace = ns;
        this.poller.reset();
      }),
    );
  }

  public reactToAction(a: ActionEvent) {
    switch (a.action) {
      case 'newResourceButton': // TODO: could also use enums here
        this.newResourceClicked();
        break;
      case 'delete':
        this.deleteVolumeClicked(a.data);
        break;
      case 'show':
        this.showEdge(a.data);
        break;
    }
  }

  // Functions for handling the action events
  public newResourceClicked() {
    const ref = this.dialog.open(FormDefaultComponent, {
      width: '600px',
      panelClass: 'form--dialog-padding',
    });

    ref.afterClosed().subscribe((newEdge: EdgeResponseObject|DIALOG_RESP) => {
      // If newEdge was created successufully and response object is returned
      if (newEdge !== DIALOG_RESP.CANCEL) {
        this.snackBar.open(
          $localize`Edge created successfully.`,
          SnackType.Success,
          2000,
        );
        this.poller.reset();

        const detailDialog = this.dialog.open(DetailDialogComponent, {
          width: '600px',
          panelClass: 'form--dialog-padding',
          data: newEdge
        });
      }
    });
  }

  public showEdge(edge: EdgeProcessedObject) {
    const ref = this.dialog.open(DetailDialogComponent, {
      width: '600px',
      panelClass: 'form--dialog-padding',
      data: edge
    });
  }

  public deleteVolumeClicked(edge: EdgeProcessedObject) {
    const deleteDialogConfig: DialogConfig = {
      title: $localize`Are you sure you want to deregister this edge: ${edge.name} ?`,
      message: "",
      accept: $localize`DELETE`,
      confirmColor: 'warn',
      cancel: $localize`CANCEL`,
      error: '',
      applying: $localize`DELETING`,
      width: '600px',
    };

    const ref = this.confirmDialog.open(edge.name, deleteDialogConfig);
    const delSub = ref.componentInstance.applying$.subscribe(applying => {
      if (!applying) {
        return;
      }

      // Close the open dialog only if the DELETE request succeeded
      this.backend.deleteEdge(this.currNamespace, edge.name).subscribe({
        next: _ => {
          this.poller.reset();
          ref.close(DIALOG_RESP.ACCEPT);
        },
        error: err => {
          // Simplify the error message
          const errorMsg = err;
          deleteDialogConfig.error = errorMsg;
          ref.componentInstance.applying$.next(false);
        },
      });
    });
  }

  // Utility funcs
  public parseIncomingData(edges: EdgeResponseObject[]): EdgeProcessedObject[] {
    const edgesCopy = JSON.parse(JSON.stringify(edges)) as EdgeProcessedObject[];

    for (const edge of edgesCopy) {
      edge.deleteAction = STATUS_TYPE.READY;
      edge.showAction = STATUS_TYPE.READY;
    }

    return edgesCopy;
  }
}

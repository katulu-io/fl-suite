import { Component, OnInit, OnDestroy } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  Validators,
  FormControl,
  ValidatorFn,
} from '@angular/forms';
import { Subscription } from 'rxjs';
import {
  NamespaceService,
  DialogConfig,
  ConfirmDialogService,
  getExistingNameValidator,
  dns1035Validator,
  getNameError,
  DIALOG_RESP,
} from 'kubeflow';
import { EdgeIdentityBackendService } from 'src/app/services/backend.service';
import { EdgePostObject, EdgePostResponseObject } from 'src/app/types';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-form-default',
  templateUrl: './form-default.component.html',
  styleUrls: ['./form-default.component.scss'],
})
export class FormDefaultComponent implements OnInit, OnDestroy {
  public TYPE_EMPTY = 'empty';

  public subs = new Subscription();
  public formCtrl: FormGroup;
  public blockSubmit = false;

  public currNamespace = '';
  public edgeNames = new Set<string>();

  constructor(
    public ns: NamespaceService,
    public fb: FormBuilder,
    public backend: EdgeIdentityBackendService,
    public dialog: MatDialogRef<FormDefaultComponent>,
    public confirmDialog: ConfirmDialogService,
  ) {
    this.formCtrl = this.fb.group({
      type: ['empty', [Validators.required]],
      name: ['', [Validators.required]],
      namespace: ['', [Validators.required]],
      size: [10, []],
      class: ['$empty', [Validators.required]],
      mode: ['ReadWriteOnce', [Validators.required]],
    });
  }

  ngOnInit() {
    this.formCtrl.controls.namespace.disable();

    this.subs.add(
      this.ns.getSelectedNamespace().subscribe(ns => {
        this.currNamespace = ns;
        this.formCtrl.controls.namespace.setValue(ns);

        this.backend.getEdges(ns).subscribe(edges => {
          this.edgeNames.clear();
          edges.forEach(edge => this.edgeNames.add(edge.name));
        });
      }),
    );
  }

  ngOnDestroy() {
    this.subs.unsubscribe();
  }

  public onSubmit() {
    const newEdge: EdgePostObject = JSON.parse(JSON.stringify(this.formCtrl.value));
    this.blockSubmit = true;

    this.backend.createEdge(this.currNamespace, newEdge).subscribe(
      (response: EdgePostResponseObject) => {
        this.dialog.close(response.edge);
      },
      error => {
        this.blockSubmit = false;
      },
    );
  }

  public onCancel() {
    this.dialog.close(DIALOG_RESP.CANCEL);
  }
}

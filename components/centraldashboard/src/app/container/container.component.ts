import { AfterViewInit, Component, ElementRef, HostListener, ViewChild } from "@angular/core";
import { ActivatedRoute } from "@angular/router";

// @TODO: Import from shared library instead.
const PARENT_CONNECTED_EVENT = "parent-connected";
const IFRAME_CONNECTED_EVENT = "iframe-connected";
const NAMESPACE_SELECTED_EVENT = "namespace-selected";

const sendConnectAckMessage = (window: Window, origin: string) => {
  window.postMessage(
    {
      type: PARENT_CONNECTED_EVENT,
      value: null,
    },
    origin
  );
};

const sendNamespaceMessage = (window: Window, origin: string, namespace: string) => {
  window.postMessage(
    {
      type: NAMESPACE_SELECTED_EVENT,
      value: namespace,
    },
    origin
  );
};

@Component({
  selector: "app-container",
  templateUrl: "./container.component.html",
  styleUrls: ["./container.component.scss"],
})
export class ContainerComponent implements AfterViewInit {
  constructor(public route: ActivatedRoute) {}

  @ViewChild("content") content!: ElementRef<HTMLIFrameElement>;

  private contentOrigin!: string;
  private contentWindow!: Window;

  ngAfterViewInit() {
    // Register content message handler
    if (this.content.nativeElement.contentWindow == null) {
      console.error("Unable to estabablish connection, container content window is undefined.");
      return;
    }

    this.contentWindow = this.content.nativeElement.contentWindow;
    this.route.data.subscribe((data) => {
      this.contentWindow?.location.replace(data["location"]);
    });
  }

  @HostListener("window:message", ["$event"])
  messageHandler({ data, origin }: MessageEvent) {
    switch (data.type) {
      case IFRAME_CONNECTED_EVENT:
        // Update origin
        this.contentOrigin = origin;
        sendConnectAckMessage(this.contentWindow, this.contentOrigin);
        sendNamespaceMessage(this.contentWindow, this.contentOrigin, "katulu-fl");
    }
  }
}

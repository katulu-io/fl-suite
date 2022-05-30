import { NgModule } from "@angular/core";
import { Router, RouterModule, Routes } from "@angular/router";
import { ConfigService } from "./config.service";
import { ContainerComponent } from "./container/container.component";

const ROUTES: Routes = [];
@NgModule({
  imports: [RouterModule.forRoot(ROUTES)],
  exports: [RouterModule],
})
export class AppRoutingModule {
  constructor(private router: Router, private configService: ConfigService) {
    const routes: Routes = [];

    this.configService.getApps().forEach(({ location, path, label }) => {
      routes.push({ path, component: ContainerComponent, data: { location, path, label } });
    });

    router.resetConfig(
      Array.prototype.concat(routes, { path: "", redirectTo: routes[0].path, pathMatch: "full" }, ROUTES)
    );
  }
}

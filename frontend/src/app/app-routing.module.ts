import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { TradersComponent } from './components/traders/traders.component';
import { TradesComponent } from './components/trades/trades.component';
import { FollowersComponent } from './components/followers/followers.component';

const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'traders', component: TradersComponent },
  { path: 'trades', component: TradesComponent },
  { path: 'followers', component: FollowersComponent },
  { path: '**', redirectTo: '/dashboard' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

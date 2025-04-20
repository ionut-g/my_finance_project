import { Routes } from '@angular/router';
import { MarketOverviewComponent } from './pages/market-overview/market-overview.component';

export const routes: Routes = [
    { path: '', redirectTo: "market-overview", pathMatch: 'full' },
    { path: 'market-overview', component: MarketOverviewComponent }
];

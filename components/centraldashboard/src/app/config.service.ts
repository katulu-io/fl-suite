import { Injectable } from '@angular/core';

const APPS = [
  { path: '_/jupyter', location: '/jupyter/', label: 'Notebook', icon: 'book' },
  { path: '_/models', location: '/models/', label: 'Models', icon: 'settings_ethernet' },
  {
    path: '_/edges',
    location: '/edges/',
    label: 'Edges',
    icon: 'developer_board',
  },
  {
    label: 'Experiments (KFP)',
    path: '_/pipeline/#/experiments',
    location: '/pipeline/#/experiments',
    icon: 'done_all',
  },
  {
    path: '_/pipeline/#/pipelines',
    location: '/pipeline/#/pipelines',
    label: 'Pipelines',
    icon: 'checklist',
  },
  {
    path: '_/pipeline/#/runs',
    location: '/pipeline/#/runs',
    label: 'Runs',
    icon: 'directions_run',
  },
  {
    path: '_/pipeline/#/recurringruns',
    location: '/pipeline/#/recurringruns',
    label: 'Recurring Runs',
    icon: 'schedule',
  },
  {
    path: '_/pipeline/#/artifacts',
    location: '/pipeline/#/artifacts',
    label: 'Artifacts',
    icon: 'bubble_chart',
  },
  {
    path: '_/pipeline/#/executions',
    location: '/pipeline/#/executions',
    label: 'Executions',
    icon: 'play_arrow',
  },
];

@Injectable({
  providedIn: 'root',
})
export class ConfigService {
  constructor() {}

  getApps() {
    return APPS;
  }
}

import {
  PropertyValue,
  StatusValue,
  ActionListValue,
  ActionIconValue,
  TRUNCATE_TEXT_SIZE,
  TableConfig,
} from 'kubeflow';

export const tableConfig: TableConfig = {
  title: $localize`Edges`,
  newButtonText: $localize`NEW EDGE`,
  columns: [
    {
      matHeaderCellDef: $localize`Status`,
      matColumnDef: 'status',
      value: new StatusValue(),
    },
    {
      matHeaderCellDef: $localize`Name`,
      matColumnDef: 'name',
      value: new PropertyValue({
        field: 'name',
        tooltipField: 'name',
        truncate: TRUNCATE_TEXT_SIZE.SMALL,
      }),
    },
    {
      matHeaderCellDef: $localize`Age`,
      matColumnDef: 'age',
      value: new PropertyValue({ field: 'age' }),
    },
  ],
};

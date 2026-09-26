# `the_angular` (Angular Frontend)

This section covers frontend Angular patterns, NGXS stores, IndexedDB synchronization, and visual components.

## 1. Service Generation
Every compiled database table receives a corresponding Angular Service under `src/app/shared/Service/Model/[Name].service.ts`.
Services hook to NGXS actions to dispatch states (`Add`, `Delete`, `Edit`, `Set`, `Upsert`) and save logs to Local IndexedDB via `IndexedDBService`.

```typescript
this.emailService.prefix("isuper").all();
```

---

## 2. Table Component (`<the-table-material>`)
Renders a filterable, paginated table list from an observable:

```html
<the-table-material 
    [isfilter]="true" 
    [table_mat$]="emailService.allState()" 
    [columnsToDisplay]="columnsToDisplay" 
    [isPaginate]="true"
    (selected)="onSelect($event)">
</the-table-material>
```

---

## 3. Dynamic Form Component (`<the-form-dynamic>`)
To construct a form, define layout schema arrays inside a `Form.ts` definition and pass it using `setformbase(FormSchema, [ValidationSchema, options])`.

### Form Layout Schema Example (`Form.ts`)
```typescript
import { predefined } from "the-angular/lib/class/predefined";

export const Form: Record<string, any>[] = [
  { key: 'email', label: 'Sender Email Address', controlType: 'textbox', row: 'col-span-2', class: 'w-full' },
  { key: 'encryption', label: 'Connection Security / Encryption', controlType: 'dropdown', row: 'col-span-2', class: 'w-full', options: [
      { key: 'ssl', value: 'SSL (Implicit)' },
      { key: 'tls', value: 'TLS / STARTTLS' }
    ]
  },
  predefined.enable()
];
```

### Component Controller Configuration (`add.component.ts`)
```typescript
import { Createsmtp_accountForm } from 'src/app/shared/Form/Validation/Smtp_account';
import { setformbase } from 'the-angular/lib/interface/form-base';
import { Form } from '../Form';

Form = setformbase(Form, [Createsmtp_accountForm, {}]);
```

### Form View template (`add.component.html`)
```html
<the-form-dynamic 
    [inputs]="Form" 
    [formClass]="'grid grid-cols-2 sm:grid-cols-4 gap-2'" 
    (formOutput)="run($event)" 
    [binding]="binding" />
```

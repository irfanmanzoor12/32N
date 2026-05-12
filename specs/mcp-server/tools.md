# MCP Server — Tool Specifications

## Design Approach

Intent-based tools. Each tool maps to a human work intent, not a CRUD operation.
Side effects (e.g. notifications on finish) are internal to the tool — agents never orchestrate them directly.

---

## Data Model: Task

```typescript
type Task = {
  id: string              // uuid v4, generated on create
  user_id: string         // owner — defaults to "default" when not provided
  title: string
  notes?: string
  priority: "low" | "medium" | "high"   // default: medium
  status: "active" | "complete" | "cancelled"
  due_date?: string       // ISO 8601 date: "2026-05-14" (no time component)
  created_at: string      // ISO 8601 UTC datetime: "2026-05-14T09:00:00Z"
  updated_at: string      // ISO 8601 UTC datetime
  completed_at?: string   // ISO 8601 UTC datetime — set by tasks_finish
  cancelled_at?: string   // ISO 8601 UTC datetime — set by tasks_cancel
  cancel_reason?: string  // set by tasks_cancel
  completion_note?: string // set by tasks_finish
}
```

All datetime fields are UTC. `due_date` is date-only (no time, no timezone).

Storage: in-memory `dict[str, Task]` — no database for now.

### User ID behaviour

All tools accept an optional `user_id`. When omitted, the server uses `"default"`.
Read tools (get, list, focus, search) only return tasks belonging to the resolved `user_id`.
Write tools (finish, cancel, defer, update) enforce ownership — a task belonging to one user cannot be mutated by another.

---

## Shared Input Field

Every tool accepts:

```typescript
user_id?: string   // default: "default"
```

Not repeated in each tool's input block below — assume it is always present.

---

## Tools

---

### `tasks_add`

Create a new task.

**Input**
```typescript
{
  user_id?: string        // default: "default"
  title: string           // required
  notes?: string
  due_date?: string       // ISO 8601 date
  priority?: "low" | "medium" | "high"  // default: "medium"
}
```

**Output**
```typescript
{ task: Task }
```

**Annotations**
```
readOnlyHint: false
destructiveHint: false
idempotentHint: false
openWorldHint: false
```

**Errors**
| Condition | Message |
|---|---|
| title is empty | "title is required and cannot be empty" |
| due_date is invalid | "due_date must be a valid ISO 8601 date (e.g. 2026-05-14)" |

---

### `tasks_finish`

Mark a task as complete. Internal side effect: emit completion event (wired to Notifications API when that service exists).

**Input**
```typescript
{
  user_id?: string        // default: "default"
  task_id: string         // required
  note?: string           // optional completion note
}
```

**Output**
```typescript
{ task: Task }            // task with status: "complete", completed_at set
```

**Annotations**
```
readOnlyHint: false
destructiveHint: false
idempotentHint: true      // finishing an already-complete task is a no-op
openWorldHint: false
```

**Errors**
| Condition | Message |
|---|---|
| task not found | "task {task_id} not found" |
| wrong owner | "task {task_id} not found" (same message — don't leak existence) |
| task already cancelled | "task {task_id} is cancelled and cannot be completed — use tasks_add to create a new task" |

---

### `tasks_cancel`

Remove a task from active work. Preserves history (status → cancelled, not deleted).

**Input**
```typescript
{
  user_id?: string        // default: "default"
  task_id: string         // required
  reason?: string
}
```

**Output**
```typescript
{ task: Task }            // task with status: "cancelled", cancelled_at set
```

**Annotations**
```
readOnlyHint: false
destructiveHint: true
idempotentHint: true      // cancelling already-cancelled task is a no-op
openWorldHint: false
```

**Errors**
| Condition | Message |
|---|---|
| task not found | "task {task_id} not found" |
| wrong owner | "task {task_id} not found" (same message — don't leak existence) |
| task already complete | "task {task_id} is already complete" |

---

### `tasks_defer`

Move a task's due date forward. Use when the user wants to reschedule, not cancel.

**Input**
```typescript
{
  user_id?: string        // default: "default"
  task_id: string         // required
  to_date: string         // required, ISO 8601 date
}
```

**Output**
```typescript
{ task: Task }            // task with updated due_date
```

**Annotations**
```
readOnlyHint: false
destructiveHint: false
idempotentHint: false
openWorldHint: false
```

**Errors**
| Condition | Message |
|---|---|
| task not found | "task {task_id} not found" |
| wrong owner | "task {task_id} not found" |
| task is terminal | "task {task_id} is {status} — only active tasks can be deferred" |
| to_date in the past | "to_date must be today or a future date" |
| to_date invalid | "to_date must be a valid ISO 8601 date (e.g. 2026-05-14)" |

---

### `tasks_update`

Edit task fields. Does not change status — use tasks_finish or tasks_cancel for that.

**Input**
```typescript
{
  user_id?: string        // default: "default"
  task_id: string         // required
  changes: {
    title?: string
    notes?: string
    priority?: "low" | "medium" | "high"
    due_date?: string | null   // null clears the due date
  }
}
```

**Output**
```typescript
{ task: Task }
```

**Annotations**
```
readOnlyHint: false
destructiveHint: false
idempotentHint: false
openWorldHint: false
```

**Errors**
| Condition | Message |
|---|---|
| task not found | "task {task_id} not found" |
| wrong owner | "task {task_id} not found" |
| task is terminal | "task {task_id} is {status} — only active tasks can be updated" |
| no changes provided | "at least one field must be provided in changes" |
| title set to empty | "title cannot be empty" |

---

### `tasks_get`

Retrieve a single task by ID.

**Input**
```typescript
{
  user_id?: string        // default: "default"
  task_id: string         // required
}
```

**Output**
```typescript
{ task: Task }
```

**Annotations**
```
readOnlyHint: true
destructiveHint: false
idempotentHint: true
openWorldHint: false
```

**Errors**
| Condition | Message |
|---|---|
| task not found or wrong owner | "task {task_id} not found" |

---

### `tasks_list`

List tasks with optional filters. Defaults to active tasks only.

**Input**
```typescript
{
  user_id?: string        // default: "default"
  status?: "active" | "complete" | "cancelled" | "all"  // default: "active"
  priority?: "low" | "medium" | "high"
  due_before?: string     // ISO 8601 date — returns tasks due on or before this date
  limit?: number          // default: 50, max: 200
  offset?: number         // default: 0
}
```

**Output**
```typescript
{
  tasks: Task[]
  total: number
  has_more: boolean
  next_offset?: number
}
```

**Annotations**
```
readOnlyHint: true
destructiveHint: false
idempotentHint: true
openWorldHint: false
```

**Errors**
| Condition | Message |
|---|---|
| due_before invalid | "due_before must be a valid ISO 8601 date (e.g. 2026-05-14)" |
| limit out of range | "limit must be between 1 and 200" |

---

### `tasks_focus`

Return the prioritized short list of what to work on — overdue tasks plus tasks due today, sorted by priority then due date. Designed for "what should I do now?" intent.

**Input**
```typescript
{
  user_id?: string        // default: "default"
  date?: string           // ISO 8601 date, default: today (server time)
}
```

**Output**
```typescript
{
  tasks: Task[]           // overdue + due on date, sorted: high → medium → low, then due_date asc
  date: string            // the date used for the query
  overdue_count: number
  due_today_count: number
}
```

**Annotations**
```
readOnlyHint: true
destructiveHint: false
idempotentHint: true
openWorldHint: false
```

**Errors**
| Condition | Message |
|---|---|
| date invalid | "date must be a valid ISO 8601 date (e.g. 2026-05-14)" |

---

### `tasks_search`

Full-text search across task title and notes. Searches active tasks by default.

**Input**
```typescript
{
  user_id?: string        // default: "default"
  query: string           // required, min 2 characters
  status?: "active" | "complete" | "cancelled" | "all"  // default: "active"
  limit?: number          // default: 20, max: 100
}
```

**Output**
```typescript
{
  tasks: Task[]
  total: number
  query: string           // echo back for agent context
}
```

**Annotations**
```
readOnlyHint: true
destructiveHint: false
idempotentHint: true
openWorldHint: false
```

**Errors**
| Condition | Message |
|---|---|
| query too short | "query must be at least 2 characters" |

---

## Tool Summary

| Tool | Intent | Mutates | Terminal |
|---|---|---|---|
| `tasks_add` | Create a task | yes | no |
| `tasks_finish` | Complete a task | yes | yes |
| `tasks_cancel` | Abandon a task | yes | yes |
| `tasks_defer` | Reschedule a task | yes | no |
| `tasks_update` | Edit task fields | yes | no |
| `tasks_get` | Look up one task | no | no |
| `tasks_list` | Browse tasks | no | no |
| `tasks_focus` | What to do now | no | no |
| `tasks_search` | Find by content | no | no |

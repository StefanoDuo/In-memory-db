# SQL-interpreter
A simple SQL interpreter written in Python, available as a REPL (read-eval-print loop) command line program.

## Instructions
Simply run `sql_interpreter/sql_repl.py` and start writing commands (requires Python3).

## Supported commands
* Create table: `create table TABLE_NAME (COLUMN_NAME COLUMN_TYPE [, ...])`.
* Drop table: `drop TABLE_NAME`.
* Insert entry into a table: `insert into TABLE_NAME values COLUMN1_VALUE [, ...]`.
* Query table: cross joins, rows filtering, columns projection and reordering, see the section below for the query syntax.
* Create table from query: `create table TABLE_NAME as TABLE_QUERY`.

At the moment the interprer is case sensitive, therefore `DROP, CREATE TABLE, ...` are not well formed commands.

### Query table syntax

```
select {*, COLUMN_NAMES_LIST}
from TABLE_NAME1 [, ...]
where COLUMN_EXPRESSION1 {<, <=, >, >=} COLUMN_EXPRESSION2
   [{and, or} ...]
```
A COLUMN_EXPRESSION is a mathematical expression composed of column names and operators (+, -, *, /).

### Supported types
Currently only int (any number without a decimal point), float (any number with a decimal point)
and string (anything contained between 2 ' characters) are supported.

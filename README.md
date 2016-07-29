Deployable SQL
==============

This module makes SQL versionable and deployable like other code.

## Usage

Running `deploy.py setup <usr> <db>` will create the folder structure you need.

* functions
* tables
* permissions
* stored_procedures

For each file in these folders, write your sql as a create statement. When
syncing, the deploy script will drop the existing object and create the new
one in its place, keeping code static and stable.

* views

For views, we made it even easier.  Just write a select statement, and the
script will convert it into a CREATE VIEW statement.

Once you are set up, run the grant_deployable.sql script manually to give your
deployable_sql service the rights to read write and control your tables.

Then, you can start syncing away with `deploy.py sync -all`

## Permissions

Either provide permissions to the sync command at runtime, or create environment
variables and use the `deploy.py auto` settings.  Environment variables should
be:

* DEPLOYABLE_USR
* DEPLOYABLE_PWD
* DEPLOYABLE_HOST
* DEPLOYABLE_DB

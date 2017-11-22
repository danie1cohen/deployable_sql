Deployable SQL
==============

The goal of this this module is to provide a clean command line interface for
working with SQL views, stored procedures and jobs in a way that is versionable,
and so providing a way to interface with typical continuous integration tools.

This project is fairly single-minded towards T-SQL at the moment.

## Usage

Running `deploy.py setup <usr> <db>` will create the folder structure you need.

* functions
* jobs
* permissions
* stored_procedures
* tables
* views

For each file in the tables, functions, and stored_procedure, write your sql as a
create statement. When syncing, the deploy script will drop the existing object
and create the new one in its place, keeping code static and stable.

* views

For views, we made it even easier.  Just write a select statement, and the
script will convert it into a CREATE VIEW statement.

* jobs

Jobs are a little bit more involved.  Instead of making you write the SQL that
adds jobs, adds steps to the job, and adds schedules, you can define an object
in yaml that is structured in such a way that the script will do the work. A
quick way to do this is to invoke `deploy.py create_job <jobname>`.

* permissions

Once you are set up, run the grant_deployable.sql script as a database admin
manually to give your deployable_sql service the rights to read write and
control your tables.  We suggest that you do not use the deployer service to
manage permissions automatically, but store the permissions as scripts and run
them manually as needed.

Then, you can start syncing away with `deploy.py --all`

## Permissions

Either provide credentials to the command at runtime, or create environment
variables, as described below, or create a `.deploy_sql.yml` file in your home
directory.  

Environment variables should be:

* DEPLOYABLE_USR
* DEPLOYABLE_PWD
* DEPLOYABLE_HOST
* DEPLOYABLE_DB

Or create a the yaml config like so:

    --- # .deploy_sql.yml

    usr: yourname
    pwd: yourpass
    host: yourhost
    db: yourdb

# Introduction


* Schemas define what data is allowed in the DB.
* Changes are incremental


A DB is constituted by:
- a current state
- a set of changes


# Schemas

This is the data model:

- structs (dictionaries with fixed fields)
- dictionaries
- strings
- bytes (!!binary)
- integers (TODO)
- floats (TODO)
- dates

These all map to YAML.


**Schemas** define what is valid data. There are validations

## Defining schemas


Structs:

Dictionaries:

String:

Bytes:

Integers: (TODO)

    TODO

Floats: (TODO)

    TODO

Dates

## Examples

This defines the db as a struct with an entry `users` which is a hash
of `User`:

    # First define the schema for the user
    schema_user = Schema()
    schema_user.string('name')
    schema_user.string('email', can_be_none=True)
    schema_user.list('groups', SchemaString())

    # Then define the schema for the db:
    db_schema = Schema()
    db_schema.hash('users', schema_user)

For example, this is a valid Python representation:

    users:
       andrea:
         email: null
         groups: ['group:admin', 'group:FDM']
         name: not Andrea
       pallo:
         email: null
         groups: ['group:FDM']
         name: Pinco Pallo

## Using views

## Encoding access control in schemas

    # define the schema
    schema_user = Schema()
    schema_user.string('name')
    schema_user.string('email', can_be_none=True)
    schema_user.list('groups', SchemaString())

    db_schema = Schema()
    db_schema.hash('users', schema_user)

    # give access control

    all_can_read = dict(
        what='allow',
        whom='system:authenticated',
        privilege='read')
    self_can_read = dict(


    )
    acl_users =
    - what: allow
       whom: system:authenticated
       what: read


    db_schema['users'].set_acl(yaml.load(acl_users))
    schema_user. add ...


struct events:

    value_set <name> <value>
        For simple values: int, string, date
    struct_set <name> <value>
    increment <name> <value>
    list_append <list> <data>
    list_delete <list> <index>
    dict_setitem <dict> <key> <value>
    dict_delitem <dict> <key>
    dict_rename <dict> <key> <key2>

file events:

    disk_dir_rename <dirname> <name>
    disk_file_create  <dirname> <filename> <contents>
    disk_file_modify  <dirname> <filename> <contents>
    disk_file_delete  <dirname> <filename>
    disk_dir_delete <dirname>
    disk_file_rename <dirname> <basename> <basename2>


## Functorial relations

Let `db0` be an initial dataset (in-memory plain data), `db1` the final data
and `events` the list of change events.

It holds that

    db1 = apply(e[-1], apply(e[-1], ... apply(e[0], data))

Now suppose we have φ: MemoryStructure -> DiskStructures
so that

    ds0 = φ(db0)
    ds1 = φ(db1)


Let:

    mem_apply: MemoryEvent x MemoryStructure -> MemoryStructure
    disk_apply: DiskEvent x DiskStructure -> DiskStructure

and

    mem_apply_s: MemoryEvents* x MemoryStructure -> MemoryStructure
    disk_apply_s: DiskEvent* x DiskStructure -> DiskStructure

now we want a translation function that takes a sequence of events

    β : MemoryEvent* -> DiskEvent*

Then we ask that the following holds:

    For all es \in MemoryEvent*:

        mem_apply_s(es, db0) = disk_apply( β(es), φ)

Furthermore we look at the single β0 that translates a single event

    β0: MemoryEvent -> DiskEvent+

So that

    β([e :: es]) = β0(e) + β(es)




Application interface  <--> Memory <--> Disk abstraction <-> Git repo

   User proxy:
       data = Abstracted with classes

       knows:
       - actor
       - permissions. (maybe)

   Application interface:
       data = Abstracted with classes

       db.users['andrea'].set_email(new_email)
       or
       db.users['andrea'].email = new_email

       db.users['andrea'].affiliation = 'affiliation:ethz' # error if it doesn't exist


   Memory:
       ## data
       Python struct that can be serialized with yaml

       It includes: dictionary, list, strings, numbers, datatypes

       It also has validation constraints.

       Some examples of validation constraints:
       - not null (default unless "default=None")
       - for string:
           - email
           - startswith:<prefix>
           - (validation) is an id in another structure
             valid:/users/
           (phone, address)

       ## diff

       A diff is a yaml-serializable structure:

           operation: append
           context: list of strings
           data: any yaml structure



   On disk structure: converts everything to disk.

       changes:
           add_file(filename, content)
           delete_file(filename)
           rename_file(filename)
           modify_file(new_content)

   Git: graphs and commits

       changes = commits


        There are some helper functions to create diffs:

           add(('users', 'andrea'))
           set(('users', 'andrea', 'email'), new_email)
           delete(('users', 'andrea'))
           rename(('users', 'andrea'), 'andrea2')
           context('users', 'andrea', 'subscriptions'))
           append((), ':newindex')
           context(':newindex')

           append(('users', 'andrea', 'subscription'), ':newindex')

           set(('users', 'andrea', 'subscriptions', ':newindex'))


           add('users', 'andrea'):
               set(

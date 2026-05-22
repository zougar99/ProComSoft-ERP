<<<<<<< HEAD
"""call using an open ADO connection --> list of table names"""

from . import adodbapi


def names(connection_object):
    ado = connection_object.adoConn
    schema = ado.OpenSchema(20)  # constant = adSchemaTables

    tables = []
    while not schema.EOF:
        name = adodbapi.getIndexedValue(schema.Fields, "TABLE_NAME").Value
        tables.append(name)
        schema.MoveNext()
    del schema
    return tables
=======
"""call using an open ADO connection --> list of table names"""

from . import adodbapi


def names(connection_object):
    ado = connection_object.adoConn
    schema = ado.OpenSchema(20)  # constant = adSchemaTables

    tables = []
    while not schema.EOF:
        name = adodbapi.getIndexedValue(schema.Fields, "TABLE_NAME").Value
        tables.append(name)
        schema.MoveNext()
    del schema
    return tables
>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457

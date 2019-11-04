.. _enumeration_description:

Interface definition language to python mapping for enumerated types
--------------------------------------------------------------------

The interface language definition type system includes enumerated types. Python
SDK supports both 2.x and 3.x versions of Python. Since Python 2.x does
not have first class support for enumerations, special classes are
generated to represent enumerated types from the interface definition
language. The special class contains class attributes which represent
the values of the enumerated type.

This documentation explains the following:

* How the class variables are defined in the module. This specifies the names that you can use in your program.
* How you instantiate a class to use it for communication with future versions of the service.

Example of an enumerated type documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*class* com.vmware.vapi.metadata_client. **SourceType** (string)
    Bases: vmware.vapi.bindings.enum.Enum

    Metadata source type

    .. note::
        This class represents an enumerated type in the interface language definition type system. The class contains class attributes which represent the values in the current version of the enumerated type. Newer versions of the enumerated type may contain new values. To use new values of the enumerated type in communication with a server that supports a newer version of the API, you instantiate this class. See :ref:`enumerated type description page <enumeration_description>`.

    **Parameters** : **string** (``str``) – String value for the SourceType instance.

    **FILE** = *SourceType(string='FILE')*
        If the source is backed by a file.

    **REMOTE** = *SourceType(string='REMOTE')*
        If the source is backed by a remote service.

Code Examples
^^^^^^^^^^^^^

The enumerated type classes are defined in python modules that your code
imports. You can use these in your code.

1. If you want to pass an enumerated type value in a method to a server, specify the class variable of the enumerated type class.

.. code-block:: python

    # SourceType is an enumerated type
    from com.vmware.vapi.metadata_client import SourceType

    # SourceType has two class attrites, SourceType.FILE and SourceType.REMOTE
    spec = Source.CreateSpec(type=SourceType.FILE, filepath='entity_metadata.json', description='Entity service')
    source_svc.create(id='entity', spec=spec)

2. When you receive an enumerated type value in the response from a server, allow for unknown enumerated type values.

.. code-block:: python

    # SourceType is an enumerated type
    from com.vmware.vapi.metadata_client import SourceType

    source_info = source_svc.get(id='entity')
    if (source_info.type == SourceType.FILE) {
        print 'Source is a file'
    } else if (source_info.type == SourceType.REMOTE) {
        print 'Source is a remote provider'
    } else {
        print 'Unknown source type: %s' % str(source_info.type)
    }

3. Sending a new enumerated type value to a server that has a newer version of the enumerated type.

To use new values of the enumerated type in communication with a server that supports a newer version of the API, you instantiate the
enumerated type class.

.. code-block:: python

    # If a newer version of SourceType has a new value FOLDER, FOLDER would be one
    # of the class attributes for SourceType. In the older version, SourceType has
    # only two class attributes, FILE and REMOTE
    from com.vmware.vapi.metadata_client import SourceType
    spec = Source.CreateSpec(type=SourceType('FOLDER'), filepath='entity_metadata', description='Entity service')
    source_svc.create(id='entity', spec=spec)
